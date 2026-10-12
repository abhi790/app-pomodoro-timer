"""Picks a font size so that a text fits in a box, without any windows.

How tall a text is depends on the font, and the font differs from one
computer to the next (and with the Windows display scale). So the pause screen
does not trust a fixed size: it asks "how tall would the tip be at this size?"
and takes the biggest size from a short list that fits the box.
"""

from typing import Callable, Sequence

# Biggest first. The first size is the normal look; the others are only used
# when a long tip would not fit on a small screen or with a tall font.
TIP_FONT_SIZES = (36, 32, 29, 26, 24)


def pick_font_px(
    height_at: Callable[[int], int],
    max_height: int,
    sizes: Sequence[int] = TIP_FONT_SIZES,
) -> int:
    """The biggest size whose text is at most ``max_height`` tall.

    ``height_at(px)`` says how tall the text is at that font size. If even the
    smallest size is too tall, the smallest size is used (it is the best we
    can do).
    """
    for size in sizes:
        if height_at(size) <= max_height:
            return size
    return sizes[-1]
