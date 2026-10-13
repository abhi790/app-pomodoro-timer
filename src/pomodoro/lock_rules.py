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


# TESTING ONLY. While the app is still being tested, the break screen and the
# pause screen have an "Emergency exit" button that leaves at once, with no
# math problem and no daily count, so a tester can never get stuck. Set this to
# False before a real release and the buttons are gone (nothing else to change).
EMERGENCY_EXIT_ENABLED = True


def emergency_exit_visible() -> bool:
    """True if the break and pause screens should offer the Emergency exit."""
    return EMERGENCY_EXIT_ENABLED


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
