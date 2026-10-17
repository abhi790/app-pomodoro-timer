import unittest

from pomodoro.warning_timing import should_show_one_minute_warning, should_start_slide_in


class OneMinuteWarningTest(unittest.TestCase):
    def test_fires_at_exactly_one_minute_left(self):
        self.assertTrue(should_show_one_minute_warning(60, 30 * 60))

    def test_does_not_fire_before_or_after_the_one_minute_mark(self):
        self.assertFalse(should_show_one_minute_warning(61, 30 * 60))
        self.assertFalse(should_show_one_minute_warning(59, 30 * 60))

    def test_does_not_fire_for_a_block_that_is_only_one_minute_long(self):
        # A 1-minute Custom focus block should not warn the instant it starts.
        self.assertFalse(should_show_one_minute_warning(60, 60))

    def test_does_not_fire_for_a_block_shorter_than_a_minute(self):
        self.assertFalse(should_show_one_minute_warning(60, 30))

    def test_fires_for_a_block_a_second_longer_than_a_minute(self):
        self.assertTrue(should_show_one_minute_warning(60, 61))


class SlideInTest(unittest.TestCase):
    def test_fires_at_exactly_ten_seconds_left(self):
        self.assertTrue(should_start_slide_in(10))

    def test_fires_anywhere_inside_the_last_ten_seconds(self):
        for remaining in (1, 2, 5, 9, 10):
            self.assertTrue(should_start_slide_in(remaining), remaining)

    def test_does_not_fire_with_more_than_ten_seconds_left(self):
        self.assertFalse(should_start_slide_in(11))
        self.assertFalse(should_start_slide_in(60))

    def test_does_not_fire_once_time_is_up(self):
        self.assertFalse(should_start_slide_in(0))

    def test_does_not_fire_for_a_negative_number(self):
        self.assertFalse(should_start_slide_in(-1))


if __name__ == "__main__":
    unittest.main()
