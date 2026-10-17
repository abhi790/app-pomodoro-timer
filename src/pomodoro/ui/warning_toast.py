"""A small toast that warns a break is coming, one minute out.

One ``WarningToast`` per monitor. It slides up from below the screen near the
bottom, like a taskbar notification, holds there for a couple of seconds,
then slides back down and closes itself. There is nothing to click and
nothing to configure: it shows, waits, and goes.

``WarningToastManager`` is what the main window talks to; it opens one toast
on every monitor each time it is asked to.
"""

from typing import List, Optional

from PySide6.QtCore import QEasingCurve, QObject, QPropertyAnimation, QRect, Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

TOAST_WIDTH = 360
TOAST_HEIGHT = 64
BOTTOM_MARGIN = 28

# How long each slide takes, and how long the toast rests in view between
# the two slides.
SLIDE_MS = 350
HOLD_MS = 2000

TOAST_STYLE = (
    "QWidget#warningToast { background-color: rgba(28, 28, 38, 235);"
    " border-radius: 10px; }"
    "QLabel#warningToastLabel { color: #ffffff; font-size: 15px; font-weight: 600; }"
)


class WarningToast(QWidget):
    """One toast window, for one monitor. Closes itself when done."""

    def __init__(self, text: str) -> None:
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setObjectName("warningToast")
        self.setStyleSheet(TOAST_STYLE)
        self.setFixedSize(TOAST_WIDTH, TOAST_HEIGHT)

        label = QLabel(text, alignment=Qt.AlignCenter)
        label.setObjectName("warningToastLabel")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.addWidget(label)

        self._up: Optional[QPropertyAnimation] = None
        self._down: Optional[QPropertyAnimation] = None

    def slide_up_then_away(self, screen_rect: QRect) -> None:
        """Slide into view near the bottom of ``screen_rect``, hold, slide
        back down, then close and delete itself."""
        x = screen_rect.x() + (screen_rect.width() - TOAST_WIDTH) // 2
        resting_y = screen_rect.y() + screen_rect.height() - TOAST_HEIGHT - BOTTOM_MARGIN
        below_y = screen_rect.y() + screen_rect.height()
        below = QRect(x, below_y, TOAST_WIDTH, TOAST_HEIGHT)
        resting = QRect(x, resting_y, TOAST_WIDTH, TOAST_HEIGHT)

        self.setGeometry(below)
        self.show()

        self._up = QPropertyAnimation(self, b"geometry", self)
        self._up.setDuration(SLIDE_MS)
        self._up.setStartValue(below)
        self._up.setEndValue(resting)
        self._up.setEasingCurve(QEasingCurve.OutCubic)

        self._down = QPropertyAnimation(self, b"geometry", self)
        self._down.setDuration(SLIDE_MS)
        self._down.setStartValue(resting)
        self._down.setEndValue(below)
        self._down.setEasingCurve(QEasingCurve.InCubic)
        self._down.finished.connect(self.close)
        self._down.finished.connect(self.deleteLater)

        self._up.start()
        QTimer.singleShot(SLIDE_MS + HOLD_MS, self._down.start)


class WarningToastManager(QObject):
    """Shows one toast per monitor. The main window owns one of these."""

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._toasts: List[WarningToast] = []

    def show_message(self, text: str) -> None:
        """Open a self-closing toast with ``text`` on every monitor."""
        self._toasts = [toast for toast in self._toasts if toast.isVisible()]
        for screen in QGuiApplication.screens():
            toast = WarningToast(text)
            toast.slide_up_then_away(screen.geometry())
            self._toasts.append(toast)
