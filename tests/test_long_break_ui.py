import os
import random
import unittest

# Run without a real screen if nobody chose a Qt platform already.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from pomodoro.ideas import CREATIVE_IDEAS, IDEA_CATEGORY, IdeaRotator
from pomodoro.settings import AppConfig
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

    def test_test_mode_can_show_a_long_break(self):
        manager = make_manager()
        self.addCleanup(manager.hide)
        manager.show_test(60, 3, long_break=True)
        self.assertEqual(manager._tip.category, IDEA_CATEGORY)


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

    def test_mode_and_times_are_still_returned(self):
        config = AppConfig()
        dialog = SettingsDialog(config)
        result = dialog.result_config()
        self.assertEqual(result.mode, config.mode)
        self.assertEqual(result.custom, config.custom)


if __name__ == "__main__":
    unittest.main()
