import ast
import random
import re
import unittest

from pomodoro.math_quiz import (
    MAX_LEVEL,
    Problem,
    ProblemMaker,
    is_correct,
    level_for_unlock,
)

ALLOWED = re.compile(r"[0-9 +\-×()]+")


def solve(text: str) -> int:
    """Work out a problem text on our own, to check the maker's answer. It
    understands brackets and "x before +", like school math. Only digits, the
    four signs and brackets are accepted."""
    assert ALLOWED.fullmatch(text), text
    tree = ast.parse(text.replace("×", "*"), mode="eval")
    return _walk(tree.body)


def _walk(node) -> int:
    if isinstance(node, ast.Constant) and isinstance(node.value, int):
        return node.value
    if isinstance(node, ast.BinOp):
        left, right = _walk(node.left), _walk(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
    raise AssertionError(f"not a plain sum: {ast.dump(node)}")


def operators(text: str) -> list:
    """The +, - and × signs of a problem, in order."""
    return re.findall(r"[+\-×]", text)


def numbers(text: str) -> list:
    return [int(n) for n in re.findall(r"\d+", text)]


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


class LevelForUnlockTest(unittest.TestCase):
    def test_the_first_unlock_of_the_day_is_level_one(self):
        self.assertEqual(level_for_unlock(0), 1)

    def test_every_unlock_used_makes_the_next_problem_a_level_harder(self):
        self.assertEqual(level_for_unlock(1), 2)
        self.assertEqual(level_for_unlock(2), 3)

    def test_it_never_goes_above_the_last_level(self):
        self.assertEqual(MAX_LEVEL, 3)
        for used in (3, 4, 10, 1000):
            self.assertEqual(level_for_unlock(used), MAX_LEVEL)

    def test_a_silly_number_is_level_one(self):
        self.assertEqual(level_for_unlock(-5), 1)


class EveryLevelTest(unittest.TestCase):
    """Rules that hold for all levels."""

    def test_answers_match_the_text(self):
        for level in range(1, MAX_LEVEL + 1):
            maker = ProblemMaker(random.Random(level))
            for _ in range(600):
                problem = maker.next_problem(level)
                self.assertEqual(problem.answer, solve(problem.text), problem.text)

    def test_answers_are_whole_numbers_from_1_up(self):
        for level in range(1, MAX_LEVEL + 1):
            maker = ProblemMaker(random.Random(10 + level))
            for _ in range(600):
                problem = maker.next_problem(level)
                self.assertIsInstance(problem.answer, int)
                self.assertGreaterEqual(problem.answer, 1, problem.text)

    def test_the_answer_fits_the_answer_box(self):
        # The box takes at most 6 digits. The answers stay far below that, so
        # they can be worked out in the head.
        for level in range(1, MAX_LEVEL + 1):
            maker = ProblemMaker(random.Random(20 + level))
            for _ in range(600):
                problem = maker.next_problem(level)
                self.assertLessEqual(problem.answer, 600, problem.text)

    def test_no_step_goes_below_zero(self):
        # Level 1 is worked from left to right: no running total is negative.
        maker = ProblemMaker(random.Random(30))
        for _ in range(600):
            text = maker.next_problem(1).text
            nums, ops = numbers(text), operators(text)
            total = nums[0]
            for sign, n in zip(ops, nums[1:]):
                total = total + n if sign == "+" else total - n
                self.assertGreaterEqual(total, 0, text)

    def test_a_bracket_never_holds_a_negative_number(self):
        for level in range(1, MAX_LEVEL + 1):
            maker = ProblemMaker(random.Random(31 + level))
            for _ in range(600):
                text = maker.next_problem(level).text
                for inside in re.findall(r"\(([^)]*)\)", text):
                    self.assertGreaterEqual(solve(inside), 1, text)

    def test_never_the_same_problem_twice_in_a_row(self):
        for level in range(1, MAX_LEVEL + 1):
            maker = ProblemMaker(random.Random(40 + level))
            texts = [maker.next_problem(level).text for _ in range(1000)]
            for before, after in zip(texts, texts[1:]):
                self.assertNotEqual(before, after)

    def test_there_is_plenty_of_variety(self):
        for level in range(1, MAX_LEVEL + 1):
            maker = ProblemMaker(random.Random(50 + level))
            texts = {maker.next_problem(level).text for _ in range(100)}
            self.assertGreater(len(texts), 50, f"level {level}")

    def test_a_level_outside_the_range_is_the_nearest_level(self):
        maker = ProblemMaker(random.Random(60))
        for _ in range(100):
            self.assertEqual(len(operators(maker.next_problem(0).text)), 2)
        for _ in range(100):
            text = maker.next_problem(99).text
            self.assertTrue("(" in text or len(operators(text)) >= 3, text)

    def test_no_level_given_means_level_one(self):
        maker = ProblemMaker(random.Random(61))
        for _ in range(100):
            self.assertNotIn("×", maker.next_problem().text)


class LevelOneTest(unittest.TestCase):
    """Level 1: two additions (or a subtraction), like 47 + 38 + 25."""

    def problems(self, count=600):
        maker = ProblemMaker(random.Random(70))
        return [maker.next_problem(1) for _ in range(count)]

    def test_two_signs_and_three_numbers(self):
        for problem in self.problems():
            self.assertEqual(len(operators(problem.text)), 2, problem.text)
            self.assertEqual(len(numbers(problem.text)), 3, problem.text)

    def test_no_times_and_no_brackets(self):
        for problem in self.problems():
            self.assertNotIn("×", problem.text)
            self.assertNotIn("(", problem.text)

    def test_most_are_two_plain_additions(self):
        plain = [p for p in self.problems() if operators(p.text) == ["+", "+"]]
        self.assertGreater(len(plain), 100)

    def test_a_subtraction_also_appears(self):
        with_minus = [p for p in self.problems() if "-" in p.text]
        self.assertGreater(len(with_minus), 50)

    def test_the_numbers_have_two_digits(self):
        for problem in self.problems():
            for n in numbers(problem.text):
                self.assertTrue(10 <= n <= 99, problem.text)


class LevelTwoTest(unittest.TestCase):
    """Level 2: two multiplications, like 4 × 6 × 7 or 7 × 8 + 6 × 4."""

    def problems(self, count=600):
        maker = ProblemMaker(random.Random(80))
        return [maker.next_problem(2) for _ in range(count)]

    def test_always_exactly_two_times_signs(self):
        for problem in self.problems():
            self.assertEqual(problem.text.count("×"), 2, problem.text)

    def test_both_shapes_appear(self):
        chain = [p for p in self.problems() if operators(p.text) == ["×", "×"]]
        joined = [p for p in self.problems() if len(operators(p.text)) == 3]
        self.assertGreater(len(chain), 100)
        self.assertGreater(len(joined), 100)

    def test_the_joined_shape_uses_plus_or_minus_between_the_two(self):
        for problem in self.problems():
            ops = operators(problem.text)
            if len(ops) == 3:
                self.assertEqual(ops[0], "×")
                self.assertIn(ops[1], ("+", "-"))
                self.assertEqual(ops[2], "×")

    def test_the_times_numbers_are_small(self):
        for problem in self.problems():
            for n in numbers(problem.text):
                self.assertTrue(2 <= n <= 12, problem.text)


class LevelThreeTest(unittest.TestCase):
    """Level 3: a mix with "times before plus", brackets and 3 or more signs."""

    def problems(self, count=800):
        maker = ProblemMaker(random.Random(90))
        return [maker.next_problem(3) for _ in range(count)]

    def test_always_has_times_and_at_least_three_signs(self):
        for problem in self.problems():
            self.assertIn("×", problem.text)
            self.assertGreaterEqual(len(operators(problem.text)), 3, problem.text)

    def test_brackets_and_no_brackets_both_appear(self):
        problems = self.problems()
        self.assertGreater(sum("(" in p.text for p in problems), 100)
        self.assertGreater(sum("(" not in p.text for p in problems), 100)

    def test_brackets_really_change_the_answer(self):
        # A "(a + b) × c" must not be worked out as "a + b × c".
        for problem in self.problems():
            if problem.text.startswith("("):
                no_brackets = problem.text.replace("(", "").replace(")", "")
                self.assertNotEqual(solve(no_brackets), problem.answer, problem.text)

    def test_brackets_are_balanced_and_never_empty_or_nested(self):
        for problem in self.problems():
            self.assertEqual(problem.text.count("("), problem.text.count(")"))
            self.assertLessEqual(problem.text.count("("), 1)
            self.assertNotIn("()", problem.text)

    def test_at_least_three_different_shapes(self):
        shapes = set()
        for problem in self.problems():
            shapes.add(re.sub(r"\d+", "n", problem.text))
        self.assertGreaterEqual(len(shapes), 3)


class LevelsGetHarderTest(unittest.TestCase):
    """Hardness is measured by how many signs there are to work through (a
    bracket also counts, because it changes the order)."""

    def steps(self, level: int) -> list:
        maker = ProblemMaker(random.Random(100 + level))
        result = []
        for _ in range(600):
            text = maker.next_problem(level).text
            result.append(len(operators(text)) + text.count("("))
        return result

    def test_on_average_each_level_has_more_steps_than_the_one_before(self):
        average = [sum(s) / len(s) for s in map(self.steps, (1, 2, 3))]
        self.assertLess(average[0], average[1])
        self.assertLess(average[1], average[2])

    def test_the_easiest_problem_of_a_level_is_never_easier_than_the_level_before(self):
        fewest = [min(self.steps(level)) for level in (1, 2, 3)]
        self.assertLessEqual(fewest[0], fewest[1])
        self.assertLessEqual(fewest[1], fewest[2])
        self.assertGreaterEqual(fewest[2], 3)


if __name__ == "__main__":
    unittest.main()
