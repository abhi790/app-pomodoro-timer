"""The settings window: pick a mode and, for Custom, set your own times.

It also has the alert sound (on or off, the default chime or your own .wav
file) and your own long-break ideas.
"""

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from pomodoro.ideas import ideas_from_text, ideas_to_text
from pomodoro.settings import (
    LONG_BREAK_MINUTES,
    MAX_FOCUS_MINUTES,
    MIN_BREAK_MINUTES,
    MODE_NAME,
    POMODOROS_BEFORE_LONG_BREAK,
    PRESETS,
    AppConfig,
    Mode,
)
from pomodoro.sound import check_sound_file
from pomodoro.timer_logic import TimerSettings
from pomodoro.ui.sound_player import AlertSound

MODE_HINT = {
    Mode.POMODORO: (
        "The classic: 25 min focus, 5 min break. Every break takes over the "
        f"screen. After every {POMODOROS_BEFORE_LONG_BREAK} focus blocks you "
        f"get a {LONG_BREAK_MINUTES} min long break."
    ),
    Mode.CUSTOM: (
        f"Set your own focus (1 to {MAX_FOCUS_MINUTES} min) and short break "
        f"({MIN_BREAK_MINUTES} min or more). Every break takes over the screen. "
        f"The long break is the same as in Pomodoro: {LONG_BREAK_MINUTES} min "
        f"after every {POMODOROS_BEFORE_LONG_BREAK} focus blocks."
    ),
}


class SettingsDialog(QDialog):
    def __init__(
        self,
        config: AppConfig,
        parent: Optional[QWidget] = None,
        sound: Optional[AlertSound] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(480)

        self._custom = config.custom
        self._sound = sound or AlertSound(self)
        self._sound_file = config.sound_file

        self._mode_box = QComboBox()
        for mode in Mode:
            self._mode_box.addItem(MODE_NAME[mode], mode)
        self._mode_box.setCurrentIndex(self._mode_box.findData(config.mode))

        self._hint = QLabel()
        self._hint.setObjectName("muted")
        self._hint.setWordWrap(True)

        self._focus = self._make_spin(1, MAX_FOCUS_MINUTES, " min")
        self._short_break = self._make_spin(MIN_BREAK_MINUTES, 120, " min")
        self._long_break = self._make_spin(1, 240, " min")
        self._cycle = self._make_spin(1, 12, " pomodoros")
        self._spins = (self._focus, self._short_break, self._long_break, self._cycle)

        form = QFormLayout()
        form.setVerticalSpacing(14)
        form.setHorizontalSpacing(20)
        form.addRow("Mode", self._mode_box)
        form.addRow("Focus", self._focus)
        form.addRow("Short break", self._short_break)
        form.addRow("Long break", self._long_break)
        form.addRow("Long break after", self._cycle)

        self._sound_check = QCheckBox(
            "Play a sound when a focus block or a break ends"
        )
        self._sound_check.setChecked(config.sound_enabled)
        self._sound_label = QLabel()
        self._sound_label.setObjectName("muted")
        self._sound_label.setWordWrap(True)
        self._choose_button = QPushButton("Choose...")
        self._default_button = QPushButton("Default")
        self._test_button = QPushButton("Test")
        sound_buttons = QHBoxLayout()
        for button in (self._choose_button, self._default_button, self._test_button):
            sound_buttons.addWidget(button)
        self._choose_button.clicked.connect(self._on_choose_sound)
        self._default_button.clicked.connect(self._on_default_sound)
        self._test_button.clicked.connect(self._on_test_sound)
        self._refresh_sound_label()

        ideas_label = QLabel(
            "Your own long-break ideas (one per line). "
            "They are mixed in with the built-in ones."
        )
        ideas_label.setObjectName("muted")
        ideas_label.setWordWrap(True)
        self._ideas_edit = QPlainTextEdit()
        self._ideas_edit.setPlaceholderText(
            "For example:\nPaint a small rock\nPlay the guitar for ten minutes"
        )
        self._ideas_edit.setMinimumHeight(90)
        self._ideas_edit.setPlainText(ideas_to_text(config.ideas))

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        # Everything except Save and Cancel scrolls, so the window never gets
        # taller than a small screen and the buttons stay in sight.
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(28, 24, 28, 12)
        layout.setSpacing(16)
        layout.addLayout(form)
        layout.addWidget(self._hint)
        layout.addWidget(self._sound_check)
        layout.addWidget(self._sound_label)
        layout.addLayout(sound_buttons)
        layout.addWidget(ideas_label)
        layout.addWidget(self._ideas_edit)

        self._scroll = QScrollArea()
        self._scroll.setWidget(content)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._content = content

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._scroll, stretch=1)
        buttons_row = QHBoxLayout()
        buttons_row.setContentsMargins(28, 8, 28, 20)
        buttons_row.addStretch(1)
        buttons_row.addWidget(buttons)
        root.addLayout(buttons_row)

        self._mode_box.currentIndexChanged.connect(self._on_mode_changed)
        for spin in self._spins:
            spin.valueChanged.connect(self._on_value_changed)
        self._on_mode_changed()

    @staticmethod
    def _make_spin(low: int, high: int, suffix: str) -> QSpinBox:
        spin = QSpinBox()
        spin.setRange(low, high)
        spin.setSuffix(suffix)
        return spin

    # ----- reacting to the user -------------------------------------------

    def _current_mode(self) -> Mode:
        return self._mode_box.currentData()

    def _on_mode_changed(self) -> None:
        mode = self._current_mode()
        if mode is Mode.CUSTOM:
            self._show(self._custom, editable=True)
        else:
            self._show(PRESETS[mode], editable=False)
        self._hint.setText(MODE_HINT[mode])

    def _on_value_changed(self) -> None:
        if self._current_mode() is Mode.CUSTOM:
            self._custom = TimerSettings(
                focus_minutes=self._focus.value(),
                short_break_minutes=self._short_break.value(),
                long_break_minutes=self._long_break.value(),
                pomodoros_before_long_break=self._cycle.value(),
            )

    def _show(self, settings: TimerSettings, editable: bool) -> None:
        values = (
            settings.focus_minutes,
            settings.short_break_minutes,
            settings.long_break_minutes,
            settings.pomodoros_before_long_break,
        )
        for spin, value in zip(self._spins, values):
            spin.blockSignals(True)
            spin.setValue(value)
            spin.blockSignals(False)
            spin.setEnabled(editable)
        # The long break is common to every mode, so it can be seen but never
        # changed, not even in Custom.
        self._long_break.setEnabled(False)
        self._cycle.setEnabled(False)

    def showEvent(self, event) -> None:
        """Fit the window to its content, but keep it inside the screen."""
        super().showEvent(event)
        screen = self.screen() or QGuiApplication.primaryScreen()
        if screen is None:
            return
        wanted = self._content.sizeHint().height() + self._buttons_height()
        limit = int(screen.availableGeometry().height() * 0.9)
        self.resize(self.width(), min(wanted, limit))

    def _buttons_height(self) -> int:
        return 84  # the Save and Cancel row, with its margins

    # ----- the alert sound -------------------------------------------------

    def _refresh_sound_label(self) -> None:
        if not self._sound_file:
            self._sound_label.setText("Sound: the default chime")
            return
        name = Path(self._sound_file).name
        error = check_sound_file(self._sound_file)
        if error:
            self._sound_label.setText(
                f"Sound: {name}. {error} The default chime is used instead."
            )
        else:
            self._sound_label.setText(f"Sound: {name}")

    def use_sound_file(self, path: str) -> Optional[str]:
        """Use your own sound. Gives None if it was accepted, or a short
        message if it cannot be used (the old sound stays then)."""
        error = check_sound_file(path)
        if error:
            self._sound_label.setText(f"Sound not changed. {error}")
            return error
        self._sound_file = path
        self._refresh_sound_label()
        return None

    def _on_choose_sound(self) -> None:
        start = str(Path(self._sound_file).parent) if self._sound_file else ""
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose a sound", start, "WAV sound (*.wav)"
        )
        if path:
            self.use_sound_file(path)

    def _on_default_sound(self) -> None:
        self._sound_file = ""
        self._refresh_sound_label()

    def _on_test_sound(self) -> None:
        """Play the chosen sound now, even if the sound is switched off."""
        if not self._sound.available:
            self._sound_label.setText("Sounds can only be played on Windows.")
            return
        self._sound.play(self._sound_file)

    # ----- result ----------------------------------------------------------

    def result_config(self) -> AppConfig:
        """The settings the user chose. Use after the dialog was accepted."""
        return AppConfig(
            mode=self._current_mode(),
            custom=self._custom,
            ideas=ideas_from_text(self._ideas_edit.toPlainText()),
            sound_enabled=self._sound_check.isChecked(),
            sound_file=self._sound_file,
        )
