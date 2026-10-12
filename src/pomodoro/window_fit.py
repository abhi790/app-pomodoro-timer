"""Keeps a window inside the usable part of the screen, without any windows.

The usable part (Qt calls it ``availableGeometry``) does not include the
taskbar. A tall window that starts near the bottom would hang below the
taskbar, and its Save button could not be reached, even with a scroll bar
inside the window. ``fit_in_area`` makes the window smaller if needed and then
moves it so that the whole window, title bar included, is inside the area.

All numbers are pixels. A rectangle is ``(x, y, width, height)``.
"""

from typing import Tuple

Rect = Tuple[int, int, int, int]

# Space left free around the window, so it never touches the screen edge or
# the taskbar.
EDGE_MARGIN = 12


def fit_in_area(
    wanted_size: Tuple[int, int],
    frame_extra: Tuple[int, int],
    area: Rect,
    preferred_center: Tuple[int, int],
    margin: int = EDGE_MARGIN,
) -> Rect:
    """Where to put a window so that all of it is on screen.

    ``wanted_size`` is the size the content would like (without the title bar
    and borders). ``frame_extra`` is how much the title bar and borders add to
    the width and the height. ``preferred_center`` is where the window would
    like to be centered (usually the middle of the main window).

    Gives ``(x, y, width, height)``: ``x`` and ``y`` are the top-left corner of
    the whole window (with its title bar), ``width`` and ``height`` are the
    size of the inside. The inside is made smaller if the screen is too small
    for the wanted size, never bigger.
    """
    wanted_width, wanted_height = wanted_size
    extra_width, extra_height = frame_extra
    area_x, area_y, area_width, area_height = area

    usable_width = max(1, area_width - 2 * margin)
    usable_height = max(1, area_height - 2 * margin)

    width = max(1, min(wanted_width, usable_width - extra_width))
    height = max(1, min(wanted_height, usable_height - extra_height))
    total_width = width + extra_width
    total_height = height + extra_height

    x = preferred_center[0] - total_width // 2
    y = preferred_center[1] - total_height // 2

    low_x = area_x + margin
    high_x = area_x + area_width - margin - total_width
    low_y = area_y + margin
    high_y = area_y + area_height - margin - total_height
    x = min(max(x, low_x), max(low_x, high_x))
    y = min(max(y, low_y), max(low_y, high_y))
    return x, y, width, height
