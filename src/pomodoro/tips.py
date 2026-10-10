"""Healthy tips shown on the Force Break screen.

No windows here, so it is easy to test. ``TipRotator`` hands out the tips one
by one in a shuffled order, never showing the same tip twice in a row.
"""

import random
from typing import Optional

HEALTHY_TIPS = (
    "Drink a glass of water.",
    "Stretch your neck slowly: tilt left, then right.",
    "Roll your shoulders back ten times.",
    "20-20-20 rule: look at something 20 feet away for 20 seconds.",
    "Stand up and walk around for a few minutes.",
    "Take five slow, deep breaths.",
    "Check your posture: back straight, shoulders relaxed.",
    "Close your eyes and rest them for a moment.",
    "Shake out your hands and stretch your wrists.",
    "Look out of a window and let your eyes relax.",
)

# How long each tip stays on screen.
TIP_SECONDS = 12


class TipRotator:
    """Gives the next tip each time ``next_tip()`` is called."""

    def __init__(
        self,
        tips: tuple = HEALTHY_TIPS,
        rng: Optional[random.Random] = None,
    ) -> None:
        if not tips:
            raise ValueError("tips must not be empty")
        self._tips = tuple(tips)
        self._rng = rng or random.Random()
        self._queue: list = []
        self._last: Optional[str] = None

    def next_tip(self) -> str:
        if not self._queue:
            self._refill()
        tip = self._queue.pop()
        self._last = tip
        return tip

    def _refill(self) -> None:
        order = list(self._tips)
        self._rng.shuffle(order)
        # The queue is read from the end, so the next tip is order[-1].
        # Make sure it is not the tip we just showed.
        if len(order) > 1 and order[-1] == self._last:
            order[0], order[-1] = order[-1], order[0]
        self._queue = order
