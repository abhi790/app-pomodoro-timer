"""The main window: big countdown plus Start/Pause and Reset buttons.

All the timing rules live in ``timer_logic.py``. This file only shows the
state on screen and passes button clicks to the timer.
"""

import time
from typing import Optional

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pomodoro.formatting import format_clock
from pomodoro.lock_rules import controls_enabled
from pomodoro.settings import MODE_NAME, AppConfig, save_config
from pomodoro.timer_logic import Phase, PomodoroTimer
from pomodoro.tray_logic import HIDE, can_quit, close_action, tray_tooltip
from pomodoro.ui.break_manager import BreakOverlayManager
from pomodoro.ui.pause_overlay import PauseCoverManager
from pomodoro.ui.settings_dialog import SettingsDialog
from pomodoro.ui.sound_player import AlertSound
from pomodoro.ui.tray import TrayIcon
from pomodoro.usage import IMPORTANT_BREAK_SECONDS, UsageTracker

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
    def __init__(
        self,
        config: Optional[AppConfig] = None,
        usage: Optional[UsageTracker] = None,
        sound: Optional[AlertSound] = None,
        tray: Optional[TrayIcon] = None,
    ) -> None:
        super().__init__()
        self._config = config or AppConfig()
        self._usage = usage or UsageTracker()
        self._sound = sound or AlertSound(self)
        # The tray icon. The window hides there when you close it, and the
        # timer keeps running. Quit (in the tray menu) really closes the app.
        self._tray = tray or TrayIcon(self)
        self._tray.show_requested.connect(self._show_from_tray)
        self._tray.quit_requested.connect(self._quit_app)
        self._quitting = False
        self._told_about_tray = False
        self._timer = PomodoroTimer(self._config.timer_settings())
        self._last_tick = time.monotonic()
        self._overlay = BreakOverlayManager(self)
        self._overlay.set_custom_ideas(self._config.ideas)
        self._overlay.math_unlocked.connect(self._on_math_unlocked)
        self._overlay.important_chosen.connect(self._on_important)
        self._force_break_active = False
        # Pause covers the screens with Run and Stop (Stop needs a math problem).
        self._pause_cover = PauseCoverManager(self)
        self._pause_cover.run_chosen.connect(self._on_run_chosen)
        self._pause_cover.stop_confirmed.connect(self._on_stop_confirmed)

        self.setWindowTitle("Pomodoro Timer")
        self.setMinimumSize(520, 640)
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
        # Start/Pause is the main action, so it stands out (see theme.py).
        self._toggle_button.setObjectName("primary")
        self._reset_button = QPushButton("Reset")
        self._settings_button = QPushButton("Settings")
        self._toggle_button.clicked.connect(self._on_toggle)
        self._reset_button.clicked.connect(self._on_reset)
        self._settings_button.clicked.connect(self._on_settings)

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
        # Equal stretch above and below, so the timer sits in the middle and
        # does not hang at the top with a big hole above the buttons.
        layout.addStretch(1)
        layout.addWidget(self._phase_label)
        layout.addWidget(self._clock_label)
        layout.addWidget(self._count_label)
        layout.addWidget(self._mode_label)
        layout.addWidget(self._message_label)
        layout.addStretch(1)
        layout.addLayout(buttons)

    # ----- button actions --------------------------------------------------

    def _controls_enabled(self) -> bool:
        """Reset and Settings only work while the timer is stopped and no
        break screen or pause screen is up (see ``lock_rules.py``)."""
        return controls_enabled(
            self._timer.running,
            self._force_break_active,
            self._pause_cover.is_active,
        )

    def _on_toggle(self) -> None:
        if self._force_break_active or self._pause_cover.is_active:
            return
        if self._timer.running:
            # Pause is not a quiet pause: the pause screen covers the monitors
            # and you choose Run or Stop there.
            self._timer.pause()
            self._pause_cover.show(
                format_clock(self._timer.remaining_seconds), self._usage.math_left
            )
        else:
            self._timer.start()
            self._last_tick = time.monotonic()
            self._message_label.setText("")
        self._refresh()

    def _on_run_chosen(self) -> None:
        """Run on the pause screen: carry on from where the clock stopped."""
        if not self._pause_cover.is_active:
            return
        self._pause_cover.hide()
        self._timer.start()
        self._last_tick = time.monotonic()
        self._refresh()

    def _on_stop_confirmed(self) -> None:
        """A math problem was solved on the pause screen: this focus block is
        given up (it does not count) and the timer waits for Start."""
        if not self._pause_cover.is_active:
            return
        self._usage.record_math()
        self._pause_cover.hide()
        self._timer.abandon_focus()
        self._message_label.setText("Focus stopped. Ready when you are.")
        self._refresh()

    def _on_reset(self) -> None:
        if not self._controls_enabled():
            return
        self._timer.reset()
        self._message_label.setText("")
        self._refresh()

    def _on_settings(self) -> None:
        if not self._controls_enabled():
            return
        dialog = SettingsDialog(self._config, self, self._sound)
        if dialog.exec() != SettingsDialog.Accepted:
            return
        self._config = dialog.result_config()
        try:
            save_config(self._config)
        except OSError:
            self._message_label.setText("Could not save your settings.")
        self._overlay.set_custom_ideas(self._config.ideas)
        self._timer.update_settings(self._config.timer_settings())
        self._refresh()

    # ----- the tray --------------------------------------------------------

    def closeEvent(self, event: QCloseEvent) -> None:
        """The close button hides the window to the tray. The timer keeps
        running. (Without a tray, or after Quit, the app really closes.)"""
        if close_action(self._tray.available, self._quitting) == HIDE:
            event.ignore()
            self.hide()
            if not self._told_about_tray:
                self._told_about_tray = True
                self._tray.notify(
                    "Pomodoro Timer",
                    "Still running in the tray. Right-click the tomato to quit.",
                )
            return
        self._tray.hide()
        event.accept()

    def _show_from_tray(self) -> None:
        """Bring the window back (also when it is minimized)."""
        self.showNormal()
        self.raise_()
        self.activateWindow()

    def _quit_app(self) -> None:
        """Quit from the tray menu. Not during a Force Break or the pause screen
        (the menu item is greyed out then, and this check is a second safety)."""
        if not can_quit(self._force_break_active, self._pause_cover.is_active):
            return
        self._quitting = True
        self.close()
        QApplication.quit()

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
        """A block ended. After focus, the break always starts by itself and
        covers the screens (in both modes). After a break, wait for Start."""
        self._play_alert()
        if finished is Phase.FOCUS:
            self._start_force_break()
            return
        self._end_force_break()
        self._message_label.setText("Break is over. Ready to focus?")
        QApplication.alert(self)  # flash the taskbar icon
        if not self.isVisible():  # hidden in the tray: say it there
            self._tray.notify("Break is over", "Ready to focus?")

    def _play_alert(self) -> None:
        """The sound for the end of a focus block or a break (if it is on)."""
        if self._config.sound_enabled:
            self._sound.play(self._config.sound_file)

    def _start_force_break(self) -> None:
        """Focus is done: start the break and cover the screens. The overlay
        closes by itself when the break ends."""
        self._timer.start()
        self._last_tick = time.monotonic()
        self._force_break_active = True
        self._message_label.setText("Time to rest.")
        self._overlay.show(
            format_clock(self._timer.remaining_seconds),
            self._usage.math_left,
            long_break=self._timer.phase is Phase.LONG_BREAK,
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
        self._tray.set_tooltip(
            tray_tooltip(PHASE_NAME[phase], clock, self._timer.running)
        )
        self._tray.set_quit_enabled(
            can_quit(self._force_break_active, self._pause_cover.is_active)
        )
        controls_on = self._controls_enabled()
        self._reset_button.setEnabled(controls_on)
        self._settings_button.setEnabled(controls_on)
        if self._force_break_active:
            self._overlay.update_clock(clock)
