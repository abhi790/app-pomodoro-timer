"""When to show the two Force Break warnings, without any windows (easy to test).

Two things happen before a focus block hands over to its break:

* With **1 minute left**, a small toast appears near the bottom of the
  screen for a couple of seconds and a short sound plays, so you know the
  break is coming.
* With **10 seconds left**, the break screen itself starts sliding up from
  the bottom of the screen, timed to finish covering the screen exactly as
  the focus block ends. There is no separate "the break has now started"
  step: the slide finishing is the break starting.

Both only fire once per focus block. The 1-minute warning only fires for a
block longer than a minute (a 1-minute Custom focus block does not get a
"1 minute left" warning the instant it starts).
"""

ONE_MINUTE_WARNING_SECONDS = 60
SLIDE_IN_SECONDS = 10


def should_show_one_minute_warning(remaining_seconds: int, focus_total_seconds: int) -> bool:
    """True exactly when there is 1 minute left, for a block longer than that."""
    return (
        focus_total_seconds > ONE_MINUTE_WARNING_SECONDS
        and remaining_seconds == ONE_MINUTE_WARNING_SECONDS
    )


def should_start_slide_in(remaining_seconds: int) -> bool:
    """True once the countdown is at 10 seconds or less (and still positive).

    Not just "exactly 10": if the focus block resumes from a pause already
    inside the last 10 seconds, the slide should still start right away (see
    ``begin_slide_in`` in ``break_manager.py``, which times the animation to
    the seconds actually left)."""
    return 0 < remaining_seconds <= SLIDE_IN_SECONDS
