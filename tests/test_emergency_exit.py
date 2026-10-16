import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# Run without a real screen if nobody chose a Qt platform already.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from pomodoro import lock_rules
from pomodoro.settings import AppConfig, Mode
from pomodoro.timer_logic import Phase
from pomodoro.ui.break_manager import BreakOverlayManager
from pomodoro.ui.break_overlay import BreakOverlay
from pomodoro.ui.main_window import MainWindow
from pomodoro.ui.pause_overlay import PauseCoverManager, PauseOverlay
from pomodoro.usage import UsageTracker
from tests.test_tray_ui import FakeSound, FakeTray

_app = QApplication.instance() or QApplication([])


def flag(value: bool):
    """Switch the testing flag on or off for one test."""
    return mock.patch.object(lock_rules, "EMERGENCY_EXIT_ENABLED", value)


class FlagTest(unittest.TestCase):
    def test_the_flag_decides_if_the_button_is_offered(self):
        with flag(True):
            self.assertTrue(lock_rules.emergency_exit_visible())
        with flag(False):
            self.assertFalse(lock_rules.emergency_exit_visible())


class ScreenButtonTest(unittest.TestCase):
    """The button on the break screen and the pause screen themselves."""

    def setUp(self):
        self.keep_alive = []

    def tearDown(self):
        for widget in self.keep_alive:
            widget.close()
            widget.deleteLater()
        _app.processEvents()

    def shown(self, widget):
        self.keep_alive.append(widget)
        widget.resize(1366, 768)
        widget.show()
        _app.processEvents()
        return widget

    def test_the_break_screen_has_the_button(self):
        with flag(True):
            overlay = self.shown(BreakOverlay())
        self.assertIsNotNone(overlay._emergency_button)
        self.assertTrue(overlay._emergency_button.isVisible())
        self.assertIn("Emergency", overlay._emergency_button.text())

    def test_the_pause_screen_has_the_button(self):
        with flag(True):
            overlay = self.shown(PauseOverlay())
        self.assertIsNotNone(overlay._emergency_button)
        self.assertTrue(overlay._emergency_button.isVisible())
        self.assertIn("Emergency", overlay._emergency_button.text())

    def test_with_the_flag_off_neither_screen_has_it(self):
        with flag(False):
            break_overlay = self.shown(BreakOverlay())
            pause_overlay = self.shown(PauseOverlay())
        self.assertIsNone(break_overlay._emergency_button)
        self.assertIsNone(pause_overlay._emergency_button)

    def test_pressing_it_sends_one_signal_on_each_screen(self):
        with flag(True):
            for overlay in (self.shown(BreakOverlay()), self.shown(PauseOverlay())):
                got = []
                overlay.emergency_exit.connect(lambda: got.append(1))
                overlay._emergency_button.click()
                self.assertEqual(got, [1], type(overlay).__name__)

    def test_it_is_there_whatever_the_days_math_count(self):
        with flag(True):
            break_overlay = self.shown(BreakOverlay())
            pause_overlay = self.shown(PauseOverlay())
        break_overlay.set_unlock_state(0)
        pause_overlay.set_math_used(0)
        self.assertTrue(break_overlay._emergency_button.isVisible())
        self.assertTrue(pause_overlay._emergency_button.isVisible())

    def test_it_is_there_while_the_math_problem_is_shown(self):
        with flag(True):
            break_overlay = self.shown(BreakOverlay())
            pause_overlay = self.shown(PauseOverlay())
        break_overlay.set_unlock_state(3)
        pause_overlay.set_math_used(3)
        break_overlay._panel._leave_button.click()
        pause_overlay._stop_button.click()
        self.assertTrue(break_overlay._emergency_button.isVisible())
        self.assertTrue(pause_overlay._emergency_button.isVisible())

    def test_the_button_does_not_make_either_screen_taller(self):
        # It floats in the corner instead of sitting in the layout, so a small
        # laptop screen has exactly the room it had without the button.
        heights = {}
        for on in (False, True):
            with flag(on):
                for cls in (BreakOverlay, PauseOverlay):
                    overlay = cls()
                    self.keep_alive.append(overlay)
                    heights[(cls.__name__, on)] = overlay.minimumSizeHint().height()
        for name in ("BreakOverlay", "PauseOverlay"):
            self.assertEqual(heights[(name, True)], heights[(name, False)], name)

    def test_the_button_stays_inside_the_screen_in_the_bottom_right_corner(self):
        with flag(True):
            for cls in (BreakOverlay, PauseOverlay):
                overlay = self.shown(cls())
                button = overlay._emergency_button
                box = button.geometry()
                self.assertTrue(overlay.rect().contains(box), cls.__name__)
                self.assertGreater(box.center().x(), overlay.width() * 0.6, cls.__name__)
                self.assertGreater(box.center().y(), overlay.height() * 0.8, cls.__name__)
                overlay.resize(1920, 1032)
                _app.processEvents()
                box = button.geometry()
                self.assertTrue(overlay.rect().contains(box), cls.__name__)
                self.assertGreater(box.center().x(), 1920 * 0.6, cls.__name__)

    def test_the_managers_pass_the_signal_on(self):
        with flag(True):
            break_manager = BreakOverlayManager()
            pause_manager = PauseCoverManager()
            break_manager.show("05:00", 3)
            pause_manager.show("10:00", 3)
        self.addCleanup(break_manager.hide)
        self.addCleanup(pause_manager.hide)
        got = []
        break_manager.emergency_exit.connect(lambda: got.append("break"))
        pause_manager.emergency_exit.connect(lambda: got.append("pause"))
        break_manager._overlays[0]._emergency_button.click()
        pause_manager._overlays[0]._emergency_button.click()
        self.assertEqual(got, ["break", "pause"])


class MainWindowTest(unittest.TestCase):
    """What the app does when the button is pressed: leave at once, with no
    math problem and without using up anything."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        patcher = flag(True)
        patcher.start()
        self.addCleanup(patcher.stop)

    def make(self, math_used: int = 0):
        usage = UsageTracker(path=Path(self._tmp.name) / "usage.json")
        for _ in range(math_used):
            usage.record_math()
        tray = FakeTray()
        window = MainWindow(AppConfig(mode=Mode.CUSTOM), usage, FakeSound(), tray)
        self.addCleanup(window._pause_cover.hide)
        self.addCleanup(window._overlay.hide)
        self.addCleanup(window.hide)
        self.addCleanup(window.deleteLater)
        window.show()
        return window, usage, tray

    def end_focus(self, window) -> None:
        """Run a focus block to its end, so the break screen opens."""
        window._on_toggle()  # Start
        finished = window._timer.tick(10**6)
        self.assertIs(finished, Phase.FOCUS)
        window._announce(finished)
        window._refresh()  # the clock check does this right after a block ends

    def pause(self, window) -> None:
        window._on_toggle()  # Start
        window._timer.tick(120)
        window._on_toggle()  # Pause

    # ----- on the break screen ----------------------------------------------

    def test_it_ends_the_break_at_once(self):
        window, _, _ = self.make()
        self.end_focus(window)
        self.assertTrue(window._overlay.is_active)
        window._overlay._overlays[0]._emergency_button.click()
        self.assertFalse(window._overlay.is_active)
        self.assertFalse(window._force_break_active)
        self.assertIs(window._timer.phase, Phase.FOCUS)
        self.assertFalse(window._timer.running)

    def test_on_the_break_it_uses_no_math_unlock(self):
        window, usage, _ = self.make(math_used=1)
        self.end_focus(window)
        window._overlay._overlays[0]._emergency_button.click()
        self.assertEqual(usage.math_used, 1)

    def test_on_the_break_it_works_however_much_math_was_used_today(self):
        window, usage, _ = self.make(math_used=3)
        self.end_focus(window)
        window._overlay._overlays[0]._emergency_button.click()
        self.assertFalse(window._overlay.is_active)
        self.assertEqual(usage.math_used, 3)

    def test_after_the_break_exit_the_window_is_free_again(self):
        window, _, tray = self.make()
        self.end_focus(window)
        self.assertFalse(tray.quit_enabled)  # Quit is locked during a break
        window._overlay._overlays[0]._emergency_button.click()
        self.assertTrue(tray.quit_enabled)
        self.assertTrue(window._settings_button.isEnabled())
        self.assertIn("Emergency", window._message_label.text())

    def test_a_late_break_signal_does_nothing_when_no_break_is_on(self):
        window, usage, _ = self.make()
        window._on_emergency_exit_break()
        self.assertIs(window._timer.phase, Phase.FOCUS)
        self.assertEqual(usage.math_used, 0)

    # ----- on the pause screen ----------------------------------------------

    def test_it_closes_the_pause_screen_and_gives_the_focus_block_up(self):
        window, _, _ = self.make()
        self.pause(window)
        self.assertTrue(window._pause_cover.is_active)
        window._pause_cover._overlays[0]._emergency_button.click()
        self.assertFalse(window._pause_cover.is_active)
        self.assertIs(window._timer.phase, Phase.FOCUS)
        self.assertFalse(window._timer.running)
        full = window._timer.settings.duration_seconds(Phase.FOCUS)
        self.assertEqual(window._timer.remaining_seconds, full)

    def test_the_interrupted_block_does_not_count(self):
        window, _, _ = self.make()
        self.pause(window)
        window._pause_cover._overlays[0]._emergency_button.click()
        self.assertEqual(window._timer.completed_pomodoros, 0)

    def test_on_the_pause_screen_it_uses_no_math_unlock(self):
        window, usage, _ = self.make(math_used=2)
        self.pause(window)
        window._pause_cover._overlays[0]._emergency_button.click()
        self.assertEqual(usage.math_used, 2)

    def test_on_the_pause_screen_it_works_whatever_math_was_used_today(self):
        window, _, _ = self.make(math_used=3)
        self.pause(window)
        overlay = window._pause_cover._overlays[0]
        overlay._emergency_button.click()
        self.assertFalse(window._pause_cover.is_active)

    def test_after_the_pause_exit_the_window_is_free_again(self):
        window, _, tray = self.make()
        self.pause(window)
        self.assertFalse(tray.quit_enabled)
        window._pause_cover._overlays[0]._emergency_button.click()
        self.assertTrue(tray.quit_enabled)
        self.assertTrue(window._settings_button.isEnabled())
        self.assertIn("Emergency", window._message_label.text())

    def test_a_late_pause_signal_does_nothing_when_no_pause_is_on(self):
        window, _, _ = self.make()
        window._on_toggle()  # Start, no pause screen
        left = window._timer.remaining_seconds
        window._on_emergency_exit_pause()
        self.assertTrue(window._timer.running)
        self.assertEqual(window._timer.remaining_seconds, left)


if __name__ == "__main__":
    unittest.main()
