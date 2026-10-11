"""What is locked while the timer works, without any windows (easy to test).

A real Pomodoro is not something you fiddle with halfway. So:

* While the timer is running, Reset and Settings are locked.
* Pause does not just stop the clock. It covers the screens with the pause
  screen, where you choose Run (carry on) or Stop (give the block up, after a
  math problem). While that screen is up, everything else stays locked too.
* Stop needs a math problem, and it uses one of the 3 daily math unlocks (the
  same ones that end a break early). With none left, Stop is not offered: you
  can only Run.
* During a Force Break everything is locked, as before.
"""


def controls_enabled(
    running: bool, break_active: bool, pause_cover_active: bool
) -> bool:
    """True if Reset and Settings may be used right now.

    They are available only when the timer is stopped and no break screen or
    pause screen is up.
    """
    return not (running or break_active or pause_cover_active)


def can_stop(math_left: int) -> bool:
    """Stop (leaving a focus block early) needs a math unlock to spend."""
    return math_left > 0
