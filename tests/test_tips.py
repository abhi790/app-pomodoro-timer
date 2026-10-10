import random
import unittest

from pomodoro.tips import HEALTHY_TIPS, TIP_SECONDS, TipRotator


class TipRotatorTest(unittest.TestCase):
    def test_has_tips_and_a_sensible_delay(self):
        self.assertGreaterEqual(len(HEALTHY_TIPS), 6)
        self.assertGreaterEqual(TIP_SECONDS, 5)

    def test_empty_list_is_rejected(self):
        with self.assertRaises(ValueError):
            TipRotator(tips=())

    def test_each_round_shows_every_tip_once(self):
        rotator = TipRotator(rng=random.Random(1))
        shown = [rotator.next_tip() for _ in range(len(HEALTHY_TIPS))]
        self.assertEqual(sorted(shown), sorted(HEALTHY_TIPS))

    def test_never_repeats_the_same_tip_twice_in_a_row(self):
        rotator = TipRotator(rng=random.Random(7))
        shown = [rotator.next_tip() for _ in range(len(HEALTHY_TIPS) * 20)]
        for before, after in zip(shown, shown[1:]):
            self.assertNotEqual(before, after)

    def test_single_tip_just_repeats(self):
        rotator = TipRotator(tips=("Only one",))
        self.assertEqual(rotator.next_tip(), "Only one")
        self.assertEqual(rotator.next_tip(), "Only one")


if __name__ == "__main__":
    unittest.main()
