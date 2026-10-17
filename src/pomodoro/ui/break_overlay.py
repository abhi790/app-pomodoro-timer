"""The Force Break screen: one full-screen window.

``BreakOverlay`` is one such window (the manager in ``break_manager.py`` opens
one per monitor). It shows the break countdown, a healthy tip, a matching
background picture and, at the bottom, the controls to leave the break early
(``UnlockPanel``).

Each tip has a category (water, food, move, ...). The window shows a matching
background picture from ``assets/backgrounds/<category>/``. If there is no
picture, it shows a soft colored gradient instead.

There are no system tricks here. The window simply ignores Close, Alt+F4 and
Esc. The manager brings it back to the front if you click away.
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import (
    QEasingCurve,
    QPropertyAnimation,
    QRect,
    QRectF,
    QSize,
    Qt,
    QVariantAnimation,
    Signal,
)
from PySide6.QtGui import (
    QBrush,
    QCloseEvent,
    QColor,
    QKeyEvent,
    QLinearGradient,
    QPainter,
    QPaintEvent,
    QPixmap,
)
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from pomodoro.ideas import IDEA_CATEGORY, IDEA_TITLE
from pomodoro.tips import CATEGORY_TITLE, Tip
from pomodoro.ui.emergency_exit import make_emergency_button, place_in_corner
from pomodoro.ui.theme import SCREEN_STYLE
from pomodoro.ui.unlock_panel import UnlockPanel

FADE_MS = 1200

# Colors used when a category has no picture (top-left, bottom-right).
DEFAULT_GRADIENT = ("#1b1b2a", "#34344a")
CATEGORY_GRADIENT = {
    "water": ("#0b3d6b", "#0f8fb0"),
    "food": ("#1e4d2b", "#9a6a1f"),
    "move": ("#6b2a1a", "#d0702a"),
    "eyes": ("#14304f", "#2f7a8c"),
    "posture": ("#2d2a52", "#4c63b8"),
    "sleep": ("#0d1030", "#3a2a7a"),
    "mind": ("#1f3d3a", "#4f8a78"),
    IDEA_CATEGORY: ("#4a1d5c", "#c2477f"),
}

# The small title above the text: the tip categories, plus the creative ideas
# that long breaks show.
TITLES = {**CATEGORY_TITLE, IDEA_CATEGORY: IDEA_TITLE}

# A dark layer over the picture so the white text is easy to read.
SCRIM = QColor(0, 0, 0, 150)

# The tip is kept in a narrow column in the middle, so it stays on the dark,
# calm part of the picture and is easier to read.
TIP_MAX_WIDTH = 900


class Scene:
    """One background: a gradient, plus a picture if there is one."""

    def __init__(self, category: str, image: Optional[QPixmap] = None) -> None:
        self.category = category
        self._image = image if image is not None and not image.isNull() else None
        self._scaled: Optional[QPixmap] = None
        self._scaled_for: Optional[QSize] = None

    def paint(self, painter: QPainter, rect: QRectF) -> None:
        top, bottom = CATEGORY_GRADIENT.get(self.category, DEFAULT_GRADIENT)
        gradient = QLinearGradient(rect.topLeft(), rect.bottomRight())
        gradient.setColorAt(0.0, QColor(top))
        gradient.setColorAt(1.0, QColor(bottom))
        painter.fillRect(rect, QBrush(gradient))

        picture = self._picture_for(rect.size().toSize())
        if picture is not None:
            x = rect.x() + (rect.width() - picture.width()) / 2
            y = rect.y() + (rect.height() - picture.height()) / 2
            painter.drawPixmap(int(x), int(y), picture)

        painter.fillRect(rect, SCRIM)

    def _picture_for(self, size: QSize) -> Optional[QPixmap]:
        """The picture scaled to cover the whole window (centered, cropped)."""
        if self._image is None or size.isEmpty():
            return None
        if self._scaled is None or self._scaled_for != size:
            self._scaled = self._image.scaled(
                size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            self._scaled_for = size
        return self._scaled


class BreakOverlay(QWidget):
    """One full-screen break window (one per monitor)."""

    # Passed on from the unlock panel, so the manager only listens to the window.
    math_solved = Signal()
    emergency_exit = Signal()  # testing only, see emergency_exit.py

    def __init__(self) -> None:
        super().__init__()
        self._allow_close = False
        self._scene = Scene("")
        self._previous: Optional[Scene] = None
        self._blend = 1.0
        self._slide_anim: Optional[QPropertyAnimation] = None

        self.setWindowTitle("Break time")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # Always dark, even in Day mode: white text over a picture.
        self.setStyleSheet(SCREEN_STYLE)

        title = QLabel("Break time", alignment=Qt.AlignCenter)
        title.setObjectName("overlayTitle")

        self._clock_label = QLabel(alignment=Qt.AlignCenter)
        self._clock_label.setObjectName("overlayClock")

        self._category_label = QLabel(alignment=Qt.AlignCenter)
        self._category_label.setObjectName("overlayCategory")

        self._tip_label = QLabel(alignment=Qt.AlignCenter)
        self._tip_label.setObjectName("overlayTip")
        self._tip_label.setWordWrap(True)
        self._tip_label.setMaximumWidth(TIP_MAX_WIDTH)
        self._tip_label.setMinimumHeight(180)

        self._panel = UnlockPanel()
        self._panel.math_solved.connect(self.math_solved)

        hint = QLabel(
            "Step away from the screen. It comes back when the break ends.",
            alignment=Qt.AlignCenter,
        )
        hint.setObjectName("overlayHint")
        hint.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(80, 30, 80, 30)
        layout.setSpacing(14)
        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(self._clock_label)
        layout.addWidget(self._category_label)
        layout.addWidget(self._tip_label, alignment=Qt.AlignHCenter)
        layout.addStretch(1)
        layout.addWidget(self._panel, alignment=Qt.AlignHCenter)
        layout.addStretch(1)
        layout.addWidget(hint)

        # Testing only: leave at once, no math (None when the flag is off). It
        # floats in the corner, so it does not change the layout.
        self._emergency_button = make_emergency_button(self)
        if self._emergency_button is not None:
            self._emergency_button.clicked.connect(self.emergency_exit)
            place_in_corner(self._emergency_button, self)

        # Soft changes when a new tip arrives: the picture cross-fades and
        # the text fades in.
        self._text_effects = []
        for label in (self._category_label, self._tip_label):
            effect = QGraphicsOpacityEffect(label)
            label.setGraphicsEffect(effect)
            self._text_effects.append(effect)

        self._fade = QVariantAnimation(self)
        self._fade.setDuration(FADE_MS)
        self._fade.setStartValue(0.0)
        self._fade.setEndValue(1.0)
        self._fade.valueChanged.connect(self._on_fade)
        self._fade.finished.connect(self._on_fade_finished)

    # ----- what the manager calls -----------------------------------------

    def set_clock(self, text: str) -> None:
        self._clock_label.setText(text)

    def set_unlock_state(self, math_used: int) -> None:
        self._panel.set_state(math_used)

    def set_tip(
        self,
        tip: Tip,
        image_path: Optional[Path] = None,
        animate: bool = True,
    ) -> None:
        self._category_label.setText(TITLES.get(tip.category, "").upper())
        self._tip_label.setText(tip.text)

        image = QPixmap(str(image_path)) if image_path else None
        new_scene = Scene(tip.category, image)
        self._fade.stop()
        if animate:
            self._previous = self._scene
            self._scene = new_scene
            self._blend = 0.0
            self._set_text_opacity(0.0)
            self._fade.start()
        else:
            self._previous = None
            self._scene = new_scene
            self._blend = 1.0
            self._set_text_opacity(1.0)
        self.update()

    def close_for_real(self) -> None:
        """Close the window. Only the manager calls this."""
        self._allow_close = True
        self._fade.stop()
        if self._slide_anim is not None:
            self._slide_anim.stop()
        self.close()

    # ----- sliding up from the bottom (the 10-second warning) --------------

    def slide_in(self, final_rect: QRect, duration_ms: int) -> None:
        """Animate from the window's current geometry (set by the caller,
        just below the screen) up to ``final_rect``, so the break screen
        eases into view instead of appearing all at once."""
        self._slide_anim = QPropertyAnimation(self, b"geometry", self)
        self._slide_anim.setDuration(max(duration_ms, 1))
        self._slide_anim.setStartValue(self.geometry())
        self._slide_anim.setEndValue(final_rect)
        self._slide_anim.setEasingCurve(QEasingCurve.OutCubic)
        self._slide_anim.start()

    def finish_slide(self, final_rect: QRect) -> None:
        """Stop the slide-in animation, if any, and snap straight to the
        final, fully-covering position. Safe to call even if there is no
        animation running (the normal, instant break-screen path)."""
        if self._slide_anim is not None:
            self._slide_anim.stop()
            self._slide_anim = None
        self.setGeometry(final_rect)

    # ----- drawing ---------------------------------------------------------

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        rect = QRectF(self.rect())
        if self._previous is not None and self._blend < 1.0:
            self._previous.paint(painter, rect)
            painter.setOpacity(self._blend)
        self._scene.paint(painter, rect)
        painter.end()

    def _on_fade(self, value) -> None:
        self._blend = float(value)
        self._set_text_opacity(self._blend)
        self.update()

    def _on_fade_finished(self) -> None:
        self._previous = None
        self._blend = 1.0
        self.update()

    def _set_text_opacity(self, value: float) -> None:
        for effect in self._text_effects:
            effect.setOpacity(value)

    # ----- things the user must not be able to do -------------------------

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        place_in_corner(self._emergency_button, self)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._allow_close:
            event.accept()
        else:
            event.ignore()  # Alt+F4 and similar end up here

    def keyPressEvent(self, event: QKeyEvent) -> None:
        event.accept()  # swallow keys nobody else wanted, including Esc
