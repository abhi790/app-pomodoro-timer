"""The "leave the break" controls on the Force Break screen.

The panel has two pages:

* the menu: "Leave break early" while math unlocks are left today. When they
  are used up, the button goes away and the break simply runs its full length
* the quiz: a math problem, a box for the answer, Check and Back

The panel only shows things and sends signals. It does not count anything and
does not touch the timer. The main window listens to ``math_solved`` and
decides what happens.
"""

from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pomodoro.math_quiz import Problem, ProblemMaker, is_correct
from pomodoro.usage import DAILY_MATH_LIMIT

PANEL_MIN_WIDTH = 520
PANEL_MAX_WIDTH = 640
# The menu and the quiz have about the same height, so the clock above does
# not jump when you switch between them.
PANEL_MIN_HEIGHT = 230


class UnlockPanel(QWidget):
    math_solved = Signal()

    def __init__(self, maker: Optional[ProblemMaker] = None) -> None:
        super().__init__()
        self.setObjectName("overlayPanel")
        self.setMinimumWidth(PANEL_MIN_WIDTH)
        self.setMaximumWidth(PANEL_MAX_WIDTH)
        self.setMinimumHeight(PANEL_MIN_HEIGHT)

        self._maker = maker or ProblemMaker()
        self._problem: Optional[Problem] = None
        self._math_left = DAILY_MATH_LIMIT

        # ----- page 1: the menu ---------------------------------------------
        self._menu = QWidget()
        self._menu.setObjectName("overlayPanel")
        self._status_label = QLabel(alignment=Qt.AlignCenter)
        self._status_label.setObjectName("overlayHint")
        self._status_label.setWordWrap(True)
        self._leave_button = QPushButton("Leave break early (solve a math problem)")
        self._leave_button.setMinimumHeight(52)

        menu_layout = QVBoxLayout(self._menu)
        menu_layout.setContentsMargins(0, 0, 0, 0)
        menu_layout.setSpacing(12)
        menu_layout.addWidget(self._status_label)
        menu_layout.addWidget(self._leave_button)

        # ----- page 2: the quiz ---------------------------------------------
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

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setAlignment(Qt.AlignTop)
        root.addWidget(self._menu)
        root.addWidget(self._quiz)
        self._quiz.hide()

        self._leave_button.clicked.connect(self._show_quiz)
        self._back_button.clicked.connect(self._show_menu)
        self._check_button.clicked.connect(self._on_check)
        self._answer_edit.returnPressed.connect(self._on_check)

        self._refresh_menu()

    # ----- what the overlay calls ------------------------------------------

    def set_state(self, math_left: int) -> None:
        """Say how many math unlocks are left today."""
        self._math_left = math_left
        self._refresh_menu()
        if math_left <= 0 and self._quiz.isVisible():
            self._show_menu()

    # ----- the menu --------------------------------------------------------

    def _refresh_menu(self) -> None:
        has_math = self._math_left > 0
        self._leave_button.setVisible(has_math)
        if has_math:
            text = f"Math unlocks left today: {self._math_left} of {DAILY_MATH_LIMIT}"
        else:
            text = "No math unlocks left today. This break runs its full time."
        self._status_label.setText(text)

    def _show_menu(self) -> None:
        self._quiz.hide()
        self._answer_edit.clear()
        self._menu.show()

    # ----- the quiz --------------------------------------------------------

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
