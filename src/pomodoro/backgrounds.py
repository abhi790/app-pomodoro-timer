"""Finds the background pictures for the Force Break screen.

No windows here, so it is easy to test. The pictures live in folders named
after the tip categories:

    src/pomodoro/assets/backgrounds/water/water_01.jpg
    src/pomodoro/assets/backgrounds/water/water_02.jpg
    src/pomodoro/assets/backgrounds/food/food_01.jpg
    ...

``BackgroundPicker`` hands out one picture per tip, shuffled, never the same
picture twice in a row. If a category has no pictures, it returns None and the
break screen shows a plain colored background instead, so the app always works.
"""

import random
from collections import deque
from pathlib import Path
from typing import Optional

IMAGE_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp")


def default_folder() -> Path:
    """The folder that holds one sub-folder per category."""
    return Path(__file__).resolve().parent / "assets" / "backgrounds"


def find_images(category: str, folder: Optional[Path] = None) -> list:
    """All pictures for a category, sorted by name. Empty if there are none."""
    category_folder = (folder or default_folder()) / category
    if not category_folder.is_dir():
        return []
    return sorted(
        path
        for path in category_folder.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )


class BackgroundPicker:
    """Gives the next picture for a category each time ``pick()`` is called."""

    def __init__(
        self,
        folder: Optional[Path] = None,
        rng: Optional[random.Random] = None,
    ) -> None:
        self._folder = folder
        self._rng = rng or random.Random()
        self._queues: dict = {}
        self._last: dict = {}

    def pick(self, category: str) -> Optional[Path]:
        queue = self._queues.get(category)
        if not queue:
            queue = self._refill(category)
            self._queues[category] = queue
        if not queue:
            return None
        path = queue.popleft()
        self._last[category] = path
        return path

    def _refill(self, category: str) -> deque:
        images = find_images(category, self._folder)
        self._rng.shuffle(images)
        # Do not start a new round with the picture we just showed.
        if len(images) > 1 and images[0] == self._last.get(category):
            images[0], images[-1] = images[-1], images[0]
        return deque(images)
