"""The pause screen: what you see after pressing Pause during focus.

Pause does not just stop the clock. It covers every monitor with this screen,
which has two choices:

* **Run:** carry on focusing, the clock continues from where it stopped.
* **Stop:** give this focus block up. This always needs a math problem first,
  with no daily cap: solve it and the block is given up.

While you decide, the screen shows the same healthy tips and background
pictures as the break screen, so a pause is a small moment of rest too.

``PauseOverlay`` is one full-screen window. ``PauseCoverManager`` opens one per
monitor, keeps them on top and rotates the tips, the same way the break screen
does. Like the break screen, it has no close button, ignores Alt+F4 and Esc,
and only shows things and sends signals. The main window decides what happens.
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QRectF, QTimer, Qt, QVariantAnimation, Signal
from PySide6.QtGui import (
    QCloseEvent,
    QGuiApplication,
    QIntValidator,
    QKeyEvent,
    QPainter,
    QPaintEvent,
    QPixmap,
)
from PySide6.QtWidgets import (
    QGraphicsOpacityEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pomodoro.backgrounds import BackgroundPicker
from pomodoro.fit_text import pick_font_px
from pomodoro.math_quiz import MAX_LEVEL, Problem, ProblemMaker, is_correct, level_for_unlock
from pomodoro.tips import CATEGORY_TITLE, Tip, TipRotator, tip_display_seconds
from pomodoro.ui.break_overlay import FADE_MS, TIP_MAX_WIDTH, Scene
from pomodoro.ui.emergency_exit import make_emergency_button, place_in_corner
from pomodoro.ui.theme import SCREEN_STYLE

KEEP_ON_TOP_MS = 500
PANEL_WIDTH = 520
# The menu and the math page have about the same height, so the clock above
# does not jump when you switch between them.
PANEL_MIN_HEIGHT = 230
# The tip column: wide enough for 3 or 4 lines, and tall enough for 4 lines.
TIP_MIN_WIDTH = 780
TIP_MIN_HEIGHT = 190


class PauseOverlay(QWidget):
    """One full-screen pause window (one per monitor)."""

    run_chosen = Signal()
    math_solved = Signal()
    emergency_exit = Signal()  # testing only, see emergency_exit.py

    def __init__(self, maker: Optional[ProblemMaker] = None) -> None:
        super().__init__()
        self._allow_close = False
        self._scene = Scene("")
        self._previous: Optional[Scene] = None
        self._blend = 1.0
        self._maker = maker or ProblemMaker()
        self._problem: Optional[Problem] = None
        self._math_used = 0

        self.setWindowTitle("Paused")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # Always dark, even in Day mode: white text over a picture.
        self.setStyleSheet(SCREEN_STYLE)

        title = QLabel("Paused", alignment=Qt.AlignCenter)
        title.setObjectName("overlayTitle")
        self._clock_label = QLabel(alignment=Qt.AlignCenter)
        self._clock_label.setObjectName("pauseClock")

        # The healthy tip, like on the break screen. The column is wide enough
        # that a tip takes at most 3 or 4 lines, so nothing is cut off.
        self._category_label = QLabel(alignment=Qt.AlignCenter)
        self._category_label.setObjectName("overlayCategory")
        self._tip_label = QLabel(alignment=Qt.AlignCenter)
        self._tip_label.setObjectName("overlayTip")
        self._tip_label.setWordWrap(True)
        self._tip_label.setMinimumWidth(TIP_MIN_WIDTH)
        self._tip_label.setMaximumWidth(TIP_MAX_WIDTH)
        self._tip_label.setMinimumHeight(TIP_MIN_HEIGHT)

        # ----- page 1: Run and Stop -----------------------------------------
        self._menu = QWidget()
        self._menu.setObjectName("overlayPanel")  # see theme.py (transparent)
        self._status_label = QLabel(alignment=Qt.AlignCenter)
        self._status_label.setObjectName("overlayHint")
        self._status_label.setWordWrap(True)
        self._run_button = QPushButton("Run (carry on focusing)")
        self._stop_button = QPushButton("Stop (solve a math problem)")
        self._run_button.setDefault(True)
        menu_layout = QVBoxLayout(self._menu)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(12)
        menu_layout.addWidget(self._status_label)
        menu_layout.addWidget(self._run_button)
        menu_layout.addWidget(self._stop_button)

        # ----- page 2: the math problem -------------------------------------
        self._quiz = QWidget()
        self._quiz.setObjectName("overlayPanel")
        self._problem_label = QLabel(alignment=Qt.AlignCenter)
        self._problem_label.setObjectName("overlayQuiz")
        self._answer_edit = QLineEdit()
        self._answer_edit.setObjectName("overlayAnswer")
        self._answer_edit.setAlignment(Qt.AlignCenter)
        self._answer_edit.setPlaceholderText("Your answer")
        self._answer_edit.setMaxLength(6)
        self._answer_edit.setValidator(QIntValidator(0, 999999, self))
        self._feedback_label = QLabel(alignment=Qt.AlignCenter)
        self._feedback_label.setObjectName("overlayHint")
        self._feedback_label.setWordWrap(True)
        self._back_button = QPushButton("Back")
        self._check_button = QPushButton("Check")
        buttons = QHBoxLayout()
        buttons.setSpacing(12)
        buttons.addWidget(self._back_button)
        buttons.addWidget(self._check_button)
        quiz_layout = QVBoxLayout(self._quiz)
        quiz_layout.setContentsMargins(0, 0, 0, 0)
        quiz_layout.setSpacing(10)
        quiz_layout.addWidget(self._problem_label)
        quiz_layout.addWidget(self._answer_edit)
        quiz_layout.addWidget(self._feedback_label)
        quiz_layout.addLayout(buttons)

        # The buttons sit on top of a picture, so they are a little see-through
        # (see "overlayButton" in theme.py).
        for button in (
            self._run_button,
            self._stop_button,
            self._back_button,
            self._check_button,
        ):
            button.setObjectName("overlayButton")
            button.setMinimumHeight(52)

        panel = QWidget()
        panel.setObjectName("overlayPanel")
        panel.setFixedWidth(PANEL_WIDTH)
        panel.setMinimumHeight(PANEL_MIN_HEIGHT)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setAlignment(Qt.AlignTop)
        panel_layout.addWidget(self._menu)
        panel_layout.addWidget(self._quiz)
        self._quiz.hide()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(60, 16, 60, 16)
        layout.setSpacing(8)
        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(self._clock_label)
        layout.addWidget(self._category_label)
        layout.addWidget(self._tip_label, alignment=Qt.AlignHCenter)
        layout.addStretch(1)
        layout.addWidget(panel, alignment=Qt.AlignHCenter)
        layout.addStretch(1)

        # Testing only: leave at once, no math (None when the flag is off). It
        # floats in the corner, so it does not change the layout.
        self._emergency_button = make_emergency_button(self)
        if self._emergency_button is not None:
            self._emergency_button.clicked.connect(self.emergency_exit)
            place_in_corner(self._emergency_button, self)

        # Soft changes when a new tip arrives: the picture cross-fades and the
        # text fades in (the same as on the break screen).
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

        self._run_button.clicked.connect(self.run_chosen)
        self._stop_button.clicked.connect(self._show_quiz)
        self._back_button.clicked.connect(self._show_menu)
        self._check_button.clicked.connect(self._on_check)
        self._answer_edit.returnPressed.connect(self._on_check)

        self.set_math_used(0)

    # ----- what the manager calls -----------------------------------------

    def set_clock(self, text: str) -> None:
        self._clock_label.setText(text)

    def set_tip(
        self,
        tip: Tip,
        image_path: Optional[Path] = None,
        animate: bool = True,
    ) -> None:
        """Show a healthy tip with its picture (a soft colored background if
        the category has no picture)."""
        self._category_label.setText(CATEGORY_TITLE.get(tip.category, "").upper())
        self._tip_label.setText(tip.text)
        self._fit_tip_font()

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

    def _fit_tip_font(self) -> None:
        """Make the tip fit in its box, whatever the font of this computer.

        How many pixels tall a tip is depends on the font and on the Windows
        display scale. So the normal size is tried first, and a smaller one
        only if the text would be taller than the box (see ``fit_text.py``).
        The text is measured at the narrowest width the column can have, so
        it also fits when the column is wider."""
        label = self._tip_label
        text = label.text()
        width = max(label.width(), TIP_MIN_WIDTH)
        flags = int(Qt.TextWordWrap | Qt.AlignCenter)

        def height_at(px: int) -> int:
            label.setStyleSheet(f"font-size: {px}px;")
            label.ensurePolished()
            return label.fontMetrics().boundingRect(0, 0, width, 10000, flags, text).height()

        size = pick_font_px(height_at, TIP_MIN_HEIGHT)
        label.setStyleSheet(f"font-size: {size}px;")
        label.ensurePolished()

    def set_math_used(self, math_used: int) -> None:
        """Say how many math problems have been solved today (sets the level
        of the next one; Stop is always offered)."""
        self._math_used = math_used
        self._status_label.setText(
            f"Stopping gives this focus block up and needs a math problem "
            f"(next: level {self._level()} of {MAX_LEVEL})."
        )

    def close_for_real(self) -> None:
        """Close the window. Only the manager calls this."""
        self._allow_close = True
        self._fade.stop()
        self.close()

    # ----- the pages -------------------------------------------------------

    def _show_menu(self) -> None:
        self._quiz.hide()
        self._answer_edit.clear()
        self._menu.show()

    def _show_quiz(self) -> None:
        self._new_problem()
        self._feedback_label.setText("")
        self._menu.hide()
        self._quiz.show()
        self._answer_edit.setFocus()

    def _level(self) -> int:
        """The problems get harder with every one solved today."""
        return level_for_unlock(self._math_used)

    def _new_problem(self) -> None:
        self._problem = self._maker.next_problem(self._level())
        self._problem_label.setText(f"{self._problem.text} = ?")
        self._answer_edit.clear()
        self._answer_edit.setFocus()

    def _on_check(self) -> None:
        if self._problem is None:
            return
        typed = self._answer_edit.text()
        if not typed.strip():
            self._feedback_label.setText("Type your answer first.")
            return
        if is_correct(self._problem, typed):
            self.math_solved.emit()
            return
        self._new_problem()
        self._feedback_label.setText("Not quite. Here is a new problem.")

    # ----- drawing and the things the user must not be able to do ----------

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


class PauseCoverManager(QObject):
    """Shows the pause screen on all monitors, keeps it on top and rotates
    the healthy tips (the same tip with the same picture on every monitor).

    ``run_chosen``: Run was pressed, the timer should carry on.
    ``stop_confirmed``: a math problem was solved, the focus block is given up.
    The manager does not count anything and does not touch the timer.
    """

    run_chosen = Signal()
    stop_confirmed = Signal()
    emergency_exit = Signal()  # testing only, see emergency_exit.py

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
        self._math_used = 0
        self._tip: Optional[Tip] = None
        self._image: Optional[Path] = None

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

    def show(self, clock_text: str, math_used: int) -> None:
        """Open the pause screens (does nothing new if already open)."""
        self._clock_text = clock_text
        if self.is_active:
            return
        self._math_used = math_used
        self._choose_tip()
        self._open_overlays()
        self._keep_on_top.start()
        self._schedule_next_tip()

    def hide(self) -> None:
        """Close all pause screens."""
        self._keep_on_top.stop()
        self._tip_timer.stop()
        self._close_overlays()

    # ----- internals -------------------------------------------------------

    def _choose_tip(self) -> None:
        self._tip = self._rotator.next_tip()
        self._image = self._picker.pick(self._tip.category)

    def _schedule_next_tip(self) -> None:
        self._tip_timer.start(tip_display_seconds(self._tip.text) * 1000)

    def _show_next_tip(self) -> None:
        self._choose_tip()
        for overlay in self._overlays:
            overlay.set_tip(self._tip, self._image, animate=True)
        self._schedule_next_tip()

    def _open_overlays(self) -> None:
        for screen in QGuiApplication.screens():
            overlay = PauseOverlay()
            overlay.setScreen(screen)
            overlay.setGeometry(screen.geometry())
            overlay.set_clock(self._clock_text)
            overlay.set_tip(self._tip, self._image, animate=False)
            overlay.set_math_used(self._math_used)
            overlay.run_chosen.connect(self.run_chosen)
            overlay.math_solved.connect(self.stop_confirmed)
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
        """A monitor was plugged in or removed while the pause screen is on."""
        if self.is_active:
            self._close_overlays()
            self._open_overlays()

    def _bring_to_front(self) -> None:
        """If the user clicked away, bring the pause screens back."""
        for overlay in self._overlays:
            if not overlay.isVisible() or overlay.isMinimized():
                overlay.showFullScreen()
            overlay.raise_()
        if self._overlays and not any(o.isActiveWindow() for o in self._overlays):
            self._overlays[0].activateWindow()
