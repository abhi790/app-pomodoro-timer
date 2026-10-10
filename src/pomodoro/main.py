"""Starts the app."""

import sys

from PySide6.QtWidgets import QApplication

from pomodoro.settings import load_config
from pomodoro.ui.main_window import MainWindow
from pomodoro.ui.theme import apply_theme


def main() -> int:
    app = QApplication(sys.argv)
    apply_theme(app)
    window = MainWindow(load_config())
    window.show()
    return app.exec()
