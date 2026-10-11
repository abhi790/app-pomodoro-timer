"""Colors, fonts and sizes for the whole app, kept in one place.

Change the look here and every window follows. Sizes are in pixels.
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

FONT_FAMILY = "Segoe UI"

BACKGROUND = "#17171c"
SURFACE = "#26262f"
SURFACE_HOVER = "#31313d"
SURFACE_PRESSED = "#3a3a49"
BORDER = "#3a3a48"
TEXT = "#f4f4f7"
TEXT_MUTED = "#a3a3b3"
TEXT_DISABLED = "#6c6c7a"
ACCENT = "#4c8dff"
BREAK_GREEN = "#3c9d5d"

APP_STYLE = f"""
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

QPushButton#emergencyButton {{
    font-size: 16px;
    padding: 6px 14px;
    color: #c9c9d6;
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


def apply_theme(app: QApplication) -> None:
    """Use the app-wide font and colors."""
    app.setFont(QFont(FONT_FAMILY, 12))
    app.setStyleSheet(APP_STYLE)
