import unittest

from pomodoro.lock_rules import can_stop, controls_enabled
from pomodoro.timer_logic import Phase, PomodoroTimer, TimerSettings
from pomodoro.tray_logic import can_quit


class ControlsEnabledTest(unittest.TestCase):
    def test_reset_and_settings_work_when_everything_is_stopped(self):
        self.assertTrue(controls_enabled(False, False, False))

    def test_they_are_locked_while_the_timer_runs(self):
        self.assertFalse(controls_enabled(True, False, False))

    def test_they_are_locked_during_a_force_break(self):
        self.assertFalse(controls_enabled(False, True, False))

    def test_they_are_locked_while_the_pause_screen_is_up(self):
        self.assertFalse(controls_enabled(False, False, True))


class CanStopTest(unittest.TestCase):
    def test_stop_is_offered_while_math_unlocks_are_left(self):
        for left in (1, 2, 3):
            self.assertTrue(can_stop(left), left)

    def test_stop_is_not_offered_with_no_math_left(self):
        self.assertFalse(can_stop(0))


class QuitDuringPauseTest(unittest.TestCase):
    def test_quit_is_locked_while_the_pause_screen_is_up(self):
        self.assertFalse(can_quit(False, pause_cover_active=True))

    def test_quit_still_works_normally(self):
        self.assertTrue(can_quit(False))
        self.assertTrue(can_quit(False, False))

    def test_quit_is_still_locked_during_a_force_break(self):
        self.assertFalse(can_quit(True))


class AbandonFocusTest(unittest.TestCase):
    def make(self) -> PomodoroTimer:
        return PomodoroTimer(TimerSettings(focus_minutes=25, short_break_minutes=5))

    def test_gives_back_a_fresh_stopped_focus_block(self):
        timer = self.make()
        timer.start()
        timer.tick(600)
        timer.pause()
        timer.abandon_focus()
        self.assertEqual(timer.phase, Phase.FOCUS)
        self.assertEqual(timer.remaining_seconds, 25 * 60)
        self.assertFalse(timer.running)

    def test_the_interrupted_block_does_not_count(self):
        timer = self.make()
        timer.start()
        timer.tick(100)
        timer.abandon_focus()
        self.assertEqual(timer.completed_pomodoros, 0)

    def test_finished_pomodoros_stay_counted(self):
        timer = self.make()
        for _ in range(2):
            timer.start()
            timer.tick(timer.remaining_seconds)  # focus done
            timer.start()
            timer.tick(timer.remaining_seconds)  # break done
        self.assertEqual(timer.completed_pomodoros, 2)
        timer.start()
        timer.tick(60)
        timer.abandon_focus()
        self.assertEqual(timer.completed_pomodoros, 2)

    def test_the_cycle_towards_the_long_break_is_not_pushed_ahead(self):
        timer = self.make()
        timer.start()
        timer.tick(timer.remaining_seconds)  # pomodoro 1 done -> short break
        timer.skip()  # back to Focus
        timer.start()
        timer.tick(30)
        timer.abandon_focus()
        self.assertEqual(timer.completed_pomodoros, 1)
        self.assertEqual(timer.phase, Phase.FOCUS)

    def test_does_nothing_during_a_break(self):
        timer = self.make()
        timer.start()
        timer.tick(timer.remaining_seconds)  # now in a short break
        timer.start()
        timer.tick(30)
        before = (timer.phase, timer.remaining_seconds, timer.running)
        timer.abandon_focus()
        self.assertEqual((timer.phase, timer.remaining_seconds, timer.running), before)

    def test_uses_the_current_settings(self):
        timer = self.make()
        timer.update_settings(TimerSettings(focus_minutes=40))
        timer.start()
        timer.tick(5)
        timer.abandon_focus()
        self.assertEqual(timer.remaining_seconds, 40 * 60)


if __name__ == "__main__":
    unittest.main()
