import os
import unittest
from unittest import mock

# Run without a real screen if nobody chose a Qt platform already.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from pomodoro.appearance import DAY_PALETTE, NIGHT_PALETTE, Appearance
from pomodoro.settings import AppConfig
from pomodoro.ui.break_overlay import BreakOverlay
from pomodoro.ui.main_window import MainWindow
from pomodoro.ui.pause_overlay import PauseOverlay
from pomodoro.ui.settings_dialog import SettingsDialog
from pomodoro.ui.theme import apply_theme, build_style

_app = QApplication.instance() or QApplication([])
apply_theme(_app, Appearance.NIGHT)


class StyleTest(unittest.TestCase):
    def tearDown(self):
        apply_theme(_app, Appearance.NIGHT)

    def test_the_style_uses_the_colors_of_the_palette(self):
        for palette in (NIGHT_PALETTE, DAY_PALETTE):
            style = build_style(palette)
            for color in (palette.background, palette.surface, palette.text, palette.accent):
                self.assertIn(color, style)

    def test_day_does_not_use_the_night_background(self):
        self.assertNotIn(NIGHT_PALETTE.background, build_style(DAY_PALETTE))

    def test_apply_theme_sets_the_style_of_the_app(self):
        apply_theme(_app, Appearance.DAY)
        self.assertEqual(_app.styleSheet(), build_style(DAY_PALETTE))
        apply_theme(_app, Appearance.NIGHT)
        self.assertEqual(_app.styleSheet(), build_style(NIGHT_PALETTE))

    def test_night_is_the_default(self):
        apply_theme(_app)
        self.assertEqual(_app.styleSheet(), build_style(NIGHT_PALETTE))


class SwitchButtonTest(unittest.TestCase):
    """The Day / Night button on the main window."""

    def setUp(self):
        patcher = mock.patch("pomodoro.ui.main_window.save_config")
        self.save = patcher.start()
        self.addCleanup(patcher.stop)
        self.windows = []

    def tearDown(self):
        for window in self.windows:
            window._quitting = True
            window.close()
            window.deleteLater()
        _app.processEvents()
        apply_theme(_app, Appearance.NIGHT)

    def make_window(self, config=None) -> MainWindow:
        window = MainWindow(config or AppConfig())
        self.windows.append(window)
        window.resize(520, 640)
        window.show()
        _app.processEvents()
        return window

    def test_the_button_is_there_and_names_the_other_look(self):
        window = self.make_window()
        self.assertEqual(window._look_button.text(), "Day mode")
        self.assertTrue(window._look_button.isVisible())
        self.assertTrue(window._look_button.isEnabled())

    def test_a_window_saved_in_day_offers_night(self):
        window = self.make_window(AppConfig(appearance=Appearance.DAY))
        self.assertEqual(window._look_button.text(), "Night mode")

    def test_pressing_it_switches_the_whole_app_at_once(self):
        window = self.make_window()
        window._look_button.click()
        self.assertEqual(_app.styleSheet(), build_style(DAY_PALETTE))
        self.assertEqual(window._look_button.text(), "Night mode")
        self.assertIs(window._config.appearance, Appearance.DAY)

    def test_pressing_it_again_goes_back_to_night(self):
        window = self.make_window()
        window._look_button.click()
        window._look_button.click()
        self.assertEqual(_app.styleSheet(), build_style(NIGHT_PALETTE))
        self.assertEqual(window._look_button.text(), "Day mode")
        self.assertIs(window._config.appearance, Appearance.NIGHT)

    def test_the_choice_is_saved(self):
        window = self.make_window()
        window._look_button.click()
        self.save.assert_called_once()
        saved = self.save.call_args.args[0]
        self.assertIs(saved.appearance, Appearance.DAY)

    def test_the_other_settings_are_kept_when_it_is_saved(self):
        config = AppConfig(sound_enabled=False, ideas=("Paint a rock",))
        window = self.make_window(config)
        window._look_button.click()
        saved = self.save.call_args.args[0]
        self.assertFalse(saved.sound_enabled)
        self.assertEqual(saved.ideas, ("Paint a rock",))
        self.assertEqual(saved.timer_settings(), config.timer_settings())

    def test_a_save_problem_does_not_stop_the_switch(self):
        self.save.side_effect = OSError("disk full")
        window = self.make_window()
        window._look_button.click()
        self.assertEqual(_app.styleSheet(), build_style(DAY_PALETTE))
        self.assertIn("Could not save", window._message_label.text())

    def test_it_works_while_the_timer_runs_and_does_not_touch_the_timer(self):
        window = self.make_window()
        window._on_toggle()  # Start
        self.assertTrue(window._timer.running)
        before = window._timer.remaining_seconds
        window._look_button.click()
        self.assertTrue(window._timer.running)
        self.assertEqual(window._timer.remaining_seconds, before)
        self.assertEqual(_app.styleSheet(), build_style(DAY_PALETTE))

    def test_the_settings_window_keeps_the_look_when_you_press_save(self):
        dialog = SettingsDialog(AppConfig(appearance=Appearance.DAY))
        self.addCleanup(dialog.deleteLater)
        self.assertIs(dialog.result_config().appearance, Appearance.DAY)


class ScreensStayDarkTest(unittest.TestCase):
    """The break and pause screens show white text over a picture, so they
    must stay dark even when the app is in Day mode."""

    def setUp(self):
        self.widgets = []

    def tearDown(self):
        for widget in self.widgets:
            widget.close()
            widget.deleteLater()
        _app.processEvents()
        apply_theme(_app, Appearance.NIGHT)

    def test_the_break_screen_has_its_own_dark_style(self):
        apply_theme(_app, Appearance.DAY)
        overlay = BreakOverlay()
        self.widgets.append(overlay)
        self.assertEqual(overlay.styleSheet(), build_style(NIGHT_PALETTE))

    def test_the_pause_screen_has_its_own_dark_style(self):
        apply_theme(_app, Appearance.DAY)
        overlay = PauseOverlay()
        self.widgets.append(overlay)
        self.assertEqual(overlay.styleSheet(), build_style(NIGHT_PALETTE))


if __name__ == "__main__":
    unittest.main()
