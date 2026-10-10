"""The daily count of break unlocks, saved in a small file.

No windows here, so it is easy to test. Two numbers are kept for today:

* ``math_used``: how many times a math problem was solved to leave a break
* ``important_used``: how many times the Important button was used

The count starts from zero on a new day (after midnight). It is saved in
``usage.json``, next to ``settings.json``, so closing the app does not give
back the unlocks. The file only says "today"; an old date means a fresh day.

Nothing here is a lock. Anyone can delete the file. It is just a promise to
yourself that is kept by the app.
"""

import json
from dataclasses import asdict, dataclass, replace
from datetime import date
from pathlib import Path
from typing import Callable, Optional

from pomodoro.settings import config_path

# How many times a day a math problem can end a break early.
DAILY_MATH_LIMIT = 3

# With the Important button, the break becomes this long (3 minutes).
IMPORTANT_BREAK_SECONDS = 180


@dataclass(frozen=True)
class DailyUsage:
    day: str  # the date as text, like "2026-10-10"
    math_used: int = 0
    important_used: int = 0


def usage_path() -> Path:
    """Where the count lives (next to ``settings.json``)."""
    return config_path().with_name("usage.json")


def _is_count(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def load_usage(path: Optional[Path], today: str) -> DailyUsage:
    """Read the saved count. A missing, broken or old file gives a fresh day."""
    path = path or usage_path()
    fresh = DailyUsage(day=today)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        usage = DailyUsage(
            day=data["day"],
            math_used=data["math_used"],
            important_used=data["important_used"],
        )
    except (OSError, ValueError, TypeError, KeyError):
        return fresh
    if usage.day != today:
        return fresh
    if not (_is_count(usage.math_used) and _is_count(usage.important_used)):
        return fresh
    return usage


def save_usage(usage: DailyUsage, path: Optional[Path] = None) -> None:
    """Write the count to disk, creating the folder if needed."""
    path = path or usage_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(usage), indent=2), encoding="utf-8")


class UsageTracker:
    """Keeps today's count and saves it every time it changes.

    ``today`` says what day it is (a function returning a ``date``). Tests
    pass their own, so they do not have to wait for midnight.
    """

    def __init__(
        self,
        path: Optional[Path] = None,
        today: Callable[[], date] = date.today,
    ) -> None:
        self._path = path or usage_path()
        self._today = today
        self._usage = load_usage(self._path, self._today_text())

    # ----- read-only state -------------------------------------------------

    @property
    def math_used(self) -> int:
        self._roll_over_if_new_day()
        return self._usage.math_used

    @property
    def math_left(self) -> int:
        return max(0, DAILY_MATH_LIMIT - self.math_used)

    @property
    def important_used(self) -> int:
        self._roll_over_if_new_day()
        return self._usage.important_used

    # ----- changes ---------------------------------------------------------

    def record_math(self) -> None:
        self._roll_over_if_new_day()
        self._usage = replace(self._usage, math_used=self._usage.math_used + 1)
        self._save()

    def record_important(self) -> None:
        self._roll_over_if_new_day()
        self._usage = replace(
            self._usage, important_used=self._usage.important_used + 1
        )
        self._save()

    # ----- internals -------------------------------------------------------

    def _today_text(self) -> str:
        return self._today().isoformat()

    def _roll_over_if_new_day(self) -> None:
        """Midnight passed while the app was open: start the count again."""
        today = self._today_text()
        if self._usage.day != today:
            self._usage = DailyUsage(day=today)

    def _save(self) -> None:
        try:
            save_usage(self._usage, self._path)
        except OSError:
            # The count still works until the app closes. Failing to save
            # must never trap someone on the break screen.
            pass
