"""The rules for the tray icon, without any windows (easy to test).

The app lives in the system tray (the little icons next to the clock):

* hovering over the icon shows the time left, like "Focus 24:59"
* pressing the window's close button hides the window to the tray, the timer
  keeps running
* the tray menu has "Quit", which really closes the app. Quit is not allowed
  during a Force Break or while the pause screen is up (see ``lock_rules.py``).
* if this computer has no system tray, close works the old way (the app quits),
  so the window can never disappear with no way to bring it back
"""

APP_NAME = "Pomodoro Timer"

# What the close button does.
HIDE = "hide"
QUIT = "quit"


def tray_tooltip(phase_name: str, clock: str, running: bool) -> str:
    """The text shown when the mouse is over the tray icon.

    A running timer shows "Focus 24:59". A stopped one adds "(paused)", so you
    can tell at a glance that the time is not moving.
    """
    text = f"{phase_name} {clock}"
    if not running:
        text += " (paused)"
    return f"{APP_NAME}\n{text}"


def close_action(tray_available: bool, quitting: bool) -> str:
    """What to do when the window's close button is pressed.

    Hide to the tray, unless the tray is missing or the app is already being
    closed on purpose (the tray's Quit).
    """
    if quitting or not tray_available:
        return QUIT
    return HIDE


def can_quit(break_active: bool, pause_cover_active: bool = False) -> bool:
    """Quit from the tray is not allowed while a Force Break or the pause
    screen is on (they would be a way around the rules)."""
    return not (break_active or pause_cover_active)
