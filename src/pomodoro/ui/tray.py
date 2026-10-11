"""The system tray icon: the tomato next to the clock.

``TrayIcon`` shows the tomato, the time left when you hover over it, and a menu
with "Show window" and "Quit". It only shows things and sends signals. The main
window decides what happens (see ``tray_logic.py`` for the rules).

If this computer has no system tray, ``available`` is False and nothing is
shown, so the app keeps working the old way.
"""

from typing import Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from pomodoro.tray_logic import APP_NAME
from pomodoro.ui.app_icon import make_app_icon


class TrayIcon(QObject):
    show_requested = Signal()
    quit_requested = Signal()

    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._tray: Optional[QSystemTrayIcon] = None
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        self._menu = QMenu()
        self._show_action = QAction("Show window", self._menu)
        self._quit_action = QAction("Quit", self._menu)
        self._show_action.triggered.connect(self.show_requested)
        self._quit_action.triggered.connect(self.quit_requested)
        self._menu.addAction(self._show_action)
        self._menu.addSeparator()
        self._menu.addAction(self._quit_action)

        self._tray = QSystemTrayIcon(make_app_icon(), self)
        self._tray.setToolTip(APP_NAME)
        self._tray.setContextMenu(self._menu)
        self._tray.activated.connect(self._on_activated)
        self._tray.show()

    @property
    def available(self) -> bool:
        """True if there is a tray and the icon is in it."""
        return self._tray is not None

    # ----- what the main window calls --------------------------------------

    def set_tooltip(self, text: str) -> None:
        if self._tray is not None:
            self._tray.setToolTip(text)

    def set_quit_enabled(self, enabled: bool) -> None:
        """Quit is greyed out during a Force Break."""
        if self._tray is not None:
            self._quit_action.setEnabled(enabled)

    def notify(self, title: str, message: str) -> None:
        """A small pop-up from the tray (works while the window is hidden)."""
        if self._tray is not None:
            self._tray.showMessage(title, message, QSystemTrayIcon.Information, 5000)

    def hide(self) -> None:
        """Take the icon out of the tray (when the app quits)."""
        if self._tray is not None:
            self._tray.hide()

    # ----- internals -------------------------------------------------------

    def _on_activated(self, reason) -> None:
        """A click or double-click on the icon brings the window back."""
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            self.show_requested.emit()
