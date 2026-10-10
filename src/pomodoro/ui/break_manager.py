"""Opens the Force Break screen on every monitor and keeps it going.

``BreakOverlayManager`` opens one ``BreakOverlay`` per monitor, keeps them on
top, updates the countdown and rotates the tips (each tip with its picture).

It also passes on what the user chose on the unlock panel:

* ``math_unlocked``: a math problem was solved, the break should end now
* ``important_chosen``: the Important button was pressed

The manager does not count anything and does not touch the timer. The main
window listens to these two signals and decides what happens.
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtGui import QGuiApplication

from pomodoro.backgrounds import BackgroundPicker
from pomodoro.formatting import format_clock
from pomodoro.tips import Tip, TipRotator, tip_display_seconds
from pomodoro.ui.break_overlay import BreakOverlay

KEEP_ON_TOP_MS = 500


class BreakOverlayManager(QObject):
    """Shows the break window on all monitors and keeps it up to date."""

    math_unlocked = Signal()
    important_chosen = Signal()

    def __init__(
        self,
        parent: Optional[QObject] = None,
        rotator: Optional[TipRotator] = None,
        picker: Optional[BackgroundPicker] = None,
    ) -> None:
        super().__init__(parent)
        self._rotator = rotator or TipRotator()
        self._picker = picker or BackgroundPicker()
        self._overlays: list = []
        self._clock_text = ""
        self._tip: Optional[Tip] = None
        self._image: Optional[Path] = None
        self._math_left = 0
        self._important_used = False
        self._is_test = False
        self._test_remaining = 0

        self._keep_on_top = QTimer(self)
        self._keep_on_top.setInterval(KEEP_ON_TOP_MS)
        self._keep_on_top.timeout.connect(self._bring_to_front)

        # One tip at a time. A longer tip stays longer (10 to 20 seconds).
        self._tip_timer = QTimer(self)
        self._tip_timer.setSingleShot(True)
        self._tip_timer.timeout.connect(self._show_next_tip)

        self._test_timer = QTimer(self)
        self._test_timer.setInterval(1000)
        self._test_timer.timeout.connect(self._on_test_tick)

        app = QGuiApplication.instance()
        app.screenAdded.connect(self._on_screens_changed)
        app.screenRemoved.connect(self._on_screens_changed)

    @property
    def is_active(self) -> bool:
        return bool(self._overlays)

    # ----- what the main window calls --------------------------------------

    def show(self, clock_text: str, math_left: int) -> None:
        """Open the break windows (does nothing new if already open).

        ``math_left`` is how many math unlocks remain today. With none left,
        the windows offer the Important button instead.
        """
        self._clock_text = clock_text
        if self.is_active:
            self.update_clock(clock_text)
            return
        self._math_left = math_left
        self._important_used = False
        self._choose_tip()
        self._open_overlays()
        self._keep_on_top.start()
        self._schedule_next_tip()

    def update_clock(self, clock_text: str) -> None:
        self._clock_text = clock_text
        for overlay in self._overlays:
            overlay.set_clock(clock_text)

    def mark_important_used(self) -> None:
        """The break was shortened: hide the Important button."""
        self._important_used = True
        self._apply_unlock_state()

    def hide(self) -> None:
        """Close all break windows."""
        self._keep_on_top.stop()
        self._tip_timer.stop()
        self._test_timer.stop()
        self._is_test = False
        self._close_overlays()

    def show_test(self, seconds: int, math_left: int) -> None:
        """Try the break screen for a while (for testing only).

        Nothing is counted and the timer is not touched: solving a problem
        just closes the test screen, and Important only hides its button.
        """
        if self.is_active:
            return
        self._is_test = True
        self._test_remaining = seconds
        self.show(format_clock(seconds), math_left)
        self._test_timer.start()

    # ----- internals -------------------------------------------------------

    def _choose_tip(self) -> None:
        self._tip = self._rotator.next_tip()
        self._image = self._picker.pick(self._tip.category)

    def _schedule_next_tip(self) -> None:
        seconds = tip_display_seconds(self._tip.text)
        self._tip_timer.start(seconds * 1000)

    def _open_overlays(self) -> None:
        for screen in QGuiApplication.screens():
            overlay = BreakOverlay()
            overlay.setScreen(screen)
            overlay.setGeometry(screen.geometry())
            overlay.set_clock(self._clock_text)
            overlay.set_tip(self._tip, self._image, animate=False)
            overlay.set_unlock_state(self._math_left, self._important_used)
            overlay.math_solved.connect(self._on_math_solved)
            overlay.important_chosen.connect(self._on_important)
            overlay.showFullScreen()
            self._overlays.append(overlay)
        if self._overlays:
            self._overlays[0].activateWindow()

    def _close_overlays(self) -> None:
        overlays, self._overlays = self._overlays, []
        for overlay in overlays:
            overlay.close_for_real()
            overlay.deleteLater()

    def _apply_unlock_state(self) -> None:
        for overlay in self._overlays:
            overlay.set_unlock_state(self._math_left, self._important_used)

    def _on_math_solved(self) -> None:
        if self._is_test:
            self.hide()
        else:
            self.math_unlocked.emit()

    def _on_important(self) -> None:
        if self._is_test:
            self.mark_important_used()
        else:
            self.important_chosen.emit()

    def _on_screens_changed(self, *_args) -> None:
        """A monitor was plugged in or removed while the break is on."""
        if self.is_active:
            self._close_overlays()
            self._open_overlays()

    def _show_next_tip(self) -> None:
        self._choose_tip()
        for overlay in self._overlays:
            overlay.set_tip(self._tip, self._image, animate=True)
        self._schedule_next_tip()

    def _bring_to_front(self) -> None:
        """If the user clicked away, bring the break windows back."""
        for overlay in self._overlays:
            if not overlay.isVisible() or overlay.isMinimized():
                overlay.showFullScreen()
            overlay.raise_()
        if self._overlays and not any(o.isActiveWindow() for o in self._overlays):
            self._overlays[0].activateWindow()

    def _on_test_tick(self) -> None:
        self._test_remaining -= 1
        if self._test_remaining <= 0:
            self.hide()
        else:
            self.update_clock(format_clock(self._test_remaining))
