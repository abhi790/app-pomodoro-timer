"""The main window: big countdown plus Start/Pause and Reset buttons.

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
from pomodoro.settings import MODE_NAME, AppConfig, Mode, save_config
from pomodoro.timer_logic import Phase, PomodoroTimer
from pomodoro.ui.break_manager import BreakOverlayManager
from pomodoro.ui.settings_dialog import SettingsDialog
from pomodoro.usage import DAILY_MATH_LIMIT, IMPORTANT_BREAK_SECONDS, UsageTracker

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

# How long the test buttons show the break screen (long enough to solve a
# math problem and read a tip or two).
TEST_OVERLAY_SECONDS = 60


class MainWindow(QWidget):
    def __init__(
        self,
        config: Optional[AppConfig] = None,
        usage: Optional[UsageTracker] = None,
    ) -> None:
        super().__init__()
        self._config = config or AppConfig()
        self._usage = usage or UsageTracker()
        self._timer = PomodoroTimer(self._config.timer_settings())
        self._last_tick = time.monotonic()
        self._overlay = BreakOverlayManager(self)
        self._overlay.math_unlocked.connect(self._on_math_unlocked)
        self._overlay.important_chosen.connect(self._on_important)
        self._overlay.emergency_exit.connect(self._on_emergency_exit)
        self._force_break_active = False

        self.setWindowTitle("Pomodoro Timer")
        self.setMinimumSize(520, 580)
        self._build_ui()

        self._clock_checker = QTimer(self)
        self._clock_checker.setInterval(CHECK_INTERVAL_MS)
        self._clock_checker.timeout.connect(self._on_clock_check)
        self._clock_checker.start()

        self._refresh()

    # ----- building the screen --------------------------------------------

    def _build_ui(self) -> None:
        self._phase_label = QLabel(alignment=Qt.AlignCenter)
        self._phase_label.setObjectName("phase")

        self._clock_label = QLabel(alignment=Qt.AlignCenter)
        self._clock_label.setObjectName("clock")

        self._count_label = QLabel(alignment=Qt.AlignCenter)
        self._count_label.setObjectName("muted")
        self._mode_label = QLabel(alignment=Qt.AlignCenter)
        self._mode_label.setObjectName("muted")
        self._message_label = QLabel(alignment=Qt.AlignCenter)
        self._message_label.setObjectName("message")
        self._message_label.setWordWrap(True)

        self._toggle_button = QPushButton("Start")
        self._reset_button = QPushButton("Reset")
        self._settings_button = QPushButton("Settings")
        # Two buttons for trying the break screen. Dev-only, removed later.
        self._test_button = QPushButton("Test overlay")
        self._test_no_math_button = QPushButton("Test: no math left")
        self._toggle_button.clicked.connect(self._on_toggle)
        self._reset_button.clicked.connect(self._on_reset)
        self._settings_button.clicked.connect(self._on_settings)
        self._test_button.clicked.connect(self._on_test_overlay)
        self._test_no_math_button.clicked.connect(self._on_test_overlay_no_math)

        buttons = QHBoxLayout()
        for button in (
            self._toggle_button,
            self._reset_button,
            self._settings_button,
        ):
            button.setMinimumHeight(52)
            buttons.addWidget(button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(14)
        layout.addWidget(self._phase_label)
        layout.addWidget(self._clock_label)
        layout.addWidget(self._count_label)
        layout.addWidget(self._mode_label)
        layout.addWidget(self._message_label)
        layout.addStretch(1)
        layout.addLayout(buttons)
        test_buttons = QHBoxLayout()
        test_buttons.addWidget(self._test_button)
        test_buttons.addWidget(self._test_no_math_button)
        layout.addLayout(test_buttons)

    # ----- button actions --------------------------------------------------

    def _on_toggle(self) -> None:
        if self._force_break_active:
            return
        if self._timer.running:
            self._timer.pause()
        else:
            self._timer.start()
            self._last_tick = time.monotonic()
            self._message_label.setText("")
        self._refresh()

    def _on_reset(self) -> None:
        if self._force_break_active:
            return
        self._timer.reset()
        self._message_label.setText("")
        self._refresh()

    def _on_test_overlay(self) -> None:
        """Try the break screen with all math unlocks available."""
        if self._force_break_active:
            return
        self._overlay.show_test(TEST_OVERLAY_SECONDS, DAILY_MATH_LIMIT)

    def _on_test_overlay_no_math(self) -> None:
        """Try the break screen as it looks when the math unlocks are used up."""
        if self._force_break_active:
            return
        self._overlay.show_test(TEST_OVERLAY_SECONDS, 0)

    def _on_settings(self) -> None:
        if self._force_break_active:
            return
        dialog = SettingsDialog(self._config, self)
        if dialog.exec() != SettingsDialog.Accepted:
            return
        self._config = dialog.result_config()
        try:
            save_config(self._config)
        except OSError:
            self._message_label.setText("Could not save your settings.")
        self._timer.update_settings(self._config.timer_settings())
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
            if self._config.mode is Mode.FORCE_BREAK:
                self._start_force_break()
                return
            if self._timer.phase is Phase.LONG_BREAK:
                text = "Great work! Time for your long break."
            else:
                text = "Focus done! Take a short break."
        else:
            self._end_force_break()
            text = "Break is over. Ready to focus?"
        self._message_label.setText(text)
        QApplication.alert(self)  # flash the taskbar icon

    def _start_force_break(self) -> None:
        """Focus is done in Force Break mode: start the break and cover the
        screens. The overlay closes by itself when the break ends."""
        self._timer.start()
        self._last_tick = time.monotonic()
        self._force_break_active = True
        self._message_label.setText("Force Break: time to rest.")
        self._overlay.show(
            format_clock(self._timer.remaining_seconds), self._usage.math_left
        )

    def _end_force_break(self) -> None:
        if self._force_break_active:
            self._force_break_active = False
            self._overlay.hide()

    def _on_math_unlocked(self) -> None:
        """A math problem was solved: the break ends now. The timer waits on
        Focus until the user presses Start."""
        if not self._force_break_active:
            return
        self._usage.record_math()
        self._timer.skip()  # break -> Focus, stopped
        self._end_force_break()
        self._message_label.setText("Break ended early. Ready to focus?")
        self._refresh()

    def _on_emergency_exit(self) -> None:
        """Emergency exit: the break ends now and nothing is counted. The timer
        waits on Focus until the user presses Start."""
        if not self._force_break_active:
            return
        self._timer.skip()  # break -> Focus, stopped
        self._end_force_break()
        self._message_label.setText("Emergency exit used. Ready to focus?")
        self._refresh()

    def _on_important(self) -> None:
        """Important was pressed: the break keeps going, but at most 3 more
        minutes."""
        if not self._force_break_active:
            return
        self._usage.record_important()
        self._timer.limit_remaining(IMPORTANT_BREAK_SECONDS)
        self._overlay.mark_important_used()
        self._refresh()  # shows the shorter clock on the break screen

    # ----- showing the state -----------------------------------------------

    def _refresh(self) -> None:
        phase = self._timer.phase
        clock = format_clock(self._timer.remaining_seconds)

        self._phase_label.setText(PHASE_NAME[phase])
        self._phase_label.setStyleSheet(f"color: {PHASE_COLOR[phase]};")
        self._clock_label.setText(clock)
        self._count_label.setText(
            f"Pomodoros done: {self._timer.completed_pomodoros}"
        )
        self._mode_label.setText(f"Mode: {MODE_NAME[self._config.mode]}")
        self._toggle_button.setText("Pause" if self._timer.running else "Start")
        self.setWindowTitle(f"{clock} - {PHASE_NAME[phase]}")
        if self._force_break_active:
            self._overlay.update_clock(clock)
