"""The main window: big countdown plus Start/Pause, Reset and Skip buttons.

All the timing rules live in ``timer_logic.py``. This file only shows the
state on screen and passes button clicks to the timer.
"""

import time
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pomodoro.formatting import format_clock
from pomodoro.timer_logic import Phase, PomodoroTimer

PHASE_NAME = {
    Phase.FOCUS: "Focus",
    Phase.SHORT_BREAK: "Short break",
    Phase.LONG_BREAK: "Long break",
}

PHASE_COLOR = {
    Phase.FOCUS: "#d9534f",
    Phase.SHORT_BREAK: "#3c9d5d",
    Phase.LONG_BREAK: "#3b7ddd",
}

# How often the screen checks the clock. The timer itself still counts in
# whole seconds, this just keeps the display from drifting.
CHECK_INTERVAL_MS = 200


class MainWindow(QWidget):
    def __init__(self, timer: Optional[PomodoroTimer] = None) -> None:
        super().__init__()
        self._timer = timer or PomodoroTimer()
        self._last_tick = time.monotonic()

        self.setWindowTitle("Pomodoro Timer")
        self.setMinimumSize(340, 320)
        self._build_ui()

        self._clock_checker = QTimer(self)
        self._clock_checker.setInterval(CHECK_INTERVAL_MS)
        self._clock_checker.timeout.connect(self._on_clock_check)
        self._clock_checker.start()

        self._refresh()

    # ----- building the screen --------------------------------------------

    def _build_ui(self) -> None:
        self._phase_label = QLabel(alignment=Qt.AlignCenter)
        self._phase_label.setStyleSheet("font-size: 22px; font-weight: bold;")

        self._clock_label = QLabel(alignment=Qt.AlignCenter)
        self._clock_label.setStyleSheet("font-size: 72px; font-weight: bold;")

        self._count_label = QLabel(alignment=Qt.AlignCenter)
        self._message_label = QLabel(alignment=Qt.AlignCenter)
        self._message_label.setWordWrap(True)

        self._toggle_button = QPushButton("Start")
        self._reset_button = QPushButton("Reset")
        self._toggle_button.clicked.connect(self._on_toggle)
        self._reset_button.clicked.connect(self._on_reset)

        buttons = QHBoxLayout()
        for button in (self._toggle_button, self._reset_button):
            button.setMinimumHeight(40)
            buttons.addWidget(button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(self._phase_label)
        layout.addWidget(self._clock_label)
        layout.addWidget(self._count_label)
        layout.addWidget(self._message_label)
        layout.addStretch(1)
        layout.addLayout(buttons)

    # ----- button actions --------------------------------------------------

    def _on_toggle(self) -> None:
        if self._timer.running:
            self._timer.pause()
        else:
            self._timer.start()
            self._last_tick = time.monotonic()
            self._message_label.setText("")
        self._refresh()

    def _on_reset(self) -> None:
        self._timer.reset()
        self._message_label.setText("")
        self._refresh()

    # ----- time passing ----------------------------------------------------

    def _on_clock_check(self) -> None:
        if not self._timer.running:
            return
        now = time.monotonic()
        whole_seconds = int(now - self._last_tick)
        if whole_seconds < 1:
            return
        self._last_tick += whole_seconds
        finished = self._timer.tick(whole_seconds)
        if finished is not None:
            self._announce(finished)
        self._refresh()

    def _announce(self, finished: Phase) -> None:
        if finished is Phase.FOCUS:
            if self._timer.phase is Phase.LONG_BREAK:
                text = "Great work! Time for your long break."
            else:
                text = "Focus done! Take a short break."
        else:
            text = "Break is over. Ready to focus?"
        self._message_label.setText(text)
        QApplication.alert(self)  # flash the taskbar icon

    # ----- showing the state -----------------------------------------------

    def _refresh(self) -> None:
        phase = self._timer.phase
        clock = format_clock(self._timer.remaining_seconds)

        self._phase_label.setText(PHASE_NAME[phase])
        self._phase_label.setStyleSheet(
            f"font-size: 22px; font-weight: bold; color: {PHASE_COLOR[phase]};"
        )
        self._clock_label.setText(clock)
        self._count_label.setText(
            f"Pomodoros done: {self._timer.completed_pomodoros}"
        )
        self._toggle_button.setText("Pause" if self._timer.running else "Start")
        self.setWindowTitle(f"{clock} - {PHASE_NAME[phase]}")
