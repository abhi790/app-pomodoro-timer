import os
import tempfile
import unittest
from pathlib import Path

# Run without a real screen if nobody chose a Qt platform already.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from pomodoro.math_quiz import Problem
from pomodoro.settings import AppConfig, Mode
from pomodoro.timer_logic import Phase
from pomodoro.ui.main_window import MainWindow
from pomodoro.ui.pause_overlay import PauseOverlay
from pomodoro.ui.unlock_panel import UnlockPanel
from pomodoro.usage import UsageTracker
from tests.test_tray_ui import FakeSound, FakeTray

_app = QApplication.instance() or QApplication([])


class RecordingMaker:
    """A maker that only notes which level it was asked for."""

    def __init__(self) -> None:
        self.levels = []

    def next_problem(self, level: int = 1) -> Problem:
        self.levels.append(level)
        return Problem("2 + 2", 4)


class BreakPanelLevelTest(unittest.TestCase):
    def make(self, math_left: int):
        maker = RecordingMaker()
        panel = UnlockPanel(maker)
        self.addCleanup(panel.deleteLater)
        panel.set_state(math_left)
        return panel, maker

    def test_the_first_unlock_of_the_day_asks_for_level_1(self):
        panel, maker = self.make(math_left=3)
        panel._leave_button.click()
        self.assertEqual(maker.levels, [1])

    def test_the_second_unlock_asks_for_level_2(self):
        panel, maker = self.make(math_left=2)
        panel._leave_button.click()
        self.assertEqual(maker.levels, [2])

    def test_the_third_unlock_asks_for_level_3(self):
        panel, maker = self.make(math_left=1)
        panel._leave_button.click()
        self.assertEqual(maker.levels, [3])

    def test_a_wrong_answer_gives_a_new_problem_of_the_same_level(self):
        panel, maker = self.make(math_left=2)
        panel._leave_button.click()
        panel._answer_edit.setText("5")
        panel._check_button.click()
        self.assertEqual(maker.levels, [2, 2])

    def test_the_text_says_which_level_comes_next(self):
        for left, level in ((3, 1), (2, 2), (1, 3)):
            panel, _ = self.make(math_left=left)
            self.assertIn(f"{left} of 3", panel._status_label.text())
            self.assertIn(f"level {level} of 3", panel._status_label.text())

    def test_with_no_unlock_left_the_text_has_no_level(self):
        panel, _ = self.make(math_left=0)
        self.assertNotIn("level", panel._status_label.text())


class PauseScreenLevelTest(unittest.TestCase):
    def make(self, math_left: int):
        maker = RecordingMaker()
        overlay = PauseOverlay(maker)
        self.addCleanup(overlay.deleteLater)
        overlay.set_math_left(math_left)
        return overlay, maker

    def test_stop_asks_for_the_level_of_the_next_unlock(self):
        for left, level in ((3, 1), (2, 2), (1, 3)):
            overlay, maker = self.make(math_left=left)
            overlay._stop_button.click()
            self.assertEqual(maker.levels, [level], f"{left} left")

    def test_the_text_says_which_level_comes_next(self):
        for left, level in ((3, 1), (2, 2), (1, 3)):
            overlay, _ = self.make(math_left=left)
            self.assertIn(f"level {level} of 3", overlay._status_label.text())

    def test_with_no_unlock_left_the_text_has_no_level(self):
        overlay, _ = self.make(math_left=0)
        self.assertNotIn("level", overlay._status_label.text())


class RealProblemsInTheAppTest(unittest.TestCase):
    """With the real problem maker: the day's problems get harder."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def break_problem_text(self, math_used: int) -> str:
        usage = UsageTracker(path=Path(self._tmp.name) / f"usage{math_used}.json")
        for _ in range(math_used):
            usage.record_math()
        window = MainWindow(AppConfig(mode=Mode.POMODORO), usage, FakeSound(), FakeTray())
        self.addCleanup(window._overlay.hide)
        self.addCleanup(window.hide)
        self.addCleanup(window.deleteLater)
        window.show()
        window._on_toggle()  # Start
        finished = window._timer.tick(10**6)
        self.assertIs(finished, Phase.FOCUS)
        window._announce(finished)
        panel = window._overlay._overlays[0]._panel
        panel._leave_button.click()
        return panel._problem_label.text()

    def test_unlock_one_is_sums_unlock_two_has_two_times_unlock_three_is_a_mix(self):
        first = self.break_problem_text(0)
        second = self.break_problem_text(1)
        third = self.break_problem_text(2)
        self.assertNotIn("×", first)
        self.assertEqual(second.count("×"), 2)
        self.assertGreaterEqual(sum(third.count(s) for s in "+-×"), 3)


if __name__ == "__main__":
    unittest.main()
