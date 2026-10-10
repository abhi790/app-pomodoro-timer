"""Modes, saved settings and where they are stored.

No windows in this file, so it is easy to test. The user picks a mode:

* Break Reminder: 25 min focus, 5 min short break
* Force Break:    45 min focus, 10 min short break
* Custom:         any times the user chooses

Every mode has a long break of 60 minutes after 4 pomodoros by default.
"""

import json
import os
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

from pomodoro.ideas import clean_ideas
from pomodoro.timer_logic import TimerSettings


class Mode(Enum):
    BREAK_REMINDER = "break_reminder"
    FORCE_BREAK = "force_break"
    CUSTOM = "custom"


MODE_NAME = {
    Mode.BREAK_REMINDER: "Break Reminder",
    Mode.FORCE_BREAK: "Force Break",
    Mode.CUSTOM: "Custom Timer",
}

PRESETS = {
    Mode.BREAK_REMINDER: TimerSettings(
        focus_minutes=25,
        short_break_minutes=5,
        long_break_minutes=60,
        pomodoros_before_long_break=4,
    ),
    Mode.FORCE_BREAK: TimerSettings(
        focus_minutes=45,
        short_break_minutes=10,
        long_break_minutes=60,
        pomodoros_before_long_break=4,
    ),
}


@dataclass(frozen=True)
class AppConfig:
    """Everything the app remembers between runs."""

    mode: Mode = Mode.CUSTOM
    custom: TimerSettings = TimerSettings()
    # The user's own long-break ideas, added to the built-in ones.
    ideas: Tuple[str, ...] = ()

    def timer_settings(self) -> TimerSettings:
        """The times to use right now, based on the chosen mode."""
        if self.mode is Mode.CUSTOM:
            return self.custom
        return PRESETS[self.mode]

    def to_dict(self) -> dict:
        return {
            "mode": self.mode.value,
            "custom": asdict(self.custom),
            "ideas": list(self.ideas),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppConfig":
        """Build a config from saved data. Raises ValueError, TypeError or
        KeyError if the data is not valid. Older files without ``ideas`` are
        fine: they just have no ideas of your own."""
        return cls(
            mode=Mode(data["mode"]),
            custom=TimerSettings(**data["custom"]),
            ideas=clean_ideas(data.get("ideas", ())),
        )


def config_path() -> Path:
    """Where the settings file lives (``%APPDATA%\\PomodoroTimer`` on Windows)."""
    base = os.environ.get("APPDATA")
    folder = Path(base) if base else Path.home() / ".config"
    return folder / "PomodoroTimer" / "settings.json"


def load_config(path: Optional[Path] = None) -> AppConfig:
    """Read the saved settings. A missing or broken file gives the defaults."""
    path = path or config_path()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return AppConfig.from_dict(data)
    except (OSError, ValueError, TypeError, KeyError):
        return AppConfig()


def save_config(config: AppConfig, path: Optional[Path] = None) -> None:
    """Write the settings to disk, creating the folder if needed."""
    path = path or config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(config.to_dict(), indent=2), encoding="utf-8")
