"""The "Emergency exit" button of the testing phase.

It sits on the break screen and on the pause screen, and leaves at once: no math
problem, no daily count, no questions. It exists only so that a tester can never
get stuck while the app is being tested. ``EMERGENCY_EXIT_ENABLED`` in
``lock_rules.py`` switches it off for a real release.

The button floats in the bottom right corner of the screen instead of sitting in
the layout, so it never makes a screen taller (a small laptop screen has exactly
the room it had before).

This file only makes and places the button. What happens when it is pressed is
decided by the main window.
"""

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QWidget

from pomodoro.lock_rules import emergency_exit_visible

EMERGENCY_TEXT = "Emergency exit (testing only)"
CORNER_MARGIN = 24


def make_emergency_button(parent: QWidget) -> Optional[QPushButton]:
    """A new Emergency exit button on ``parent``, or None when the testing flag
    is off."""
    if not emergency_exit_visible():
        return None
    button = QPushButton(EMERGENCY_TEXT, parent)
    button.setObjectName("emergencyExit")  # see theme.py
    button.setMinimumHeight(40)
    button.setCursor(Qt.PointingHandCursor)
    button.adjustSize()
    return button


def place_in_corner(button: Optional[QPushButton], parent: QWidget) -> None:
    """Put the button in the bottom right corner of ``parent`` (does nothing
    when there is no button). Call it every time ``parent`` changes size."""
    if button is None:
        return
    button.adjustSize()
    x = max(0, parent.width() - button.width() - CORNER_MARGIN)
    y = max(0, parent.height() - button.height() - CORNER_MARGIN)
    button.move(x, y)
    button.raise_()
