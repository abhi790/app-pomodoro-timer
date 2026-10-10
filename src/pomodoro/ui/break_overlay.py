"""The Force Break screen: a full-screen window on every monitor.

``BreakOverlay`` is one such window. ``BreakOverlayManager`` opens one per
monitor, keeps them on top, updates the countdown and rotates the tips.

There are no system tricks here. The windows simply ignore Close, Alt+F4 and
Esc, and come back to the front if you click away. In this step the only way
to leave early is to wait; the math unlock comes in the next step.
"""

from typing import Optional

from PySide6.QtCore import QObject, Qt, QTimer
from PySide6.QtGui import QCloseEvent, QGuiApplication, QKeyEvent
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from pomodoro.formatting import format_clock
from pomodoro.tips import TIP_SECONDS, TipRotator

KEEP_ON_TOP_MS = 500


class BreakOverlay(QWidget):
    """One full-screen break window (one per monitor)."""

    def __init__(self) -> None:
        super().__init__()
        self._allow_close = False
        self.setWindowTitle("Break time")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        title = QLabel("Break time", alignment=Qt.AlignCenter)
        title.setObjectName("overlayTitle")

        self._clock_label = QLabel(alignment=Qt.AlignCenter)
        self._clock_label.setObjectName("overlayClock")

        self._tip_label = QLabel(alignment=Qt.AlignCenter)
        self._tip_label.setObjectName("overlayTip")
        self._tip_label.setWordWrap(True)
        self._tip_label.setMinimumHeight(140)

        hint = QLabel(
            "Step away from the screen. It comes back when the break ends.",
            alignment=Qt.AlignCenter,
        )
        hint.setObjectName("overlayHint")
        hint.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(80, 40, 80, 40)
        layout.setSpacing(16)
        layout.addStretch(2)
        layout.addWidget(title)
        layout.addWidget(self._clock_label)
        layout.addWidget(self._tip_label)
        layout.addStretch(3)
        layout.addWidget(hint)

    def set_clock(self, text: str) -> None:
        self._clock_label.setText(text)

    def set_tip(self, text: str) -> None:
        self._tip_label.setText(text)

    def close_for_real(self) -> None:
        """Close the window. Only the manager calls this."""
        self._allow_close = True
        self.close()

    # ----- things the user must not be able to do -------------------------

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._allow_close:
            event.accept()
        else:
            event.ignore()  # Alt+F4 and similar end up here

    def keyPressEvent(self, event: QKeyEvent) -> None:
        event.accept()  # swallow every key, including Esc


class BreakOverlayManager(QObject):
    """Shows the break window on all monitors and keeps it up to date."""

    def __init__(
        self,
        parent: Optional[QObject] = None,
        rotator: Optional[TipRotator] = None,
    ) -> None:
        super().__init__(parent)
        self._rotator = rotator or TipRotator()
        self._overlays: list = []
        self._clock_text = ""
        self._tip_text = ""
        self._test_remaining = 0

        self._keep_on_top = QTimer(self)
        self._keep_on_top.setInterval(KEEP_ON_TOP_MS)
        self._keep_on_top.timeout.connect(self._bring_to_front)

        self._tip_timer = QTimer(self)
        self._tip_timer.setInterval(TIP_SECONDS * 1000)
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

    def show(self, clock_text: str) -> None:
        """Open the break windows (does nothing new if already open)."""
        self._clock_text = clock_text
        if self.is_active:
            self.update_clock(clock_text)
            return
        self._tip_text = self._rotator.next_tip()
        self._open_overlays()
        self._keep_on_top.start()
        self._tip_timer.start()

    def update_clock(self, clock_text: str) -> None:
        self._clock_text = clock_text
        for overlay in self._overlays:
            overlay.set_clock(clock_text)

    def hide(self) -> None:
        """Close all break windows."""
        self._keep_on_top.stop()
        self._tip_timer.stop()
        self._test_timer.stop()
        self._close_overlays()

    def show_test(self, seconds: int) -> None:
        """Try the break screen for a few seconds (for testing only)."""
        if self.is_active:
            return
        self._test_remaining = seconds
        self.show(format_clock(seconds))
        self._test_timer.start()

    # ----- internals -------------------------------------------------------

    def _open_overlays(self) -> None:
        for screen in QGuiApplication.screens():
            overlay = BreakOverlay()
            overlay.set_clock(self._clock_text)
            overlay.set_tip(self._tip_text)
            overlay.setScreen(screen)
            overlay.setGeometry(screen.geometry())
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
        self._tip_text = self._rotator.next_tip()
        for overlay in self._overlays:
            overlay.set_tip(self._tip_text)

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
