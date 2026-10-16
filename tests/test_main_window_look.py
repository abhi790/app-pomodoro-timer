import os
import unittest

# Run without a real screen if nobody chose a Qt platform already.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from pomodoro.settings import AppConfig
from pomodoro.ui.main_window import MainWindow
from pomodoro.ui.theme import APP_STYLE, apply_theme

_app = QApplication.instance() or QApplication([])
apply_theme(_app)

# How different the free space above the timer and below it may be (pixels).
CENTER_TOLERANCE = 40


class MainWindowLookTest(unittest.TestCase):
    """The main window's look: Start stands out, and the timer is not stuck to
    the top with a big hole above the buttons."""

    def setUp(self):
        self.window = MainWindow(AppConfig())
        self.window.resize(520, 640)
        self.window.show()
        _app.processEvents()
        _app.processEvents()

    def tearDown(self):
        self.window._quitting = True
        self.window.close()
        self.window.deleteLater()
        _app.processEvents()

    def test_start_is_the_main_button(self):
        self.assertEqual(self.window._toggle_button.objectName(), "primary")

    def test_settings_is_a_normal_button(self):
        self.assertNotEqual(self.window._settings_button.objectName(), "primary")

    def test_the_theme_has_a_style_for_the_main_button(self):
        self.assertIn("QPushButton#primary", APP_STYLE)

    def test_the_timer_is_centered_between_the_corner_button_and_the_buttons(self):
        w = self.window
        # The small Day / Night switch is at the top, so measure from under it.
        free_above = w._phase_label.geometry().top() - w._look_button.geometry().bottom()
        free_below = w._toggle_button.geometry().top() - w._message_label.geometry().bottom()
        self.assertLessEqual(
            abs(free_above - free_below),
            CENTER_TOLERANCE,
            f"free space above the timer {free_above}px, below it {free_below}px",
        )


if __name__ == "__main__":
    unittest.main()
