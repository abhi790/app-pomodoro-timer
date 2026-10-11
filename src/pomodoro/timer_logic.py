"""Timer logic for the Pomodoro app.

This file knows nothing about windows, buttons or sound. It only keeps track
of time and decides what comes next. That makes it easy to test and easy to
change without touching the user interface.

The cycle looks like this (with the default settings):

    Focus 30 min -> Short break 5 min -> Focus -> Short break -> Focus ->
    Short break -> Focus -> LONG break 60 min -> back to Focus ...
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Phase(Enum):
    """The three kinds of time block."""

    FOCUS = "focus"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"


@dataclass(frozen=True)
class TimerSettings:
    """User-customizable times. All durations are in minutes."""

    focus_minutes: int = 30
    short_break_minutes: int = 5
    long_break_minutes: int = 60
    pomodoros_before_long_break: int = 4

    def __post_init__(self) -> None:
        for name in (
            "focus_minutes",
            "short_break_minutes",
            "long_break_minutes",
            "pomodoros_before_long_break",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise ValueError(f"{name} must be a whole number of at least 1")

    def duration_seconds(self, phase: Phase) -> int:
        """Length of the given phase in seconds."""
        minutes = {
            Phase.FOCUS: self.focus_minutes,
            Phase.SHORT_BREAK: self.short_break_minutes,
            Phase.LONG_BREAK: self.long_break_minutes,
        }[phase]
        return minutes * 60


class PomodoroTimer:
    """A countdown that moves through focus and break phases.

    The timer does not read the clock by itself. Whoever uses it (the window
    later on) calls ``tick()`` once per second while the timer is running.
    """

    def __init__(self, settings: Optional[TimerSettings] = None) -> None:
        self._settings = settings or TimerSettings()
        self.reset()

    # ----- read-only state -------------------------------------------------

    @property
    def settings(self) -> TimerSettings:
        return self._settings

    @property
    def phase(self) -> Phase:
        return self._phase

    @property
    def remaining_seconds(self) -> int:
        return self._remaining

    @property
    def running(self) -> bool:
        return self._running

    @property
    def completed_pomodoros(self) -> int:
        """How many focus blocks were finished since the last reset."""
        return self._completed

    # ----- controls --------------------------------------------------------

    def start(self) -> None:
        self._running = True

    def pause(self) -> None:
        self._running = False

    def reset(self) -> None:
        """Back to a fresh first focus block, stopped, count at zero."""
        self._phase = Phase.FOCUS
        self._remaining = self._settings.duration_seconds(Phase.FOCUS)
        self._running = False
        self._completed = 0

    def skip(self) -> None:
        """Jump to the next phase without counting the skipped one as done."""
        self._running = False
        self._go_to_next_phase(count_focus=False)

    def abandon_focus(self) -> None:
        """Give up the current focus block (Stop on the pause screen).

        Like the classic Pomodoro rule, an interrupted pomodoro does not count:
        the timer goes back to a fresh, stopped focus block. Pomodoros that
        were already finished stay counted. Does nothing during a break.
        """
        if self._phase is not Phase.FOCUS:
            return
        self._running = False
        self._remaining = self._settings.duration_seconds(Phase.FOCUS)

    def limit_remaining(self, seconds: int) -> None:
        """Make the current block end sooner.

        If more than ``seconds`` are left, only ``seconds`` are left. It never
        makes the block longer. (The Important button uses this to cut a break
        down to 3 minutes.)
        """
        self._remaining = min(self._remaining, max(1, seconds))

    def update_settings(self, settings: TimerSettings) -> None:
        """Use new times. If the timer is stopped, the current phase restarts
        with its new length. A running phase keeps its remaining time."""
        self._settings = settings
        if not self._running:
            self._remaining = settings.duration_seconds(self._phase)

    # ----- time ------------------------------------------------------------

    def tick(self, seconds: int = 1) -> Optional[Phase]:
        """Move time forward.

        Returns the phase that just finished, or None if nothing finished.
        When a phase finishes, the timer moves to the next phase and stops,
        so the app can notify the user and wait for them to press Start.
        """
        if not self._running or seconds < 1:
            return None

        self._remaining -= seconds
        if self._remaining > 0:
            return None

        finished = self._phase
        self._running = False
        self._go_to_next_phase(count_focus=True)
        return finished

    # ----- internals -------------------------------------------------------

    def _go_to_next_phase(self, count_focus: bool) -> None:
        if self._phase is Phase.FOCUS:
            if count_focus:
                self._completed += 1
            long_break_due = (
                count_focus
                and self._completed % self._settings.pomodoros_before_long_break == 0
            )
            self._phase = Phase.LONG_BREAK if long_break_due else Phase.SHORT_BREAK
        else:
            self._phase = Phase.FOCUS
        self._remaining = self._settings.duration_seconds(self._phase)
