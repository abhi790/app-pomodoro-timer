import random
import unittest

from pomodoro.ideas import (
    CREATIVE_IDEAS,
    MAX_CUSTOM_IDEAS,
    MAX_IDEA_LENGTH,
    IdeaRotator,
    clean_ideas,
    ideas_from_text,
    ideas_to_text,
)


class IdeaListTest(unittest.TestCase):
    def test_has_a_good_list_of_ideas(self):
        self.assertGreaterEqual(len(CREATIVE_IDEAS), 30)

    def test_no_duplicate_ideas(self):
        lowered = [idea.casefold() for idea in CREATIVE_IDEAS]
        self.assertEqual(len(lowered), len(set(lowered)))

    def test_ideas_are_a_readable_length(self):
        for idea in CREATIVE_IDEAS:
            self.assertGreaterEqual(len(idea), 20, idea)
            self.assertLessEqual(len(idea), MAX_IDEA_LENGTH, idea)

    def test_ideas_are_plain_text(self):
        for idea in CREATIVE_IDEAS:
            self.assertTrue(idea.isascii(), idea)


class CleanIdeasTest(unittest.TestCase):
    def test_squeezes_spaces_and_drops_empty_lines(self):
        result = clean_ideas(["  paint   a  rock ", "", "   ", "bake bread"])
        self.assertEqual(result, ("paint a rock", "bake bread"))

    def test_drops_repeats_ignoring_capitals(self):
        result = clean_ideas(["Paint a rock", "paint a ROCK", "Other"])
        self.assertEqual(result, ("Paint a rock", "Other"))

    def test_cuts_very_long_ideas(self):
        result = clean_ideas(["word " * 100])
        self.assertEqual(len(result), 1)
        self.assertLessEqual(len(result[0]), MAX_IDEA_LENGTH)
        self.assertFalse(result[0].endswith(" "))

    def test_keeps_at_most_the_limit(self):
        lines = [f"idea number {n}" for n in range(MAX_CUSTOM_IDEAS + 50)]
        result = clean_ideas(lines)
        self.assertEqual(len(result), MAX_CUSTOM_IDEAS)
        self.assertEqual(result[0], "idea number 0")

    def test_keeps_other_alphabets(self):
        self.assertEqual(clean_ideas(["  chitra banao  "]), ("chitra banao",))
        self.assertEqual(clean_ideas(["संगीत"]), ("संगीत",))

    def test_a_plain_string_is_rejected(self):
        with self.assertRaises(TypeError):
            clean_ideas("one idea")

    def test_a_non_text_item_is_rejected(self):
        with self.assertRaises(TypeError):
            clean_ideas(["fine", 5])

    def test_empty_gives_empty(self):
        self.assertEqual(clean_ideas([]), ())


class TextConversionTest(unittest.TestCase):
    def test_one_idea_per_line(self):
        self.assertEqual(
            ideas_from_text("paint a rock\n\n  bake bread  \n"),
            ("paint a rock", "bake bread"),
        )

    def test_round_trip(self):
        ideas = ("paint a rock", "bake bread")
        self.assertEqual(ideas_from_text(ideas_to_text(ideas)), ideas)

    def test_empty_text_gives_no_ideas(self):
        self.assertEqual(ideas_from_text(""), ())


class IdeaRotatorTest(unittest.TestCase):
    def test_each_round_shows_every_idea_once(self):
        rotator = IdeaRotator(rng=random.Random(1))
        shown = [rotator.next_idea() for _ in range(len(CREATIVE_IDEAS))]
        self.assertEqual(set(shown), set(CREATIVE_IDEAS))
        self.assertEqual(len(shown), len(set(shown)))

    def test_never_repeats_the_same_idea_twice_in_a_row(self):
        rotator = IdeaRotator(rng=random.Random(7))
        shown = [rotator.next_idea() for _ in range(len(CREATIVE_IDEAS) * 5)]
        for before, after in zip(shown, shown[1:]):
            self.assertNotEqual(before, after)

    def test_order_changes_between_rounds(self):
        rotator = IdeaRotator(rng=random.Random(5))
        size = len(CREATIVE_IDEAS)
        first = [rotator.next_idea() for _ in range(size)]
        second = [rotator.next_idea() for _ in range(size)]
        self.assertNotEqual(first, second)

    def test_your_own_ideas_are_mixed_in(self):
        mine = ("Juggle three socks", "Write a limerick")
        rotator = IdeaRotator(custom=mine, rng=random.Random(2))
        shown = {rotator.next_idea() for _ in range(len(CREATIVE_IDEAS) + 2)}
        for idea in mine:
            self.assertIn(idea, shown)

    def test_your_idea_that_matches_a_built_in_is_not_doubled(self):
        copy = CREATIVE_IDEAS[0].upper()
        rotator = IdeaRotator(custom=(copy,), rng=random.Random(2))
        shown = [rotator.next_idea() for _ in range(len(CREATIVE_IDEAS))]
        self.assertEqual(len(shown), len(set(shown)))
        self.assertNotIn(copy, shown)

    def test_messy_custom_ideas_are_cleaned(self):
        rotator = IdeaRotator(
            custom=("  Juggle   socks ", "", "juggle socks"),
            ideas=("Built in",),
            rng=random.Random(2),
        )
        shown = {rotator.next_idea() for _ in range(2)}
        self.assertEqual(shown, {"Built in", "Juggle socks"})

    def test_empty_everything_is_rejected(self):
        with self.assertRaises(ValueError):
            IdeaRotator(ideas=())

    def test_only_custom_ideas_work(self):
        rotator = IdeaRotator(custom=("Only mine",), ideas=())
        self.assertEqual(rotator.next_idea(), "Only mine")
        self.assertEqual(rotator.next_idea(), "Only mine")


if __name__ == "__main__":
    unittest.main()
