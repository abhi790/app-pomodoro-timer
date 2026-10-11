"""The pause screen: what you see after pressing Pause during focus.

Pause does not just stop the clock. It covers every monitor with this screen,
which has two choices:

* **Run:** carry on focusing, the clock continues from where it stopped.
* **Stop:** give this focus block up. This needs a math problem (one of the 3
  daily math unlocks). With none left, Stop is not offered, only Run.

``PauseOverlay`` is one full-screen window. ``PauseCoverManager`` opens one per
monitor and keeps them on top, the same way the break screen does. Like the
break screen, it has no close button, ignores Alt+F4 and Esc, and only shows
things and sends signals. The main window decides what happens.
"""

from typing import Optional

from PySide6.QtCore import QObject, QRectF, QTimer, Qt, Signal
from PySide6.QtGui import QCloseEvent, QGuiApplication, QIntValidator, QKeyEvent
from PySide6.QtGui import QPainter, QPaintEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pomodoro.lock_rules import can_stop
from pomodoro.math_quiz import Problem, ProblemMaker, is_correct
from pomodoro.usage import DAILY_MATH_LIMIT
from pomodoro.ui.break_overlay import Scene

KEEP_ON_TOP_MS = 500
PANEL_WIDTH = 520
# The menu and the math page have about the same height, so the clock above
# does not jump when you switch between them.
PANEL_MIN_HEIGHT = 250


class PauseOverlay(QWidget):
    """One full-screen pause window (one per monitor)."""

    run_chosen = Signal()
    math_solved = Signal()

    def __init__(self, maker: Optional[ProblemMaker] = None) -> None:
        super().__init__()
        self._allow_close = False
        self._scene = Scene("")
        self._maker = maker or ProblemMaker()
        self._problem: Optional[Problem] = None
        self._math_left = 0

        self.setWindowTitle("Paused")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        title = QLabel("Paused", alignment=Qt.AlignCenter)
        title.setObjectName("overlayTitle")
        self._clock_label = QLabel(alignment=Qt.AlignCenter)
        self._clock_label.setObjectName("overlayClock")

        # ----- page 1: Run and Stop -----------------------------------------
        self._menu = QWidget()
        self._menu.setObjectName("overlayPanel")  # see theme.py (transparent)
        self._status_label = QLabel(alignment=Qt.AlignCenter)
        self._status_label.setObjectName("overlayHint")
        self._status_label.setWordWrap(True)
        self._run_button = QPushButton("Run (carry on focusing)")
        self._stop_button = QPushButton("Stop (solve a math problem)")
        for button in (self._run_button, self._stop_button):
            button.setMinimumHeight(52)
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
        for button in (self._back_button, self._check_button):
            button.setMinimumHeight(52)
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
        layout.setContentsMargins(80, 30, 80, 30)
        layout.setSpacing(18)
        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(self._clock_label)
        layout.addSpacing(24)
        layout.addWidget(panel, alignment=Qt.AlignHCenter)
        layout.addStretch(2)

        self._run_button.clicked.connect(self.run_chosen)
        self._stop_button.clicked.connect(self._show_quiz)
        self._back_button.clicked.connect(self._show_menu)
        self._check_button.clicked.connect(self._on_check)
        self._answer_edit.returnPressed.connect(self._on_check)

        self.set_math_left(0)

    # ----- what the manager calls -----------------------------------------

    def set_clock(self, text: str) -> None:
        self._clock_label.setText(text)

    def set_math_left(self, math_left: int) -> None:
        """Say how many math unlocks are left today. With none, there is no
        Stop button, only Run."""
        self._math_left = math_left
        stop_allowed = can_stop(math_left)
        self._stop_button.setVisible(stop_allowed)
        if stop_allowed:
            text = (
                f"Math unlocks left today: {math_left} of {DAILY_MATH_LIMIT}. "
                "Stopping gives this focus block up and uses one."
            )
        else:
            text = "No math unlocks left today, so this focus block must go on."
        self._status_label.setText(text)
        if not stop_allowed and self._quiz.isVisible():
            self._show_menu()

    def close_for_real(self) -> None:
        """Close the window. Only the manager calls this."""
        self._allow_close = True
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

    def _new_problem(self) -> None:
        self._problem = self._maker.next_problem()
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
        self._scene.paint(painter, QRectF(self.rect()))
        painter.end()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._allow_close:
            event.accept()
        else:
            event.ignore()  # Alt+F4 and similar end up here

    def keyPressEvent(self, event: QKeyEvent) -> None:
        event.accept()  # swallow keys nobody else wanted, including Esc


class PauseCoverManager(QObject):
    """Shows the pause screen on all monitors and keeps it on top.

    ``run_chosen``: Run was pressed, the timer should carry on.
    ``stop_confirmed``: a math problem was solved, the focus block is given up.
    The manager does not count anything and does not touch the timer.
    """

    run_chosen = Signal()
    stop_confirmed = Signal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._overlays: list = []
        self._clock_text = ""
        self._math_left = 0

        self._keep_on_top = QTimer(self)
        self._keep_on_top.setInterval(KEEP_ON_TOP_MS)
        self._keep_on_top.timeout.connect(self._bring_to_front)

        app = QGuiApplication.instance()
        app.screenAdded.connect(self._on_screens_changed)
        app.screenRemoved.connect(self._on_screens_changed)

    @property
    def is_active(self) -> bool:
        return bool(self._overlays)

    def show(self, clock_text: str, math_left: int) -> None:
        """Open the pause screens (does nothing new if already open)."""
        self._clock_text = clock_text
        if self.is_active:
            return
        self._math_left = math_left
        self._open_overlays()
        self._keep_on_top.start()

    def hide(self) -> None:
        """Close all pause screens."""
        self._keep_on_top.stop()
        overlays, self._overlays = self._overlays, []
        for overlay in overlays:
            overlay.close_for_real()
            overlay.deleteLater()

    # ----- internals -------------------------------------------------------

    def _open_overlays(self) -> None:
        for screen in QGuiApplication.screens():
            overlay = PauseOverlay()
            overlay.setScreen(screen)
            overlay.setGeometry(screen.geometry())
            overlay.set_clock(self._clock_text)
            overlay.set_math_left(self._math_left)
            overlay.run_chosen.connect(self.run_chosen)
            overlay.math_solved.connect(self.stop_confirmed)
            overlay.showFullScreen()
            self._overlays.append(overlay)
        if self._overlays:
            self._overlays[0].activateWindow()

    def _on_screens_changed(self, *_args) -> None:
        """A monitor was plugged in or removed while the pause screen is on."""
        if self.is_active:
            self.hide()
            self._open_overlays()
            self._keep_on_top.start()

    def _bring_to_front(self) -> None:
        """If the user clicked away, bring the pause screens back."""
        for overlay in self._overlays:
            if not overlay.isVisible() or overlay.isMinimized():
                overlay.showFullScreen()
            overlay.raise_()
        if self._overlays and not any(o.isActiveWindow() for o in self._overlays):
            self._overlays[0].activateWindow()
