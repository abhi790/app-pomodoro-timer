import os
import tempfile
import unittest
from pathlib import Path

# Run without a real screen if nobody chose a Qt platform already.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton

from pomodoro.settings import AppConfig, Mode
from pomodoro.timer_logic import Phase
from pomodoro.ui.main_window import MainWindow
from pomodoro.usage import DAILY_MATH_LIMIT, UsageTracker
from tests.test_tray_ui import FakeSound, FakeTray

_app = QApplication.instance() or QApplication([])


class BreakFullLengthTest(unittest.TestCase):
    """After the 3 math unlocks are used up there is no Important button and no
    other way to shorten a break (except the testing Emergency exit)."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def make(self, math_used: int):
        usage = UsageTracker(path=Path(self._tmp.name) / "usage.json")
        for _ in range(math_used):
            usage.record_math()
        window = MainWindow(AppConfig(mode=Mode.POMODORO), usage, FakeSound(), FakeTray())
        self.addCleanup(window._pause_cover.hide)
        self.addCleanup(window._overlay.hide)
        self.addCleanup(window.hide)
        self.addCleanup(window.deleteLater)
        window.show()
        return window

    def end_focus(self, window) -> None:
        window._on_toggle()  # Start
        finished = window._timer.tick(10**6)
        self.assertIs(finished, Phase.FOCUS)
        window._announce(finished)
        window._refresh()

    def test_with_no_unlock_left_the_break_has_its_full_length(self):
        window = self.make(math_used=DAILY_MATH_LIMIT)
        self.end_focus(window)
        self.assertTrue(window._force_break_active)
        self.assertEqual(window._timer.remaining_seconds, 5 * 60)

    def test_the_main_window_has_no_important_handler(self):
        window = self.make(math_used=DAILY_MATH_LIMIT)
        self.assertFalse(hasattr(window, "_on_important"))

    def test_no_button_on_the_break_screen_is_about_important(self):
        window = self.make(math_used=DAILY_MATH_LIMIT)
        self.end_focus(window)
        for overlay in window._overlay._overlays:
            for button in overlay.findChildren(QPushButton):
                self.assertNotIn("important", button.text().lower())

    def test_the_usage_file_never_mentions_important(self):
        window = self.make(math_used=1)
        window._usage.record_math()
        text = (Path(self._tmp.name) / "usage.json").read_text(encoding="utf-8")
        self.assertNotIn("important", text)


if __name__ == "__main__":
    unittest.main()
