"""Creative ideas for the long break.

No windows here, so it is easy to test. A long break is the time to do
something fun and creative, not something that feels like studying. This file
holds a list of such ideas and the rules for the ideas you add yourself.

``IdeaRotator`` hands out the ideas one by one in a shuffled order. Every idea
is shown once before any idea comes back, and the same idea never shows twice
in a row.

To add your own ideas, open Settings and write one idea per line in the box
"Your own long-break ideas". They are saved in ``settings.json``. To change the
built-in list, add a line to ``CREATIVE_IDEAS`` below. Keep each idea short,
friendly and something a person can start right away.
"""

import random
from collections import deque
from typing import Iterable, Optional, Sequence

# The longest idea we keep (longer lines are cut), and how many of your own
# ideas we keep. These keep the break screen readable.
MAX_IDEA_LENGTH = 140
MAX_CUSTOM_IDEAS = 100

# Shown above the idea on the break screen.
IDEA_CATEGORY = "creative"
IDEA_TITLE = "Be creative"

CREATIVE_IDEAS = (
    "Sketch the object nearest to you. It does not need to look good.",
    "Doodle for five minutes without lifting your pen from the paper.",
    "Write a short poem about your day. Four lines is plenty.",
    "Pick up an instrument and play anything. No wrong notes allowed.",
    "Hum a tune that comes to mind and keep changing it until it feels new.",
    "Go for a walk and take three photos of things you would normally ignore.",
    "Write a six-word story about something that happened this week.",
    "Make a tiny paper animal. Origami, scissors or just folding all count.",
    "Cook or assemble a snack in a way you have never tried before.",
    "Invent a new word and write down what it means.",
    "Draw a map of an imaginary island. Give the places funny names.",
    "Write a letter to yourself one year from now.",
    "Dance to a song you love, all the way to the end.",
    "Sketch the view outside your window using only simple shapes.",
    "Make up a short story starring three things on your desk.",
    "Choose a color and find five things around you in that color.",
    "Build something from whatever is nearby: paper clips, cups, books or blocks.",
    "Write a thank-you note to someone who helped you recently.",
    "Try to draw your own hand without looking at the paper.",
    "Sing in the shower, the kitchen or the balcony. Nobody is judging.",
    "Rearrange a shelf or a corner of your room to make it feel new.",
    "Write down ten silly names for a pet you may never have.",
    "Take a different route on your walk and notice what is new.",
    "Make a playlist for a mood you would like to have tomorrow.",
    "Draw a comic strip with three panels about your morning.",
    "Take a photo of a shadow and give it a title.",
    "Write a menu for an imaginary restaurant with funny dishes.",
    "Learn to fold a paper plane that flies better than your last one.",
    "Bake, stir or chop something simple. Making food with your hands is relaxing.",
    "Tell a joke or a funny story to someone you like.",
    "Water a plant and sketch one of its leaves.",
    "Sit by a window and describe the scene in a few lines, like a writer.",
    "Make a small collage from old papers, magazines or leaflets.",
    "Write a song about something boring, like a spoon or a staircase.",
    "Rewrite the plot of a movie you know with a different ending.",
    "Whittle, knit, braid, weave or tie something. Hands busy, mind free.",
    "Start a doodle, then pass it on or save it and finish it tomorrow.",
    "Imagine your dream room and draw a quick plan of it.",
    "Play a board game, cards or a puzzle with someone, or just by yourself.",
    "Take ten minutes to just play, with no goal and no result needed.",
)


def clean_ideas(lines: Iterable[str]) -> tuple:
    """Tidy up ideas typed by the user.

    Extra spaces are squeezed, empty lines are dropped, long lines are cut to
    ``MAX_IDEA_LENGTH``, repeats (ignoring capital letters) are dropped, and
    at most ``MAX_CUSTOM_IDEAS`` are kept. A single string is not a list of
    ideas, so it raises ``TypeError`` (use ``ideas_from_text`` for that).
    """
    if isinstance(lines, (str, bytes)):
        raise TypeError("ideas must be a list of strings")
    kept: list = []
    seen: set = set()
    for line in lines:
        if not isinstance(line, str):
            raise TypeError("every idea must be a string")
        text = " ".join(line.split())
        if len(text) > MAX_IDEA_LENGTH:
            text = text[:MAX_IDEA_LENGTH].rstrip()
        key = text.casefold()
        if not text or key in seen:
            continue
        seen.add(key)
        kept.append(text)
        if len(kept) >= MAX_CUSTOM_IDEAS:
            break
    return tuple(kept)


def ideas_from_text(text: str) -> tuple:
    """Your ideas from the settings box: one idea per line."""
    return clean_ideas(text.splitlines())


def ideas_to_text(ideas: Sequence[str]) -> str:
    """Your ideas as text for the settings box: one idea per line."""
    return "\n".join(ideas)


class IdeaRotator:
    """Gives the next idea each time ``next_idea()`` is called.

    The built-in ideas and your own are mixed together. Each round shows every
    idea once, in a new shuffled order.
    """

    def __init__(
        self,
        custom: Sequence[str] = (),
        ideas: Sequence[str] = CREATIVE_IDEAS,
        rng: Optional[random.Random] = None,
    ) -> None:
        pool = list(ideas)
        known = {idea.casefold() for idea in pool}
        for idea in clean_ideas(custom):
            if idea.casefold() not in known:
                known.add(idea.casefold())
                pool.append(idea)
        if not pool:
            raise ValueError("ideas must not be empty")
        self._ideas = tuple(pool)
        self._rng = rng or random.Random()
        self._queue: deque = deque()
        self._last: Optional[str] = None

    def next_idea(self) -> str:
        if not self._queue:
            self._refill()
        idea = self._queue.popleft()
        self._last = idea
        return idea

    def _refill(self) -> None:
        order = list(self._ideas)
        self._rng.shuffle(order)
        # Do not start the new round with the idea we just showed.
        if len(order) > 1 and order[0] == self._last:
            order[0], order[-1] = order[-1], order[0]
        self._queue = deque(order)
