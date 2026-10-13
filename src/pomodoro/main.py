"""Starts the app."""

import sys

from PySide6.QtWidgets import QApplication

from pomodoro.settings import load_config
from pomodoro.ui.app_icon import make_app_icon, set_windows_app_id
from pomodoro.ui.main_window import MainWindow
from pomodoro.ui.theme import apply_theme


def main() -> int:
    set_windows_app_id()  # so the taskbar shows our icon, not Python's
    app = QApplication(sys.argv)
    # The window hides to the tray when closed, and the break screens come and
    # go, so the app must not quit just because no window is open.
    app.setQuitOnLastWindowClosed(False)
    app.setWindowIcon(make_app_icon())  # window corner, taskbar, Alt+Tab
    config = load_config()
    apply_theme(app, config.appearance)  # Night or Day, as you left it
    window = MainWindow(config)
    window.show()
    return app.exec()
