"""The settings window: pick a mode and, for Custom, set your own times."""

from typing import Optional

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from pomodoro.settings import MODE_NAME, PRESETS, AppConfig, Mode
from pomodoro.timer_logic import TimerSettings

MODE_HINT = {
    Mode.BREAK_REMINDER: "A gentle reminder when it is time to rest.",
    Mode.FORCE_BREAK: (
        "Breaks take over the screen. The full-screen break is coming in a "
        "later step; for now this mode only sets the times."
    ),
    Mode.CUSTOM: "Set your own times below.",
}


class SettingsDialog(QDialog):
    def __init__(self, config: AppConfig, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(360)

        self._custom = config.custom

        self._mode_box = QComboBox()
        for mode in Mode:
            self._mode_box.addItem(MODE_NAME[mode], mode)
        self._mode_box.setCurrentIndex(self._mode_box.findData(config.mode))

        self._hint = QLabel()
        self._hint.setWordWrap(True)

        self._focus = self._make_spin(1, 240, " min")
        self._short_break = self._make_spin(1, 120, " min")
        self._long_break = self._make_spin(1, 240, " min")
        self._cycle = self._make_spin(1, 12, " pomodoros")
        self._spins = (self._focus, self._short_break, self._long_break, self._cycle)

        form = QFormLayout()
        form.addRow("Mode", self._mode_box)
        form.addRow("Focus", self._focus)
        form.addRow("Short break", self._short_break)
        form.addRow("Long break", self._long_break)
        form.addRow("Long break after", self._cycle)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addLayout(form)
        layout.addWidget(self._hint)
        layout.addWidget(buttons)

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

    # ----- result ----------------------------------------------------------

    def result_config(self) -> AppConfig:
        """The settings the user chose. Use after the dialog was accepted."""
        return AppConfig(mode=self._current_mode(), custom=self._custom)
