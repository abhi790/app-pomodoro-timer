import os
import random
import tempfile
import unittest
from pathlib import Path
from unittest import mock

# Run without a real screen if nobody chose a Qt platform already.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from pomodoro.backgrounds import BackgroundPicker
from pomodoro.fit_text import TIP_FONT_SIZES
from pomodoro.settings import AppConfig, Mode
from pomodoro.timer_logic import Phase
from pomodoro.tips import CATEGORY_TITLE, HEALTHY_TIPS, Tip, TipRotator
from pomodoro.ui.main_window import MainWindow
from pomodoro.ui.pause_overlay import PauseCoverManager, PauseOverlay
from pomodoro.ui.theme import apply_theme
from pomodoro.usage import DAILY_MATH_LIMIT, UsageTracker
from tests.test_tray_ui import FakeSound, FakeTray

_app = QApplication.instance() or QApplication([])


class PauseWindowTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.keep_alive = []

    def make(self, math_used: int = 0) -> tuple:
        usage = UsageTracker(path=Path(self._tmp.name) / "usage.json")
        for _ in range(math_used):
            usage.record_math()
        tray = FakeTray()
        window = MainWindow(AppConfig(mode=Mode.CUSTOM), usage, FakeSound(), tray)
        self.keep_alive += [window, tray, usage]
        self.addCleanup(window._pause_cover.hide)
        self.addCleanup(window._overlay.hide)
        self.addCleanup(window.hide)
        window.show()
        return window, usage

    def start_and_pause(self, window, seconds: int = 120) -> None:
        window._on_toggle()  # Start
        window._timer.tick(seconds)
        window._on_toggle()  # Pause

    def cover(self, window):
        return window._pause_cover._overlays[0]

    def solve(self, overlay, correct: bool = True) -> None:
        overlay._stop_button.click()
        answer = overlay._problem.answer + (0 if correct else 1)
        overlay._answer_edit.setText(str(answer))
        overlay._check_button.click()

    # ----- Reset and Settings are locked while the timer works --------------

    def test_reset_and_settings_work_before_the_timer_starts(self):
        window, _ = self.make()
        self.assertTrue(window._reset_button.isEnabled())
        self.assertTrue(window._settings_button.isEnabled())

    def test_reset_and_settings_are_locked_once_the_timer_runs(self):
        window, _ = self.make()
        window._on_toggle()  # Start
        self.assertFalse(window._reset_button.isEnabled())
        self.assertFalse(window._settings_button.isEnabled())

    def test_the_locked_buttons_do_nothing_even_if_called(self):
        window, _ = self.make()
        window._on_toggle()
        window._timer.tick(100)
        left = window._timer.remaining_seconds
        window._on_reset()
        self.assertEqual(window._timer.remaining_seconds, left)
        with mock.patch("pomodoro.ui.main_window.SettingsDialog") as dialog:
            window._on_settings()
        dialog.assert_not_called()

    def test_they_stay_locked_while_the_pause_screen_is_up(self):
        window, _ = self.make()
        self.start_and_pause(window)
        self.assertFalse(window._reset_button.isEnabled())
        self.assertFalse(window._settings_button.isEnabled())

    # ----- Pause opens the pause screen -------------------------------------

    def test_pause_covers_every_monitor_and_stops_the_clock(self):
        window, _ = self.make()
        self.start_and_pause(window)
        self.assertFalse(window._timer.running)
        self.assertTrue(window._pause_cover.is_active)
        self.assertEqual(
            len(window._pause_cover._overlays), len(QGuiApplication.screens())
        )

    def test_time_does_not_pass_while_paused(self):
        window, _ = self.make()
        self.start_and_pause(window)
        left = window._timer.remaining_seconds
        window._last_tick -= 30
        window._on_clock_check()
        self.assertEqual(window._timer.remaining_seconds, left)

    def test_start_does_nothing_while_the_pause_screen_is_up(self):
        window, _ = self.make()
        self.start_and_pause(window)
        window._on_toggle()
        self.assertFalse(window._timer.running)

    def test_the_pause_screen_cannot_be_closed(self):
        window, _ = self.make()
        self.start_and_pause(window)
        overlay = self.cover(window)
        overlay.close()
        self.assertTrue(overlay.isVisible())

    def test_the_pause_screen_shows_the_time_left_and_the_unlocks_left(self):
        window, _ = self.make()
        self.start_and_pause(window, seconds=60)
        overlay = self.cover(window)
        self.assertEqual(overlay._clock_label.text(), window._clock_label.text())
        self.assertIn(f"{DAILY_MATH_LIMIT} of {DAILY_MATH_LIMIT}", overlay._status_label.text())

    # ----- Run --------------------------------------------------------------

    def test_run_carries_on_from_where_the_clock_stopped(self):
        window, _ = self.make()
        self.start_and_pause(window, seconds=300)
        left = window._timer.remaining_seconds
        self.cover(window)._run_button.click()
        self.assertTrue(window._timer.running)
        self.assertFalse(window._pause_cover.is_active)
        self.assertEqual(window._timer.remaining_seconds, left)

    def test_run_costs_nothing(self):
        window, usage = self.make()
        self.start_and_pause(window)
        self.cover(window)._run_button.click()
        self.assertEqual(usage.math_used, 0)

    def test_after_run_reset_and_settings_stay_locked(self):
        window, _ = self.make()
        self.start_and_pause(window)
        self.cover(window)._run_button.click()
        self.assertFalse(window._reset_button.isEnabled())
        self.assertFalse(window._settings_button.isEnabled())

    # ----- Stop (math) ------------------------------------------------------

    def test_stop_gives_a_math_problem_first(self):
        window, _ = self.make()
        self.start_and_pause(window)
        overlay = self.cover(window)
        overlay._stop_button.click()
        self.assertTrue(overlay._quiz.isVisibleTo(overlay))
        self.assertIn("=", overlay._problem_label.text())
        self.assertTrue(window._pause_cover.is_active)  # nothing happened yet

    def test_a_solved_problem_gives_up_the_block_and_stops_the_timer(self):
        window, usage = self.make()
        self.start_and_pause(window)
        self.solve(self.cover(window))
        self.assertFalse(window._pause_cover.is_active)
        self.assertFalse(window._timer.running)
        self.assertEqual(window._timer.phase, Phase.FOCUS)
        self.assertEqual(
            window._timer.remaining_seconds,
            window._config.timer_settings().focus_minutes * 60,
        )
        self.assertEqual(window._timer.completed_pomodoros, 0)
        self.assertEqual(usage.math_used, 1)

    def test_after_stop_reset_and_settings_work_again(self):
        window, _ = self.make()
        self.start_and_pause(window)
        self.solve(self.cover(window))
        self.assertTrue(window._reset_button.isEnabled())
        self.assertTrue(window._settings_button.isEnabled())
        self.assertIn("stopped", window._message_label.text())

    def test_a_wrong_answer_gives_a_new_problem_and_costs_nothing(self):
        window, usage = self.make()
        self.start_and_pause(window)
        self.solve(self.cover(window), correct=False)
        self.assertTrue(window._pause_cover.is_active)
        self.assertEqual(usage.math_used, 0)
        self.assertIn("Not quite", self.cover(window)._feedback_label.text())

    def test_back_returns_to_run_and_stop(self):
        window, _ = self.make()
        self.start_and_pause(window)
        overlay = self.cover(window)
        overlay._stop_button.click()
        overlay._back_button.click()
        self.assertTrue(overlay._menu.isVisibleTo(overlay))
        self.assertFalse(overlay._quiz.isVisibleTo(overlay))

    def test_stop_uses_the_same_three_daily_unlocks_as_a_break(self):
        window, usage = self.make(math_used=2)
        self.start_and_pause(window)
        overlay = self.cover(window)
        self.assertIn("1 of 3", overlay._status_label.text())
        self.solve(overlay)
        self.assertEqual(usage.math_left, 0)

    # ----- no math left -----------------------------------------------------

    def test_with_no_math_left_there_is_no_stop_button(self):
        window, _ = self.make(math_used=DAILY_MATH_LIMIT)
        self.start_and_pause(window)
        overlay = self.cover(window)
        self.assertFalse(overlay._stop_button.isVisibleTo(overlay))
        self.assertTrue(overlay._run_button.isVisibleTo(overlay))
        self.assertIn("No math unlocks left", overlay._status_label.text())

    def test_with_no_math_left_run_still_works(self):
        window, _ = self.make(math_used=DAILY_MATH_LIMIT)
        self.start_and_pause(window)
        self.cover(window)._run_button.click()
        self.assertTrue(window._timer.running)

    def test_the_third_stop_removes_stop_from_the_next_pause(self):
        window, usage = self.make(math_used=2)
        self.start_and_pause(window)
        self.solve(self.cover(window))  # the third unlock
        self.start_and_pause(window)
        overlay = self.cover(window)
        self.assertFalse(overlay._stop_button.isVisibleTo(overlay))

    # ----- Quit and breaks --------------------------------------------------

    def test_quit_is_locked_while_the_pause_screen_is_up(self):
        window, _ = self.make()
        self.start_and_pause(window)
        tray = window._tray
        with mock.patch.object(QApplication, "quit") as quit_app:
            tray.quit_requested.emit()
        quit_app.assert_not_called()
        self.assertFalse(tray.quit_enabled)

    def test_quit_works_again_after_run(self):
        window, _ = self.make()
        self.start_and_pause(window)
        self.cover(window)._run_button.click()
        self.assertTrue(window._tray.quit_enabled)

    def test_pause_does_not_open_during_a_force_break(self):
        window, _ = self.make()
        window._timer.start()
        window._timer.tick(window._timer.remaining_seconds)
        window._announce(Phase.FOCUS)  # the break starts
        window._on_toggle()
        self.assertFalse(window._pause_cover.is_active)
        self.assertTrue(window._timer.running)


def describe_tip(label, wanted: int) -> str:
    """Everything that decides how tall a tip is, for a failing test message
    (the same test can pass on one computer and fail on another, because fonts
    differ)."""
    font = label.font()
    return (
        f"wanted={wanted} box_height={label.height()} width={label.width()} "
        f"family={font.family()!r} px={font.pixelSize()} pt={font.pointSizeF()} "
        f"lineSpacing={label.fontMetrics().lineSpacing()} "
        f"chars={len(label.text())} sheet={label.styleSheet()!r}"
    )


class PauseTipsTest(unittest.TestCase):
    """The pause screen shows the same healthy tips as the break screen."""

    def make(self) -> PauseCoverManager:
        manager = PauseCoverManager(
            rotator=TipRotator(rng=random.Random(1)),
            picker=BackgroundPicker(rng=random.Random(1)),
        )
        self.addCleanup(manager.hide)
        self.keep_alive = manager
        return manager

    def test_a_tip_with_its_category_is_shown(self):
        manager = self.make()
        manager.show("20:00", 3)
        overlay = manager._overlays[0]
        self.assertEqual(overlay._tip_label.text(), manager._tip.text)
        self.assertEqual(
            overlay._category_label.text(),
            CATEGORY_TITLE[manager._tip.category].upper(),
        )

    def test_the_tip_is_a_healthy_tip(self):
        manager = self.make()
        manager.show("20:00", 3)
        self.assertIn(manager._tip, HEALTHY_TIPS)

    def test_every_monitor_shows_the_same_tip(self):
        manager = self.make()
        manager.show("20:00", 3)
        for _ in range(3):
            manager._show_next_tip()
            texts = {o._tip_label.text() for o in manager._overlays}
            self.assertEqual(texts, {manager._tip.text})

    def test_the_tips_take_turns(self):
        manager = self.make()
        manager.show("20:00", 3)
        seen = [manager._tip.text]
        for _ in range(5):
            manager._show_next_tip()
            seen.append(manager._tip.text)
        self.assertEqual(len(set(seen)), len(seen))

    def test_a_tip_timer_runs_while_the_screen_is_up_and_stops_after(self):
        manager = self.make()
        manager.show("20:00", 3)
        self.assertTrue(manager._tip_timer.isActive())
        manager.hide()
        self.assertFalse(manager._tip_timer.isActive())

    def test_a_new_pause_starts_with_a_new_tip(self):
        manager = self.make()
        manager.show("20:00", 3)
        first = manager._tip.text
        manager.hide()
        manager.show("20:00", 3)
        self.assertNotEqual(manager._tip.text, first)

    def test_the_buttons_are_the_see_through_kind(self):
        manager = self.make()
        manager.show("20:00", 3)
        overlay = manager._overlays[0]
        for button in (overlay._run_button, overlay._stop_button,
                       overlay._back_button, overlay._check_button):
            self.assertEqual(button.objectName(), "overlayButton")

    def test_no_tip_is_cut_off_on_a_small_laptop_screen(self):
        overlay = PauseOverlay()
        self.addCleanup(overlay.close_for_real)
        overlay.resize(1366, 768)
        overlay.show()
        apply_theme(_app)
        for tip in HEALTHY_TIPS:
            overlay.set_tip(tip, None, animate=False)
            _app.processEvents()
            label = overlay._tip_label
            wanted = label.fontMetrics().boundingRect(
                0, 0, label.width(), 10000,
                int(Qt.TextWordWrap | Qt.AlignCenter), tip.text,
            ).height()
            self.assertLessEqual(wanted, label.height(), describe_tip(label, wanted))

    def test_a_very_long_tip_gets_a_smaller_font_instead_of_being_cut_off(self):
        # Fonts differ between computers (and with the Windows display scale),
        # so a tip that is taller than the box must shrink, not be cut.
        overlay = PauseOverlay()
        self.addCleanup(overlay.close_for_real)
        overlay.resize(1366, 768)
        overlay.show()
        apply_theme(_app)
        text = "Sip water through the day, not only when you feel dry. " * 4
        overlay.set_tip(Tip("water", text), None, animate=False)
        _app.processEvents()
        label = overlay._tip_label
        wanted = label.fontMetrics().boundingRect(
            0, 0, label.width(), 10000,
            int(Qt.TextWordWrap | Qt.AlignCenter), text,
        ).height()
        self.assertLessEqual(wanted, label.height(), describe_tip(label, wanted))
        self.assertLess(label.font().pixelSize(), TIP_FONT_SIZES[0])

    def test_a_short_tip_keeps_the_normal_font_size(self):
        overlay = PauseOverlay()
        self.addCleanup(overlay.close_for_real)
        overlay.resize(1366, 768)
        overlay.show()
        apply_theme(_app)
        overlay.set_tip(Tip("water", "Drink some water."), None, animate=False)
        _app.processEvents()
        self.assertEqual(overlay._tip_label.font().pixelSize(), TIP_FONT_SIZES[0])

    def test_the_font_goes_back_to_normal_after_a_long_tip(self):
        overlay = PauseOverlay()
        self.addCleanup(overlay.close_for_real)
        overlay.resize(1366, 768)
        overlay.show()
        apply_theme(_app)
        long_text = "Sip water through the day, not only when you feel dry. " * 4
        overlay.set_tip(Tip("water", long_text), None, animate=False)
        overlay.set_tip(Tip("water", "Drink some water."), None, animate=False)
        _app.processEvents()
        self.assertEqual(overlay._tip_label.font().pixelSize(), TIP_FONT_SIZES[0])


if __name__ == "__main__":
    unittest.main()
