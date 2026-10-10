"""Starts the app."""

import sys

from PySide6.QtWidgets import QApplication

from pomodoro.settings import load_config
from pomodoro.ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow(load_config())
    window.show()
    return app.exec()
