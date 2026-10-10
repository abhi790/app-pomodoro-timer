import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from pomodoro.usage import (
    DAILY_MATH_LIMIT,
    IMPORTANT_BREAK_SECONDS,
    DailyUsage,
    UsageTracker,
    load_usage,
    save_usage,
)

DAY_ONE = date(2026, 10, 10)
DAY_TWO = date(2026, 10, 11)


class Clock:
    """A fake calendar the test can move forward."""

    def __init__(self, today: date) -> None:
        self.today = today

    def __call__(self) -> date:
        return self.today


class ConstantsTest(unittest.TestCase):
    def test_three_math_unlocks_a_day(self):
        self.assertEqual(DAILY_MATH_LIMIT, 3)

    def test_important_break_is_three_minutes(self):
        self.assertEqual(IMPORTANT_BREAK_SECONDS, 3 * 60)


class LoadSaveTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "folder" / "usage.json"

    def test_missing_file_is_a_fresh_day(self):
        self.assertEqual(load_usage(self.path, "2026-10-10"), DailyUsage("2026-10-10"))

    def test_save_then_load_same_day(self):
        save_usage(DailyUsage("2026-10-10", math_used=2, important_used=1), self.path)
        loaded = load_usage(self.path, "2026-10-10")
        self.assertEqual(loaded, DailyUsage("2026-10-10", 2, 1))

    def test_save_creates_the_folder(self):
        save_usage(DailyUsage("2026-10-10"), self.path)
        self.assertTrue(self.path.exists())

    def test_old_date_is_a_fresh_day(self):
        save_usage(DailyUsage("2026-10-09", math_used=3), self.path)
        self.assertEqual(load_usage(self.path, "2026-10-10"), DailyUsage("2026-10-10"))

    def test_broken_json_is_a_fresh_day(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{not json", encoding="utf-8")
        self.assertEqual(load_usage(self.path, "2026-10-10"), DailyUsage("2026-10-10"))

    def test_wrong_shape_is_a_fresh_day(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
        self.assertEqual(load_usage(self.path, "2026-10-10"), DailyUsage("2026-10-10"))

    def test_bad_numbers_are_a_fresh_day(self):
        self.path.parent.mkdir(parents=True)
        for bad in (-1, "2", 1.5, True, None):
            data = {"day": "2026-10-10", "math_used": bad, "important_used": 0}
            self.path.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(
                load_usage(self.path, "2026-10-10"), DailyUsage("2026-10-10"), bad
            )


class UsageTrackerTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "usage.json"
        self.clock = Clock(DAY_ONE)

    def tracker(self) -> UsageTracker:
        return UsageTracker(self.path, self.clock)

    def test_starts_with_all_unlocks_left(self):
        t = self.tracker()
        self.assertEqual(t.math_used, 0)
        self.assertEqual(t.math_left, DAILY_MATH_LIMIT)
        self.assertEqual(t.important_used, 0)

    def test_record_math_counts_down(self):
        t = self.tracker()
        t.record_math()
        self.assertEqual(t.math_used, 1)
        self.assertEqual(t.math_left, DAILY_MATH_LIMIT - 1)

    def test_math_left_stops_at_zero(self):
        t = self.tracker()
        for _ in range(DAILY_MATH_LIMIT + 2):
            t.record_math()
        self.assertEqual(t.math_left, 0)

    def test_record_important_has_no_limit(self):
        t = self.tracker()
        for _ in range(10):
            t.record_important()
        self.assertEqual(t.important_used, 10)

    def test_count_is_saved_and_survives_a_restart(self):
        t = self.tracker()
        t.record_math()
        t.record_math()
        t.record_important()
        again = self.tracker()
        self.assertEqual(again.math_used, 2)
        self.assertEqual(again.important_used, 1)
        self.assertEqual(again.math_left, DAILY_MATH_LIMIT - 2)

    def test_new_day_after_restart_starts_again(self):
        t = self.tracker()
        for _ in range(DAILY_MATH_LIMIT):
            t.record_math()
        self.clock.today = DAY_TWO
        again = self.tracker()
        self.assertEqual(again.math_left, DAILY_MATH_LIMIT)

    def test_midnight_while_the_app_is_open_resets_the_count(self):
        t = self.tracker()
        for _ in range(DAILY_MATH_LIMIT):
            t.record_math()
        t.record_important()
        self.assertEqual(t.math_left, 0)
        self.clock.today = DAY_TWO  # the clock passes midnight
        self.assertEqual(t.math_left, DAILY_MATH_LIMIT)
        self.assertEqual(t.important_used, 0)

    def test_first_record_of_the_new_day_counts_as_one(self):
        t = self.tracker()
        t.record_math()
        self.clock.today = DAY_TWO
        t.record_math()
        self.assertEqual(t.math_used, 1)

    def test_file_holds_only_today(self):
        t = self.tracker()
        t.record_math()
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.assertEqual(
            data, {"day": "2026-10-10", "math_used": 1, "important_used": 0}
        )

    def test_unwritable_location_does_not_crash(self):
        blocker = Path(self._tmp.name) / "blocker"
        blocker.write_text("a file, not a folder", encoding="utf-8")
        t = UsageTracker(blocker / "usage.json", self.clock)
        t.record_math()  # saving fails quietly
        self.assertEqual(t.math_used, 1)


if __name__ == "__main__":
    unittest.main()
