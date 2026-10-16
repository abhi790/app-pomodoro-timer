"""What is locked while the timer works, without any windows (easy to test).

A real Pomodoro is not something you fiddle with halfway. So:

* While the timer is running, Settings is locked. (There is no Reset button
  any more: the count of finished pomodoros resets itself once the long
  break ends, see ``timer_logic.py``.)
* Pause does not just stop the clock. It covers the screens with the pause
  screen, where you choose Run (carry on) or Stop (give the block up, after a
  math problem). While that screen is up, everything else stays locked too.
* Stop always needs a math problem first, every time, with no daily cap: solve
  it and the pause screen closes, however many times that happens in a day.
* During a Force Break everything is locked, as before. Leaving a break early
  works the same way: there is no cap on how many times a day you can solve
  the math problem to end a break or stop a focus block.
"""


# TESTING ONLY. While the app is still being tested, the break screen and the
# pause screen have an "Emergency exit" button that leaves at once, with no
# math problem and no daily count, so a tester can never get stuck. Set this to
# False before a real release and the buttons are gone (nothing else to change).
EMERGENCY_EXIT_ENABLED = True


def emergency_exit_visible() -> bool:
    """True if the break and pause screens should offer the Emergency exit."""
    return EMERGENCY_EXIT_ENABLED


def settings_enabled(
    running: bool, break_active: bool, pause_cover_active: bool
) -> bool:
    """True if Settings may be opened right now.

    Only when the timer is stopped and no break screen or pause screen is up.
    """
    return not (running or break_active or pause_cover_active)
