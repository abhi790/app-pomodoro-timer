"""Colors, fonts and sizes for the whole app, kept in one place.

Change the look here and every window follows. Sizes are in pixels.
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from pomodoro.appearance import NIGHT_PALETTE, Appearance, Palette, palette_for

FONT_FAMILY = "Segoe UI"

BREAK_GREEN = "#3c9d5d"


def build_style(palette: Palette) -> str:
    """The style sheet of the whole app, in the colors of one look (Night or
    Day, see ``appearance.py``)."""
    BACKGROUND = palette.background
    SURFACE = palette.surface
    SURFACE_HOVER = palette.surface_hover
    SURFACE_PRESSED = palette.surface_pressed
    BORDER = palette.border
    TEXT = palette.text
    TEXT_MUTED = palette.text_muted
    TEXT_DISABLED = palette.text_disabled
    ACCENT = palette.accent
    ACCENT_HOVER = palette.accent_hover
    ACCENT_PRESSED = palette.accent_pressed
    ON_ACCENT = palette.on_accent
    return f"""
QWidget {{
    background-color: {BACKGROUND};
    color: {TEXT};
    font-family: "{FONT_FAMILY}";
    font-size: 17px;
}}

QLabel {{
    background: transparent;
}}

QLabel#phase {{
    font-size: 30px;
    font-weight: 600;
}}

QLabel#clock {{
    font-size: 96px;
    font-weight: 700;
}}

QLabel#muted {{
    color: {TEXT_MUTED};
    font-size: 17px;
}}

QLabel#message {{
    font-size: 18px;
}}

QLabel#overlayTitle {{
    color: {BREAK_GREEN};
    font-size: 44px;
    font-weight: 600;
}}

QLabel#overlayClock {{
    font-size: 170px;
    font-weight: 700;
}}

/* The pause screen also has a tip and two buttons, so its clock is smaller
   than on the break screen. That way everything fits on a small laptop. */
QLabel#pauseClock {{
    font-size: 120px;
    font-weight: 700;
}}

QLabel#overlayCategory {{
    color: #d8d8e2;
    font-size: 24px;
    font-weight: 600;
}}

QLabel#overlayTip {{
    font-size: 36px;
}}

QLabel#overlayHint {{
    color: #c9c9d6;
    font-size: 20px;
}}

QLabel#overlayQuiz {{
    font-size: 44px;
    font-weight: 700;
}}

QWidget#overlayPanel {{
    background: transparent;
}}

QLineEdit {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 12px;
    min-height: 30px;
    font-size: 17px;
}}

QLineEdit:focus, QPlainTextEdit:focus {{
    border: 1px solid {ACCENT};
}}

QPlainTextEdit {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 17px;
}}

QLineEdit#overlayAnswer {{
    font-size: 32px;
    font-weight: 600;
}}

QCheckBox {{
    spacing: 10px;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border: 1px solid {BORDER};
    border-radius: 5px;
    background-color: {SURFACE};
}}

QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border: 1px solid {ACCENT};
}}

QPushButton {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 10px 20px;
    font-size: 18px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {SURFACE_HOVER};
}}

QPushButton:pressed {{
    background-color: {SURFACE_PRESSED};
}}

QPushButton:focus {{
    border: 1px solid {ACCENT};
}}

QPushButton:disabled {{
    color: {TEXT_DISABLED};
    background-color: {BACKGROUND};
    border: 1px solid {SURFACE};
}}

/* The main action (Start / Pause) is filled with the accent color. */
QPushButton#primary {{
    background-color: {ACCENT};
    border: 1px solid {ACCENT};
    color: {ON_ACCENT};
}}

QPushButton#primary:hover {{
    background-color: {ACCENT_HOVER};
    border: 1px solid {ACCENT_HOVER};
}}

QPushButton#primary:pressed {{
    background-color: {ACCENT_PRESSED};
    border: 1px solid {ACCENT_PRESSED};
}}

QPushButton#primary:disabled {{
    color: {TEXT_DISABLED};
    background-color: {BACKGROUND};
    border: 1px solid {SURFACE};
}}

/* TESTING ONLY: the Emergency exit on the break and pause screens. Quiet, so
   it does not look like the normal way out, but easy to find. */
QPushButton#emergencyExit {{
    background-color: rgba(120, 30, 30, 90);
    border: 1px solid rgba(232, 144, 141, 150);
    color: #f0b0ad;
    font-size: 15px;
    padding: 6px 18px;
}}

QPushButton#emergencyExit:hover {{
    background-color: rgba(160, 40, 40, 150);
}}

QPushButton#emergencyExit:pressed {{
    background-color: rgba(190, 50, 50, 190);
}}

/* The small Day / Night switch in the corner of the main window. */
QPushButton#themeToggle {{
    padding: 6px 16px;
    border-radius: 16px;
    font-size: 15px;
}}

/* Buttons on the pause screen sit on top of a picture, so they are a little
   see-through: you still see the picture through them. */
QPushButton#overlayButton {{
    background-color: rgba(38, 38, 47, 120);
    border: 1px solid rgba(255, 255, 255, 60);
}}

QPushButton#overlayButton:hover {{
    background-color: rgba(60, 60, 78, 170);
}}

QPushButton#overlayButton:pressed {{
    background-color: rgba(80, 80, 104, 200);
}}

QPushButton#overlayButton:focus {{
    border: 1px solid {ACCENT};
}}

QComboBox, QSpinBox {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 6px 12px;
    min-height: 30px;
    font-size: 17px;
}}

QComboBox:hover, QSpinBox:hover {{
    border: 1px solid {ACCENT};
}}

QSpinBox:disabled {{
    color: {TEXT_DISABLED};
    background-color: {BACKGROUND};
}}

QComboBox QAbstractItemView {{
    background-color: {SURFACE};
    border: 1px solid {BORDER};
    selection-background-color: {ACCENT};
    outline: 0;
}}
"""


# The look the app had before Day mode existed (and the default).
APP_STYLE = build_style(NIGHT_PALETTE)

# The full-screen break and pause screens always use this dark style, in both
# looks: they show white text over a picture.
SCREEN_STYLE = APP_STYLE


def apply_theme(app: QApplication, appearance: Appearance = Appearance.NIGHT) -> None:
    """Use the app-wide font and the colors of the chosen look. Can be called
    again at any time: every window changes at once."""
    app.setFont(QFont(FONT_FAMILY, 12))
    app.setStyleSheet(build_style(palette_for(appearance)))
