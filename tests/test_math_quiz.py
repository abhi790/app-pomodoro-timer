import random
import re
import unittest

from pomodoro.math_quiz import Problem, ProblemMaker, is_correct


def solve(text: str) -> int:
    """Work out a problem text on our own, to check the maker's answer."""
    a, sign, b = re.fullmatch(r"(\d+) (\S) (\d+)", text).groups()
    a, b = int(a), int(b)
    return {"+": a + b, "-": a - b, "×": a * b}[sign]


class IsCorrectTest(unittest.TestCase):
    problem = Problem("47 + 38", 85)

    def test_right_answer(self):
        self.assertTrue(is_correct(self.problem, "85"))

    def test_spaces_around_the_number_are_ignored(self):
        self.assertTrue(is_correct(self.problem, "  85 "))

    def test_wrong_number(self):
        self.assertFalse(is_correct(self.problem, "84"))

    def test_empty_and_letters_are_wrong(self):
        for typed in ("", "   ", "abc", "8 5", "85x", "8_5", "+85", "-85"):
            self.assertFalse(is_correct(self.problem, typed), typed)

    def test_decimals_are_wrong(self):
        self.assertFalse(is_correct(self.problem, "85.0"))


class ProblemMakerTest(unittest.TestCase):
    def test_answers_match_the_text(self):
        maker = ProblemMaker(random.Random(1))
        for _ in range(500):
            problem = maker.next_problem()
            self.assertEqual(problem.answer, solve(problem.text), problem.text)

    def test_answers_are_never_negative(self):
        maker = ProblemMaker(random.Random(2))
        for _ in range(500):
            self.assertGreaterEqual(maker.next_problem().answer, 1)

    def test_all_three_kinds_appear(self):
        maker = ProblemMaker(random.Random(3))
        signs = set()
        for _ in range(200):
            signs.add(maker.next_problem().text.split()[1])
        self.assertEqual(signs, {"+", "-", "×"})

    def test_numbers_stay_small(self):
        maker = ProblemMaker(random.Random(4))
        for _ in range(500):
            problem = maker.next_problem()
            self.assertLessEqual(problem.answer, 198, problem.text)

    def test_never_the_same_problem_twice_in_a_row(self):
        maker = ProblemMaker(random.Random(5))
        texts = [maker.next_problem().text for _ in range(1000)]
        for before, after in zip(texts, texts[1:]):
            self.assertNotEqual(before, after)

    def test_a_new_problem_each_time_has_variety(self):
        maker = ProblemMaker(random.Random(6))
        texts = {maker.next_problem().text for _ in range(100)}
        self.assertGreater(len(texts), 30)


if __name__ == "__main__":
    unittest.main()
