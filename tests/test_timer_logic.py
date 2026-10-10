import unittest

from pomodoro.timer_logic import Phase, PomodoroTimer, TimerSettings


def finish_phase(timer: PomodoroTimer):
    """Start the timer and run it until the current phase ends."""
    timer.start()
    return timer.tick(timer.remaining_seconds)


class TimerSettingsTest(unittest.TestCase):
    def test_defaults(self):
        s = TimerSettings()
        self.assertEqual(s.focus_minutes, 30)
        self.assertEqual(s.short_break_minutes, 5)
        self.assertEqual(s.long_break_minutes, 60)
        self.assertEqual(s.pomodoros_before_long_break, 4)

    def test_duration_seconds(self):
        s = TimerSettings(focus_minutes=25, short_break_minutes=5, long_break_minutes=15)
        self.assertEqual(s.duration_seconds(Phase.FOCUS), 1500)
        self.assertEqual(s.duration_seconds(Phase.SHORT_BREAK), 300)
        self.assertEqual(s.duration_seconds(Phase.LONG_BREAK), 900)

    def test_rejects_zero_and_negative(self):
        with self.assertRaises(ValueError):
            TimerSettings(focus_minutes=0)
        with self.assertRaises(ValueError):
            TimerSettings(short_break_minutes=-5)
        with self.assertRaises(ValueError):
            TimerSettings(pomodoros_before_long_break=0)

    def test_rejects_non_whole_numbers(self):
        with self.assertRaises(ValueError):
            TimerSettings(focus_minutes=2.5)
        with self.assertRaises(ValueError):
            TimerSettings(focus_minutes=True)


class PomodoroTimerTest(unittest.TestCase):
    def test_starts_stopped_on_focus(self):
        t = PomodoroTimer()
        self.assertEqual(t.phase, Phase.FOCUS)
        self.assertEqual(t.remaining_seconds, 30 * 60)
        self.assertFalse(t.running)
        self.assertEqual(t.completed_pomodoros, 0)

    def test_tick_does_nothing_when_not_running(self):
        t = PomodoroTimer()
        self.assertIsNone(t.tick(10))
        self.assertEqual(t.remaining_seconds, 30 * 60)

    def test_tick_counts_down_when_running(self):
        t = PomodoroTimer()
        t.start()
        self.assertIsNone(t.tick(10))
        self.assertEqual(t.remaining_seconds, 30 * 60 - 10)

    def test_pause_stops_the_countdown(self):
        t = PomodoroTimer()
        t.start()
        t.tick(5)
        t.pause()
        t.tick(5)
        self.assertEqual(t.remaining_seconds, 30 * 60 - 5)

    def test_focus_finishes_into_short_break_and_stops(self):
        t = PomodoroTimer()
        finished = finish_phase(t)
        self.assertEqual(finished, Phase.FOCUS)
        self.assertEqual(t.phase, Phase.SHORT_BREAK)
        self.assertEqual(t.remaining_seconds, 5 * 60)
        self.assertFalse(t.running)
        self.assertEqual(t.completed_pomodoros, 1)

    def test_break_finishes_back_into_focus(self):
        t = PomodoroTimer()
        finish_phase(t)
        finished = finish_phase(t)
        self.assertEqual(finished, Phase.SHORT_BREAK)
        self.assertEqual(t.phase, Phase.FOCUS)
        self.assertEqual(t.completed_pomodoros, 1)

    def test_long_break_after_four_pomodoros(self):
        t = PomodoroTimer()
        for _ in range(3):
            finish_phase(t)  # focus
            self.assertEqual(t.phase, Phase.SHORT_BREAK)
            finish_phase(t)  # short break
        finish_phase(t)  # 4th focus
        self.assertEqual(t.phase, Phase.LONG_BREAK)
        self.assertEqual(t.remaining_seconds, 60 * 60)
        self.assertEqual(t.completed_pomodoros, 4)

    def test_cycle_repeats_after_long_break(self):
        t = PomodoroTimer()
        for _ in range(4):
            finish_phase(t)  # focus
            finish_phase(t)  # break (the 4th one is the long break)
        self.assertEqual(t.phase, Phase.FOCUS)
        # Next long break comes after the 8th pomodoro, not the 5th.
        finish_phase(t)
        self.assertEqual(t.phase, Phase.SHORT_BREAK)

    def test_custom_cycle_length(self):
        t = PomodoroTimer(TimerSettings(pomodoros_before_long_break=2))
        finish_phase(t)
        self.assertEqual(t.phase, Phase.SHORT_BREAK)
        finish_phase(t)
        finish_phase(t)
        self.assertEqual(t.phase, Phase.LONG_BREAK)

    def test_overshoot_does_not_leave_negative_time(self):
        t = PomodoroTimer(TimerSettings(focus_minutes=1))
        t.start()
        t.tick(500)
        self.assertEqual(t.phase, Phase.SHORT_BREAK)
        self.assertEqual(t.remaining_seconds, 5 * 60)

    def test_skip_focus_does_not_count_and_gives_short_break(self):
        t = PomodoroTimer()
        t.start()
        t.skip()
        self.assertEqual(t.phase, Phase.SHORT_BREAK)
        self.assertEqual(t.completed_pomodoros, 0)
        self.assertFalse(t.running)

    def test_skip_break_goes_to_focus(self):
        t = PomodoroTimer()
        finish_phase(t)
        t.skip()
        self.assertEqual(t.phase, Phase.FOCUS)
        self.assertEqual(t.remaining_seconds, 30 * 60)

    def test_skip_long_break_goes_to_focus_without_changing_the_count(self):
        t = PomodoroTimer()
        for _ in range(4):
            finish_phase(t)  # focus
            if t.phase is Phase.LONG_BREAK:
                break
            finish_phase(t)  # short break
        self.assertEqual(t.phase, Phase.LONG_BREAK)
        t.start()
        t.skip()
        self.assertEqual(t.phase, Phase.FOCUS)
        self.assertEqual(t.completed_pomodoros, 4)
        self.assertEqual(t.remaining_seconds, 30 * 60)
        self.assertFalse(t.running)

    def test_limit_remaining_cuts_a_long_break_short(self):
        t = PomodoroTimer(TimerSettings(focus_minutes=1, long_break_minutes=60,
                                        pomodoros_before_long_break=1))
        finish_phase(t)
        self.assertEqual(t.phase, Phase.LONG_BREAK)
        t.start()
        t.limit_remaining(180)
        self.assertEqual(t.remaining_seconds, 180)
        self.assertEqual(t.phase, Phase.LONG_BREAK)
        self.assertTrue(t.running)

    def test_limit_remaining_never_makes_time_longer(self):
        t = PomodoroTimer()
        t.limit_remaining(10 * 60 * 60)
        self.assertEqual(t.remaining_seconds, 30 * 60)

    def test_limit_remaining_keeps_a_shorter_break_as_it_is(self):
        t = PomodoroTimer()
        finish_phase(t)
        t.start()
        t.tick(4 * 60)  # 1 minute of the 5-minute break is left
        t.limit_remaining(180)
        self.assertEqual(t.remaining_seconds, 60)

    def test_limit_remaining_then_the_break_ends_into_focus(self):
        t = PomodoroTimer()
        finish_phase(t)
        t.start()
        t.limit_remaining(60)
        self.assertEqual(t.tick(60), Phase.SHORT_BREAK)
        self.assertEqual(t.phase, Phase.FOCUS)
        self.assertFalse(t.running)

    def test_reset_goes_back_to_start(self):
        t = PomodoroTimer()
        finish_phase(t)
        t.reset()
        self.assertEqual(t.phase, Phase.FOCUS)
        self.assertEqual(t.remaining_seconds, 30 * 60)
        self.assertEqual(t.completed_pomodoros, 0)
        self.assertFalse(t.running)

    def test_update_settings_when_stopped_uses_new_length(self):
        t = PomodoroTimer()
        t.update_settings(TimerSettings(focus_minutes=45))
        self.assertEqual(t.remaining_seconds, 45 * 60)

    def test_update_settings_while_running_keeps_remaining_time(self):
        t = PomodoroTimer()
        t.start()
        t.tick(60)
        t.update_settings(TimerSettings(focus_minutes=45))
        self.assertEqual(t.remaining_seconds, 30 * 60 - 60)
        # The new length is used for the next phases.
        t.tick(t.remaining_seconds)
        self.assertEqual(t.phase, Phase.SHORT_BREAK)


if __name__ == "__main__":
    unittest.main()
