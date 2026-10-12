import os
import unittest

# Run without a real screen if nobody chose a Qt platform already.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QRect
from PySide6.QtWidgets import QApplication, QDialogButtonBox, QWidget

from pomodoro.settings import AppConfig, Mode
from pomodoro.ui.settings_dialog import SettingsDialog
from pomodoro.window_fit import EDGE_MARGIN

_app = QApplication.instance() or QApplication([])


class SettingsDialogFitTest(unittest.TestCase):
    """The Settings window must always be fully on the screen, with Save and
    Cancel in sight (it used to hang below the taskbar)."""

    def setUp(self):
        self.keep_alive = []

    def tearDown(self):
        for widget in self.keep_alive:
            widget.close()
            widget.deleteLater()
        _app.processEvents()

    def available(self) -> QRect:
        return _app.primaryScreen().availableGeometry()

    def show_dialog(self, parent=None, config=None) -> SettingsDialog:
        dialog = SettingsDialog(config or AppConfig(mode=Mode.CUSTOM), parent)
        self.keep_alive.append(dialog)
        dialog.show()
        _app.processEvents()
        _app.processEvents()
        return dialog

    def make_parent(self, x: int, y: int, width=420, height=300) -> QWidget:
        parent = QWidget()
        parent.setGeometry(x, y, width, height)
        self.keep_alive.append(parent)
        parent.show()
        _app.processEvents()
        return parent

    def assert_on_screen(self, dialog):
        area = self.available()
        frame = dialog.frameGeometry()
        self.assertTrue(
            area.contains(frame),
            f"window {frame} is not inside the screen {area}",
        )

    def test_without_a_parent_the_window_is_on_the_screen(self):
        self.assert_on_screen(self.show_dialog())

    def test_a_main_window_at_the_bottom_does_not_push_it_below_the_taskbar(self):
        area = self.available()
        parent = self.make_parent(100, area.bottom() - 200)
        self.assert_on_screen(self.show_dialog(parent))

    def test_a_main_window_at_the_top_keeps_the_title_bar_visible(self):
        parent = self.make_parent(100, 0)
        dialog = self.show_dialog(parent)
        self.assert_on_screen(dialog)
        self.assertGreaterEqual(dialog.frameGeometry().top(), self.available().top())

    def test_a_main_window_at_the_right_edge_is_handled(self):
        area = self.available()
        parent = self.make_parent(area.right() - 200, 100)
        self.assert_on_screen(self.show_dialog(parent))

    def test_the_window_is_never_taller_than_the_screen(self):
        dialog = self.show_dialog()
        self.assertLessEqual(
            dialog.frameGeometry().height(), self.available().height() - 2 * EDGE_MARGIN
        )

    def test_save_and_cancel_are_inside_the_window(self):
        area = self.available()
        parent = self.make_parent(100, area.bottom() - 200)
        dialog = self.show_dialog(parent)
        buttons = dialog.findChild(QDialogButtonBox)
        self.assertIsNotNone(buttons)
        top_left = buttons.mapTo(dialog, buttons.rect().topLeft())
        bottom_right = buttons.mapTo(dialog, buttons.rect().bottomRight())
        self.assertTrue(dialog.rect().contains(top_left))
        self.assertTrue(dialog.rect().contains(bottom_right))
        # ... and the window itself is on the screen, so the buttons are too.
        self.assert_on_screen(dialog)
        self.assertTrue(buttons.isVisible())

    def test_the_rest_of_the_window_scrolls_when_it_is_cut(self):
        dialog = self.show_dialog()
        scroll = dialog._scroll
        needed = dialog._content.sizeHint().height()
        if needed > scroll.viewport().height():
            self.assertGreater(scroll.verticalScrollBar().maximum(), 0)

    def test_showing_it_again_is_also_on_the_screen(self):
        area = self.available()
        parent = self.make_parent(100, area.bottom() - 200)
        dialog = self.show_dialog(parent)
        dialog.hide()
        parent.move(300, area.bottom() - 100)
        _app.processEvents()
        dialog.show()
        _app.processEvents()
        _app.processEvents()
        self.assert_on_screen(dialog)


if __name__ == "__main__":
    unittest.main()
