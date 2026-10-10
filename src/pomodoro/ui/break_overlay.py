"""The Force Break screen: a full-screen window on every monitor.

``BreakOverlay`` is one such window. ``BreakOverlayManager`` opens one per
monitor, keeps them on top, updates the countdown and rotates the tips.

Each tip has a category (water, food, move, ...). The window shows a matching
background picture from ``assets/backgrounds/<category>/``. If there is no
picture, it shows a soft colored gradient instead.

There are no system tricks here. The windows simply ignore Close, Alt+F4 and
Esc, and come back to the front if you click away. In this step the only way
to leave early is to wait; the math unlock comes in the next step.
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QRectF, QSize, Qt, QTimer, QVariantAnimation
from PySide6.QtGui import (
    QBrush,
    QCloseEvent,
    QColor,
    QGuiApplication,
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

from pomodoro.backgrounds import BackgroundPicker
from pomodoro.formatting import format_clock
from pomodoro.tips import CATEGORY_TITLE, Tip, TipRotator, tip_display_seconds

KEEP_ON_TOP_MS = 500
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
}

# A dark layer over the picture so the white text is easy to read.
SCRIM = QColor(0, 0, 0, 115)


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

    def __init__(self) -> None:
        super().__init__()
        self._allow_close = False
        self._scene = Scene("")
        self._previous: Optional[Scene] = None
        self._blend = 1.0

        self.setWindowTitle("Break time")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        title = QLabel("Break time", alignment=Qt.AlignCenter)
        title.setObjectName("overlayTitle")

        self._clock_label = QLabel(alignment=Qt.AlignCenter)
        self._clock_label.setObjectName("overlayClock")

        self._category_label = QLabel(alignment=Qt.AlignCenter)
        self._category_label.setObjectName("overlayCategory")

        self._tip_label = QLabel(alignment=Qt.AlignCenter)
        self._tip_label.setObjectName("overlayTip")
        self._tip_label.setWordWrap(True)
        self._tip_label.setMinimumHeight(180)

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
        layout.addWidget(self._category_label)
        layout.addWidget(self._tip_label)
        layout.addStretch(3)
        layout.addWidget(hint)

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

    def set_tip(
        self,
        tip: Tip,
        image_path: Optional[Path] = None,
        animate: bool = True,
    ) -> None:
        self._category_label.setText(CATEGORY_TITLE.get(tip.category, "").upper())
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
        self.close()

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
        picker: Optional[BackgroundPicker] = None,
    ) -> None:
        super().__init__(parent)
        self._rotator = rotator or TipRotator()
        self._picker = picker or BackgroundPicker()
        self._overlays: list = []
        self._clock_text = ""
        self._tip: Optional[Tip] = None
        self._image: Optional[Path] = None
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

    def show(self, clock_text: str) -> None:
        """Open the break windows (does nothing new if already open)."""
        self._clock_text = clock_text
        if self.is_active:
            self.update_clock(clock_text)
            return
        self._choose_tip()
        self._open_overlays()
        self._keep_on_top.start()
        self._schedule_next_tip()

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

    def _on_test_tick(self) -> None:
        self._test_remaining -= 1
        if self._test_remaining <= 0:
            self.hide()
        else:
            self.update_clock(format_clock(self._test_remaining))
