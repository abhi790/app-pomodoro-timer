"""Modes, saved settings and where they are stored.

No windows in this file, so it is easy to test. The user picks a mode:

* Pomodoro: 25 min focus, 5 min short break
* Custom:   your own focus (1 to 45 min) and short break (5 min or more)

Both modes end every focus block with the full-screen break (Force Break), so
there is no "reminder only" mode.

The long break is the same in both modes: 60 minutes, once after every 4 focus
blocks. Custom cannot change it.

Settings files from older versions can name two modes that no longer exist:
"break_reminder" becomes Pomodoro and "force_break" becomes Custom with
45 min focus and a 10 min short break (what Force Break used to be).
"""

import json
import os
from dataclasses import asdict, dataclass, replace
from enum import Enum
from pathlib import Path
from typing import Optional, Tuple

from pomodoro.ideas import clean_ideas
from pomodoro.timer_logic import TimerSettings


class Mode(Enum):
    POMODORO = "pomodoro"
    CUSTOM = "custom"


# Limits for the Custom timer: a focus block is at most 45 minutes (longer is
# not focus any more) and a short break is at least 5 minutes.
MAX_FOCUS_MINUTES = 45
MIN_BREAK_MINUTES = 5

# The long break is common to every mode: once after every 4 focus blocks.
LONG_BREAK_MINUTES = 60
POMODOROS_BEFORE_LONG_BREAK = 4


def limit_custom(settings: TimerSettings) -> TimerSettings:
    """Bring Custom times inside the limits.

    Focus is cut to 45 minutes, the short break is raised to 5 minutes, and the
    long break is the common one (60 minutes after 4 focus blocks). Old
    settings files from before these limits are fixed this way when loaded.
    """
    return replace(
        settings,
        focus_minutes=min(settings.focus_minutes, MAX_FOCUS_MINUTES),
        short_break_minutes=max(settings.short_break_minutes, MIN_BREAK_MINUTES),
        long_break_minutes=LONG_BREAK_MINUTES,
        pomodoros_before_long_break=POMODOROS_BEFORE_LONG_BREAK,
    )


MODE_NAME = {
    Mode.POMODORO: "Pomodoro",
    Mode.CUSTOM: "Custom Timer",
}

PRESETS = {
    Mode.POMODORO: TimerSettings(
        focus_minutes=25,
        short_break_minutes=5,
        long_break_minutes=60,
        pomodoros_before_long_break=4,
    ),
}

# What the old Force Break mode used to be (see the top of this file).
_OLD_FORCE_BREAK_CUSTOM = TimerSettings(focus_minutes=45, short_break_minutes=10)


@dataclass(frozen=True)
class AppConfig:
    """Everything the app remembers between runs."""

    mode: Mode = Mode.CUSTOM
    custom: TimerSettings = TimerSettings()
    # The user's own long-break ideas, added to the built-in ones.
    ideas: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        # Custom times always stay inside the limits, whoever built the config.
        object.__setattr__(self, "custom", limit_custom(self.custom))

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
        fine: they just have no ideas of your own. The two old modes are
        converted (see the top of this file)."""
        name = data["mode"]
        custom = TimerSettings(**data["custom"])
        if name == "break_reminder":
            mode = Mode.POMODORO
        elif name == "force_break":
            mode, custom = Mode.CUSTOM, _OLD_FORCE_BREAK_CUSTOM
        else:
            mode = Mode(name)
        return cls(
            mode=mode,
            custom=custom,
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
