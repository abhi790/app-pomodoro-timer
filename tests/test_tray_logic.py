import unittest

from pomodoro.tray_logic import (
    HIDE,
    QUIT,
    can_quit,
    close_action,
    tray_tooltip,
)


class TooltipTest(unittest.TestCase):
    def test_a_running_timer_shows_the_time_left(self):
        text = tray_tooltip("Focus", "24:59", running=True)
        self.assertIn("Focus 24:59", text)
        self.assertNotIn("paused", text)

    def test_a_stopped_timer_says_paused(self):
        self.assertIn("(paused)", tray_tooltip("Focus", "25:00", running=False))

    def test_the_app_name_is_on_the_first_line(self):
        self.assertEqual(
            tray_tooltip("Short break", "04:30", True).splitlines()[0],
            "Pomodoro Timer",
        )

    def test_breaks_show_their_name(self):
        self.assertIn("Long break 59:00", tray_tooltip("Long break", "59:00", True))


class CloseActionTest(unittest.TestCase):
    def test_close_hides_to_the_tray(self):
        self.assertEqual(close_action(tray_available=True, quitting=False), HIDE)

    def test_close_quits_when_there_is_no_tray(self):
        self.assertEqual(close_action(tray_available=False, quitting=False), QUIT)

    def test_close_quits_when_quit_was_chosen(self):
        self.assertEqual(close_action(tray_available=True, quitting=True), QUIT)
        self.assertEqual(close_action(tray_available=False, quitting=True), QUIT)


class CanQuitTest(unittest.TestCase):
    def test_quit_is_allowed_outside_a_break(self):
        self.assertTrue(can_quit(break_active=False))

    def test_quit_is_locked_during_a_force_break(self):
        self.assertFalse(can_quit(break_active=True))


if __name__ == "__main__":
    unittest.main()
