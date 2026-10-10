import random
import unittest

from pomodoro.tips import (
    CATEGORIES,
    CATEGORY_TITLE,
    HEALTHY_TIPS,
    MAX_TIP_SECONDS,
    MIN_TIP_SECONDS,
    Tip,
    TipRotator,
    tip_display_seconds,
)


class TipListTest(unittest.TestCase):
    def test_has_a_big_list_of_tips(self):
        self.assertGreaterEqual(len(HEALTHY_TIPS), 100)

    def test_every_category_has_many_tips_and_a_title(self):
        for category in CATEGORIES:
            count = sum(1 for tip in HEALTHY_TIPS if tip.category == category)
            self.assertGreaterEqual(count, 10, category)
            self.assertIn(category, CATEGORY_TITLE)

    def test_every_tip_uses_a_known_category(self):
        for tip in HEALTHY_TIPS:
            self.assertIn(tip.category, CATEGORIES)

    def test_no_duplicate_tips(self):
        texts = [tip.text for tip in HEALTHY_TIPS]
        self.assertEqual(len(texts), len(set(texts)))

    def test_tips_are_a_readable_length(self):
        for tip in HEALTHY_TIPS:
            self.assertGreaterEqual(len(tip.text), 20, tip.text)
            self.assertLessEqual(len(tip.text), 180, tip.text)

    def test_tips_are_plain_text(self):
        for tip in HEALTHY_TIPS:
            self.assertTrue(tip.text.isascii(), tip.text)


class DisplaySecondsTest(unittest.TestCase):
    def test_short_text_stays_the_minimum(self):
        self.assertEqual(tip_display_seconds("Drink water."), MIN_TIP_SECONDS)

    def test_very_long_text_stays_the_maximum(self):
        self.assertEqual(tip_display_seconds("x" * 1000), MAX_TIP_SECONDS)

    def test_longer_text_stays_longer(self):
        self.assertLess(tip_display_seconds("x" * 40), tip_display_seconds("x" * 70))

    def test_every_tip_is_between_ten_and_twenty_seconds(self):
        for tip in HEALTHY_TIPS:
            seconds = tip_display_seconds(tip.text)
            self.assertGreaterEqual(seconds, 10)
            self.assertLessEqual(seconds, 20)

    def test_the_tips_do_not_all_use_the_same_time(self):
        times = {tip_display_seconds(tip.text) for tip in HEALTHY_TIPS}
        self.assertGreater(len(times), 3)


class TipRotatorTest(unittest.TestCase):
    def test_empty_list_is_rejected(self):
        with self.assertRaises(ValueError):
            TipRotator(tips=())

    def test_each_round_shows_every_tip_once(self):
        rotator = TipRotator(rng=random.Random(1))
        shown = [rotator.next_tip() for _ in range(len(HEALTHY_TIPS))]
        self.assertEqual(set(shown), set(HEALTHY_TIPS))
        self.assertEqual(len(shown), len(set(shown)))

    def test_never_repeats_the_same_tip_twice_in_a_row(self):
        rotator = TipRotator(rng=random.Random(7))
        shown = [rotator.next_tip() for _ in range(len(HEALTHY_TIPS) * 5)]
        for before, after in zip(shown, shown[1:]):
            self.assertNotEqual(before, after)

    def test_categories_take_turns(self):
        rotator = TipRotator(rng=random.Random(3))
        shown = [rotator.next_tip() for _ in range(len(HEALTHY_TIPS) * 3)]
        for before, after in zip(shown, shown[1:]):
            self.assertNotEqual(before.category, after.category)

    def test_order_changes_between_rounds(self):
        rotator = TipRotator(rng=random.Random(5))
        size = len(HEALTHY_TIPS)
        first = [rotator.next_tip() for _ in range(size)]
        second = [rotator.next_tip() for _ in range(size)]
        self.assertNotEqual(first, second)

    def test_single_tip_just_repeats(self):
        only = Tip("mind", "Only one")
        rotator = TipRotator(tips=(only,))
        self.assertEqual(rotator.next_tip(), only)
        self.assertEqual(rotator.next_tip(), only)


if __name__ == "__main__":
    unittest.main()
