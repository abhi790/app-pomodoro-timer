import unittest

from pomodoro.formatting import format_clock


class FormatClockTest(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(format_clock(0), "00:00")

    def test_seconds_only(self):
        self.assertEqual(format_clock(9), "00:09")

    def test_minutes_and_seconds(self):
        self.assertEqual(format_clock(1500), "25:00")
        self.assertEqual(format_clock(1799), "29:59")

    def test_long_break_shows_sixty_minutes(self):
        self.assertEqual(format_clock(3600), "60:00")

    def test_negative_is_shown_as_zero(self):
        self.assertEqual(format_clock(-5), "00:00")


if __name__ == "__main__":
    unittest.main()
