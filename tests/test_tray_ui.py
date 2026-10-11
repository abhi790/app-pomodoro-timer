import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# Run without a real screen if nobody chose a Qt platform already.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication

from pomodoro.settings import AppConfig, Mode
from pomodoro.timer_logic import Phase
from pomodoro.ui.main_window import MainWindow
from pomodoro.ui.tray import TrayIcon
from pomodoro.usage import UsageTracker

_app = QApplication.instance() or QApplication([])


class FakeSound:
    available = True

    def play(self, sound_file: str = "") -> bool:
        return True


class FakeTray(QObject):
    """Stands in for TrayIcon: remembers what the window asked of it."""

    show_requested = Signal()
    quit_requested = Signal()

    def __init__(self, available: bool = True) -> None:
        super().__init__()
        self.available = available
        self.tooltip = ""
        self.quit_enabled = True
        self.messages: list = []
        self.hidden = False

    def set_tooltip(self, text: str) -> None:
        self.tooltip = text

    def set_quit_enabled(self, enabled: bool) -> None:
        self.quit_enabled = enabled

    def notify(self, title: str, message: str) -> None:
        self.messages.append((title, message))

    def hide(self) -> None:
        self.hidden = True


class TrayWindowTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)

    def make(self, available: bool = True) -> tuple:
        tray = FakeTray(available)
        window = MainWindow(
            AppConfig(mode=Mode.CUSTOM),
            UsageTracker(path=Path(self._tmp.name) / "usage.json"),
            FakeSound(),
            tray,
        )
        self.keep_alive = getattr(self, "keep_alive", []) + [window, tray]
        self.addCleanup(window._overlay.hide)
        self.addCleanup(window.hide)
        window.show()
        return window, tray

    def end_focus(self, window) -> None:
        window._timer.start()
        window._timer.tick(window._timer.remaining_seconds)
        window._announce(Phase.FOCUS)

    # ----- closing the window ----------------------------------------------

    def test_close_hides_the_window_and_the_timer_keeps_running(self):
        window, tray = self.make()
        window._on_toggle()  # Start
        window.close()
        self.assertFalse(window.isVisible())
        self.assertTrue(window._timer.running)
        self.assertFalse(tray.hidden)

    def test_the_first_close_tells_you_it_is_still_in_the_tray(self):
        window, tray = self.make()
        window.close()
        window.show()
        window.close()
        self.assertEqual(len(tray.messages), 1)
        self.assertIn("tray", tray.messages[0][1])

    def test_without_a_tray_close_works_the_old_way(self):
        window, tray = self.make(available=False)
        window.close()
        self.assertFalse(window.isVisible())
        self.assertTrue(tray.hidden)
        self.assertEqual(tray.messages, [])

    # ----- the tray menu ---------------------------------------------------

    def test_quit_really_closes_the_app(self):
        window, tray = self.make()
        with mock.patch.object(QApplication, "quit") as quit_app:
            tray.quit_requested.emit()
        quit_app.assert_called_once()
        self.assertTrue(tray.hidden)
        self.assertFalse(window.isVisible())

    def test_quit_does_nothing_during_a_force_break(self):
        window, tray = self.make()
        self.end_focus(window)
        with mock.patch.object(QApplication, "quit") as quit_app:
            tray.quit_requested.emit()
        quit_app.assert_not_called()
        self.assertTrue(window._force_break_active)
        self.assertTrue(window._overlay.is_active)

    def test_quit_is_greyed_out_during_a_force_break_only(self):
        window, tray = self.make()
        self.assertTrue(tray.quit_enabled)
        self.end_focus(window)
        window._refresh()
        self.assertFalse(tray.quit_enabled)
        window._on_math_unlocked()  # leaving the break early
        self.assertTrue(tray.quit_enabled)

    def test_clicking_the_icon_brings_the_window_back(self):
        window, tray = self.make()
        window.close()
        self.assertFalse(window.isVisible())
        tray.show_requested.emit()
        self.assertTrue(window.isVisible())

    # ----- the tooltip -----------------------------------------------------

    def test_the_tooltip_shows_the_time_left(self):
        window, tray = self.make()
        self.assertIn("Focus", tray.tooltip)
        self.assertIn("(paused)", tray.tooltip)
        window._on_toggle()  # Start
        self.assertNotIn("paused", tray.tooltip)
        window._timer.tick(61)
        window._refresh()
        remaining = window._clock_label.text()
        self.assertIn(f"Focus {remaining}", tray.tooltip)

    def test_the_tooltip_follows_the_phase(self):
        window, tray = self.make()
        self.end_focus(window)
        window._refresh()
        self.assertIn("break", tray.tooltip)

    # ----- hidden in the tray while the timer works ------------------------

    def test_the_break_screen_still_opens_when_the_window_is_hidden(self):
        window, tray = self.make()
        window._on_toggle()  # Start
        window.close()
        self.end_focus(window)
        self.assertTrue(window._force_break_active)
        self.assertTrue(window._overlay.is_active)
        self.assertFalse(window.isVisible())

    def test_the_end_of_a_break_is_announced_from_the_tray(self):
        window, tray = self.make()
        self.end_focus(window)
        window.close()
        tray.messages.clear()
        window._announce(Phase.SHORT_BREAK)
        self.assertFalse(window._overlay.is_active)
        self.assertEqual(tray.messages[0][0], "Break is over")

    def test_no_tray_message_when_the_window_is_in_sight(self):
        window, tray = self.make()
        self.end_focus(window)
        window._announce(Phase.SHORT_BREAK)
        self.assertEqual(tray.messages, [])


class TrayIconTest(unittest.TestCase):
    def test_without_a_system_tray_nothing_breaks(self):
        with mock.patch(
            "pomodoro.ui.tray.QSystemTrayIcon.isSystemTrayAvailable",
            return_value=False,
        ):
            tray = TrayIcon()
        self.assertFalse(tray.available)
        # None of these may fail.
        tray.set_tooltip("x")
        tray.set_quit_enabled(False)
        tray.notify("a", "b")
        tray.hide()


if __name__ == "__main__":
    unittest.main()
