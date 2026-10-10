"""Simple math problems for leaving a break early.

No windows here, so it is easy to test. The problems are easy for a rested
mind but need a moment of thought, so nobody solves one by reflex:

* adding two numbers from 10 to 99          (47 + 38)
* taking a smaller number from a bigger one (83 - 29)
* times tables from 3 to 12                 (7 x 8)

The answer is always a whole number, never negative.
"""

import random
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Problem:
    text: str  # what is shown, like "47 + 38"
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


class ProblemMaker:
    """Makes a new problem each time. Never the same one twice in a row."""

    def __init__(self, rng: Optional[random.Random] = None) -> None:
        self._rng = rng or random.Random()
        self._last: Optional[str] = None

    def next_problem(self) -> Problem:
        while True:
            problem = self._make()
            if problem.text != self._last:
                self._last = problem.text
                return problem

    def _make(self) -> Problem:
        kind = self._rng.choice(("add", "subtract", "multiply"))
        if kind == "add":
            a, b = self._rng.randint(10, 99), self._rng.randint(10, 99)
            return Problem(f"{a} + {b}", a + b)
        if kind == "subtract":
            a = self._rng.randint(30, 99)
            b = self._rng.randint(10, a - 1)
            return Problem(f"{a} - {b}", a - b)
        a, b = self._rng.randint(3, 12), self._rng.randint(3, 12)
        return Problem(f"{a} × {b}", a * b)  # × is the times sign
