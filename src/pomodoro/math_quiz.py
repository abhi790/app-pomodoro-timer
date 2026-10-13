"""Math problems for leaving a break early (and for stopping a focus block).

No windows here, so it is easy to test. A problem is easy for a rested mind
but needs a moment of thought, so nobody solves one by reflex. There are three
levels. The level goes up with every unlock you use in a day, so the first
problem of the day is the lightest and the third is the hardest:

* Level 1: two additions (or one subtraction)   47 + 38 + 25     60 + 25 - 18
* Level 2: two multiplications                  4 x 6 x 7        7 x 8 + 6 x 4
* Level 3: a mix, with brackets, 3 or more signs (12 + 8) x 5 - 9   20 + 6 x 7 - 9

"x" is the times sign (the real sign is used on the screen). Times is worked
out before plus and minus, like in school. The answer is always a whole number
from 1 up and at most a few hundred, and no step on the way goes below zero.
"""

import random
from dataclasses import dataclass
from typing import Callable, List, Optional

MAX_LEVEL = 3
TIMES = "\u00d7"  # the times sign


@dataclass(frozen=True)
class Problem:
    text: str  # what is shown, like "47 + 38 + 25"
    answer: int


def is_correct(problem: Problem, typed: str) -> bool:
    """True if the typed text is the whole number that solves the problem.

    Spaces around the number are ignored. Anything that is not plain digits
    (empty, letters, decimals, signs, underscores) is simply wrong.
    """
    text = typed.strip()
    if not (text.isascii() and text.isdigit()):
        return False
    return int(text) == problem.answer


def level_for_unlock(math_used: int) -> int:
    """The level of the next problem, when ``math_used`` unlocks are already
    used today: 0 used gives level 1, 1 used gives 2, and 2 or more give 3."""
    return min(max(int(math_used), 0) + 1, MAX_LEVEL)


class ProblemMaker:
    """Makes a new problem each time. Never the same one twice in a row."""

    def __init__(self, rng: Optional[random.Random] = None) -> None:
        self._rng = rng or random.Random()
        self._last: Optional[str] = None
        self._makers: List[List[Callable[[], Problem]]] = [
            [self._add_add, self._add_add, self._add_sub, self._sub_add],  # level 1
            [self._times_times, self._times_plus_times, self._times_minus_times],  # 2
            [  # level 3
                self._brackets_times_minus,
                self._brackets_times_minus,
                self._plus_times_minus,
                self._times_plus_times_plus,
                self._brackets_minus_times_plus,
            ],
        ]

    def next_problem(self, level: int = 1) -> Problem:
        """A new problem of this level (1 to 3; anything else is the nearest)."""
        level = min(max(int(level), 1), MAX_LEVEL)
        while True:
            problem = self._rng.choice(self._makers[level - 1])()
            if problem.text != self._last:
                self._last = problem.text
                return problem

    # ----- level 1: two additions (or a subtraction) ---------------------------

    def _add_add(self) -> Problem:
        a, b, c = (self._rng.randint(10, 60) for _ in range(3))
        return Problem(f"{a} + {b} + {c}", a + b + c)

    def _add_sub(self) -> Problem:
        a, b = self._rng.randint(20, 70), self._rng.randint(10, 50)
        c = self._rng.randint(10, min(a + b - 1, 60))
        return Problem(f"{a} + {b} - {c}", a + b - c)

    def _sub_add(self) -> Problem:
        a = self._rng.randint(30, 99)
        b = self._rng.randint(10, a - 1)
        c = self._rng.randint(10, 60)
        return Problem(f"{a} - {b} + {c}", a - b + c)

    # ----- level 2: two multiplications ---------------------------------------

    def _times_times(self) -> Problem:
        a, b, c = self._rng.randint(3, 9), self._rng.randint(3, 9), self._rng.randint(2, 5)
        return Problem(f"{a} {TIMES} {b} {TIMES} {c}", a * b * c)

    def _times_plus_times(self) -> Problem:
        a, b, c, d = (self._rng.randint(3, 12) for _ in range(4))
        return Problem(f"{a} {TIMES} {b} + {c} {TIMES} {d}", a * b + c * d)

    def _times_minus_times(self) -> Problem:
        a, b, c, d = (self._rng.randint(3, 12) for _ in range(4))
        if a * b <= c * d:  # keep the answer above zero
            a, b, c, d = c, d, a, b
        if a * b == c * d:
            a += 1
        return Problem(f"{a} {TIMES} {b} - {c} {TIMES} {d}", a * b - c * d)

    # ----- level 3: a mix, with brackets --------------------------------------

    def _brackets_times_minus(self) -> Problem:
        a, b, c = self._rng.randint(5, 30), self._rng.randint(5, 30), self._rng.randint(3, 9)
        d = self._rng.randint(2, min((a + b) * c - 1, 40))
        return Problem(f"({a} + {b}) {TIMES} {c} - {d}", (a + b) * c - d)

    def _plus_times_minus(self) -> Problem:
        a, b, c = self._rng.randint(10, 40), self._rng.randint(3, 9), self._rng.randint(3, 9)
        d = self._rng.randint(2, min(a + b * c - 1, 30))
        return Problem(f"{a} + {b} {TIMES} {c} - {d}", a + b * c - d)

    def _times_plus_times_plus(self) -> Problem:
        a, b, c, d = (self._rng.randint(3, 9) for _ in range(4))
        e = self._rng.randint(5, 30)
        return Problem(f"{a} {TIMES} {b} + {c} {TIMES} {d} + {e}", a * b + c * d + e)

    def _brackets_minus_times_plus(self) -> Problem:
        a = self._rng.randint(15, 40)
        b = self._rng.randint(3, a - 5)
        c, d = self._rng.randint(3, 9), self._rng.randint(5, 30)
        return Problem(f"({a} - {b}) {TIMES} {c} + {d}", (a - b) * c + d)
