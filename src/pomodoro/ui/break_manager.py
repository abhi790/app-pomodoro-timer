"""Opens the Force Break screen on every monitor and keeps it going.

``BreakOverlayManager`` opens one ``BreakOverlay`` per monitor, keeps them on
top, updates the countdown and rotates the tips (each tip with its picture).

It also passes on what the user chose on the unlock panel:

* ``math_unlocked``: a math problem was solved, the break should end now

The manager does not count anything and does not touch the timer. The main
window listens to this signal and decides what happens.

``begin_slide_in`` is the 10-second warning: the break screen starts easing
up from the bottom of each monitor before the focus block has actually
ended, timed to finish covering the screen exactly as it does. ``show`` (the
real break start) then just finalizes that slide instead of opening the
windows again, if it is already running.
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QRect, QTimer, Signal
from PySide6.QtGui import QGuiApplication

from pomodoro.backgrounds import BackgroundPicker
from pomodoro.ideas import IDEA_CATEGORY, IdeaRotator
from pomodoro.tips import Tip, TipRotator, tip_display_seconds
from pomodoro.ui.break_overlay import BreakOverlay

KEEP_ON_TOP_MS = 500


class BreakOverlayManager(QObject):
    """Shows the break window on all monitors and keeps it up to date."""

    math_unlocked = Signal()
    emergency_exit = Signal()  # testing only, see emergency_exit.py

    def __init__(
        self,
        parent: Optional[QObject] = None,
        rotator: Optional[TipRotator] = None,
        picker: Optional[BackgroundPicker] = None,
        idea_rotator: Optional[IdeaRotator] = None,
    ) -> None:
        super().__init__(parent)
        self._rotator = rotator or TipRotator()
        self._picker = picker or BackgroundPicker()
        self._ideas = idea_rotator or IdeaRotator()
        self._long_break = False
        self._idea_turn = False
        self._overlays: list = []
        self._clock_text = ""
        self._tip: Optional[Tip] = None
        self._image: Optional[Path] = None
        self._math_used = 0
        self._sliding = False

        self._keep_on_top = QTimer(self)
        self._keep_on_top.setInterval(KEEP_ON_TOP_MS)
        self._keep_on_top.timeout.connect(self._bring_to_front)

        # One tip at a time. A longer tip stays longer (10 to 20 seconds).
        self._tip_timer = QTimer(self)
        self._tip_timer.setSingleShot(True)
        self._tip_timer.timeout.connect(self._show_next_tip)

        app = QGuiApplication.instance()
        app.screenAdded.connect(self._on_screens_changed)
        app.screenRemoved.connect(self._on_screens_changed)

    @property
    def is_active(self) -> bool:
        return bool(self._overlays)

    # ----- what the main window calls --------------------------------------

    def set_custom_ideas(self, ideas) -> None:
        """Use these ideas of your own (plus the built-in ones) in long breaks."""
        self._ideas = IdeaRotator(custom=ideas)

    def show(self, clock_text: str, math_used: int, long_break: bool = False) -> None:
        """Open the break windows (does nothing new if already open).

        ``math_used`` is how many math problems have been solved today
        already (sets how hard the next one is; leaving early always works).
        In a long break, a creative idea and a healthy tip take turns
        (starting with the idea).
        """
        self._clock_text = clock_text
        if self.is_active:
            self._finish_slide()
            self._math_used = math_used
            for overlay in self._overlays:
                overlay.set_unlock_state(math_used)
            self.update_clock(clock_text)
            return
        self._math_used = math_used
        self._long_break = long_break
        self._idea_turn = long_break
        self._choose_tip()
        self._open_overlays()
        self._keep_on_top.start()
        self._schedule_next_tip()

    def begin_slide_in(self, math_used: int, seconds: int, long_break: bool = False) -> None:
        """The 10-second warning: start the break screen sliding up from the
        bottom of each monitor, timed to finish covering the screen in
        ``seconds`` real seconds. Does nothing if the break screens are
        already open (sliding or not).

        ``long_break`` is a *prediction* (the focus block has not actually
        finished yet, so the real long-break decision is not made until it
        does) — it only decides whether the long break's creative idea shows
        first; ``show()`` corrects the clock and math count once the focus
        block really ends.
        """
        if self.is_active:
            return
        self._math_used = math_used
        self._long_break = long_break
        self._idea_turn = long_break
        self._choose_tip()
        self._sliding = True
        for screen in QGuiApplication.screens():
            rect = screen.geometry()
            below = QRect(rect.x(), rect.y() + rect.height(), rect.width(), rect.height())
            overlay = BreakOverlay()
            overlay.setScreen(screen)
            overlay.setGeometry(below)
            overlay.set_clock(self._clock_text)
            overlay.set_tip(self._tip, self._image, animate=False)
            overlay.set_unlock_state(self._math_used)
            overlay.math_solved.connect(self.math_unlocked)
            overlay.emergency_exit.connect(self.emergency_exit)
            overlay.show()
            overlay.slide_in(rect, seconds * 1000)
            self._overlays.append(overlay)
        if self._overlays:
            self._overlays[0].activateWindow()
        self._keep_on_top.start()
        self._schedule_next_tip()

    def cancel_slide_in(self) -> None:
        """Stop a slide-in in progress and close the (not yet real) break
        screens — used when the focus block is paused during the warning."""
        if self._sliding:
            self.hide()

    def update_clock(self, clock_text: str) -> None:
        self._clock_text = clock_text
        for overlay in self._overlays:
            overlay.set_clock(clock_text)

    def hide(self) -> None:
        """Close all break windows."""
        self._keep_on_top.stop()
        self._tip_timer.stop()
        self._close_overlays()
        self._sliding = False

    # ----- internals -------------------------------------------------------

    def _finish_slide(self) -> None:
        """Stop any slide-in animation and snap every overlay straight to
        fully covering its screen (safe to call even when not sliding)."""
        for overlay in self._overlays:
            screen = overlay.screen()
            if screen is not None:
                overlay.finish_slide(screen.geometry())
        self._sliding = False

    def _choose_tip(self) -> None:
        if self._long_break and self._idea_turn:
            self._tip = Tip(IDEA_CATEGORY, self._ideas.next_idea())
        else:
            self._tip = self._rotator.next_tip()
        if self._long_break:
            self._idea_turn = not self._idea_turn
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
            overlay.set_unlock_state(self._math_used)
            overlay.math_solved.connect(self.math_unlocked)
            overlay.emergency_exit.connect(self.emergency_exit)
            overlay.showFullScreen()
            self._overlays.append(overlay)
        if self._overlays:
            self._overlays[0].activateWindow()

    def _close_overlays(self) -> None:
        overlays, self._overlays = self._overlays, []
        for overlay in overlays:
            overlay.close_for_real()
            overlay.deleteLater()

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
