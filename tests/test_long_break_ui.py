import os
import random
import unittest

# Run without a real screen if nobody chose a Qt platform already.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from pomodoro.ideas import CREATIVE_IDEAS, IDEA_CATEGORY, IdeaRotator
from pomodoro.settings import AppConfig, Mode
from pomodoro.tips import TipRotator
from pomodoro.ui.break_manager import BreakOverlayManager
from pomodoro.ui.settings_dialog import SettingsDialog

_app = QApplication.instance() or QApplication([])


def make_manager(custom=()) -> BreakOverlayManager:
    return BreakOverlayManager(
        rotator=TipRotator(rng=random.Random(1)),
        idea_rotator=IdeaRotator(custom=custom, rng=random.Random(1)),
    )


class LongBreakManagerTest(unittest.TestCase):
    def test_long_break_starts_with_an_idea_then_alternates(self):
        manager = make_manager()
        self.addCleanup(manager.hide)
        manager.show("60:00", 3, long_break=True)
        kinds = [manager._tip.category == IDEA_CATEGORY]
        for _ in range(5):
            manager._show_next_tip()
            kinds.append(manager._tip.category == IDEA_CATEGORY)
        self.assertEqual(kinds, [True, False, True, False, True, False])

    def test_the_idea_comes_from_the_idea_list(self):
        manager = make_manager()
        self.addCleanup(manager.hide)
        manager.show("60:00", 3, long_break=True)
        self.assertIn(manager._tip.text, CREATIVE_IDEAS)

    def test_your_own_ideas_can_show_up(self):
        mine = "Juggle three socks"
        manager = make_manager(custom=(mine,))
        self.addCleanup(manager.hide)
        manager.show("60:00", 3, long_break=True)
        seen = set()
        for _ in range((len(CREATIVE_IDEAS) + 1) * 2):
            if manager._tip.category == IDEA_CATEGORY:
                seen.add(manager._tip.text)
            manager._show_next_tip()
        self.assertIn(mine, seen)

    def test_set_custom_ideas_changes_the_ideas_used(self):
        manager = make_manager()
        manager.set_custom_ideas(["Juggle three socks"])
        self.addCleanup(manager.hide)
        manager.show("60:00", 3, long_break=True)
        seen = set()
        for _ in range((len(CREATIVE_IDEAS) + 1) * 2):
            if manager._tip.category == IDEA_CATEGORY:
                seen.add(manager._tip.text)
            manager._show_next_tip()
        self.assertIn("Juggle three socks", seen)

    def test_short_break_never_shows_creative_ideas(self):
        manager = make_manager()
        self.addCleanup(manager.hide)
        manager.show("10:00", 3)
        for _ in range(30):
            self.assertNotEqual(manager._tip.category, IDEA_CATEGORY)
            manager._show_next_tip()

    def test_the_next_break_starts_fresh(self):
        manager = make_manager()
        manager.show("60:00", 3, long_break=True)
        manager.hide()
        manager.show("10:00", 3)
        self.addCleanup(manager.hide)
        for _ in range(10):
            self.assertNotEqual(manager._tip.category, IDEA_CATEGORY)
            manager._show_next_tip()

class UnlockSignalsTest(unittest.TestCase):
    """The break screen only passes on what the user chose. Nothing else."""

    def test_a_solved_problem_reaches_the_main_window(self):
        manager = make_manager()
        self.addCleanup(manager.hide)
        got = []
        manager.math_unlocked.connect(lambda: got.append(1))
        manager.show("10:00", 3)
        manager._overlays[0].math_solved.emit()
        self.assertEqual(got, [1])

    def test_the_important_button_reaches_the_main_window(self):
        manager = make_manager()
        self.addCleanup(manager.hide)
        got = []
        manager.important_chosen.connect(lambda: got.append(1))
        manager.show("10:00", 0)
        manager._overlays[0].important_chosen.emit()
        self.assertEqual(got, [1])

    def test_with_no_math_left_the_screen_offers_important(self):
        manager = make_manager()
        self.addCleanup(manager.hide)
        manager.show("10:00", 0)
        panel = manager._overlays[0]._panel
        self.assertFalse(panel._leave_button.isVisibleTo(panel))
        self.assertTrue(panel._important_button.isVisibleTo(panel))

    def test_there_is_no_emergency_exit_any_more(self):
        manager = make_manager()
        self.addCleanup(manager.hide)
        manager.show("10:00", 3)
        panel = manager._overlays[0]._panel
        self.assertFalse(hasattr(panel, "emergency_chosen"))
        self.assertFalse(hasattr(manager, "emergency_exit"))


class SettingsDialogIdeasTest(unittest.TestCase):
    def test_shows_the_saved_ideas_one_per_line(self):
        dialog = SettingsDialog(AppConfig(ideas=("Paint a rock", "Bake bread")))
        self.assertEqual(
            dialog._ideas_edit.toPlainText(), "Paint a rock\nBake bread"
        )

    def test_result_has_the_ideas_typed_in_the_box(self):
        dialog = SettingsDialog(AppConfig())
        dialog._ideas_edit.setPlainText("  Paint a rock \n\nBake bread\npaint a ROCK")
        self.assertEqual(
            dialog.result_config().ideas, ("Paint a rock", "Bake bread")
        )

    def test_empty_box_gives_no_ideas(self):
        dialog = SettingsDialog(AppConfig(ideas=("Paint a rock",)))
        dialog._ideas_edit.setPlainText("")
        self.assertEqual(dialog.result_config().ideas, ())

    def test_focus_and_break_boxes_follow_the_limits(self):
        dialog = SettingsDialog(AppConfig())
        self.assertEqual(dialog._focus.maximum(), 45)
        self.assertEqual(dialog._short_break.minimum(), 5)

    def test_long_break_is_shown_but_cannot_be_changed(self):
        for mode in Mode:
            dialog = SettingsDialog(AppConfig(mode=mode))
            self.assertFalse(dialog._long_break.isEnabled(), mode)
            self.assertFalse(dialog._cycle.isEnabled(), mode)
            self.assertEqual(dialog._long_break.value(), 60, mode)
            self.assertEqual(dialog._cycle.value(), 4, mode)

    def test_custom_focus_and_short_break_can_be_changed(self):
        dialog = SettingsDialog(AppConfig(mode=Mode.CUSTOM))
        self.assertTrue(dialog._focus.isEnabled())
        self.assertTrue(dialog._short_break.isEnabled())
        dialog._focus.setValue(40)
        dialog._short_break.setValue(8)
        result = dialog.result_config().timer_settings()
        self.assertEqual((result.focus_minutes, result.short_break_minutes), (40, 8))

    def test_a_focus_over_45_cannot_be_typed_in(self):
        dialog = SettingsDialog(AppConfig(mode=Mode.CUSTOM))
        dialog._focus.setValue(90)
        self.assertEqual(dialog.result_config().timer_settings().focus_minutes, 45)

    def test_mode_and_times_are_still_returned(self):
        config = AppConfig()
        dialog = SettingsDialog(config)
        result = dialog.result_config()
        self.assertEqual(result.mode, config.mode)
        self.assertEqual(result.custom, config.custom)


if __name__ == "__main__":
    unittest.main()
