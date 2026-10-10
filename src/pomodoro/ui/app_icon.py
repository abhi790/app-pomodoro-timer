"""The app icon: a little tomato ("pomodoro" means tomato in Italian).

The icon is drawn with code, so there is no picture file to carry around and
no copyright question. ``draw_tomato`` makes one image of any size (easy to
test). ``make_app_icon`` packs several sizes into one icon, so the window
corner, the taskbar and Alt+Tab each get a sharp picture.

``set_windows_app_id`` tells Windows that this is its own app. Without it,
the taskbar shows the Python icon when you start the app with ``python run.py``.
"""

import math
import sys

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QImage,
    QPainter,
    QPen,
    QPixmap,
    QPolygonF,
    QRadialGradient,
)

# Sizes Windows asks for: title bar, taskbar, Alt+Tab, large icons.
ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)

APP_ID = "abhi790.PomodoroTimer"

# Colors of the tomato.
BODY_LIGHT = "#ff6a57"
BODY_MID = "#e03a2e"
BODY_DARK = "#b3261e"
LEAF = "#3f9b4a"
STEM = "#2f7d3a"


def draw_tomato(size: int) -> QImage:
    """Draw the tomato on a transparent square image of ``size`` pixels."""
    image = QImage(size, size, QImage.Format_ARGB32_Premultiplied)
    image.fill(Qt.transparent)

    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.scale(size / 100.0, size / 100.0)  # draw on a 100 x 100 sheet
    painter.setPen(Qt.NoPen)

    # Round red body with a soft light from the top left.
    glow = QRadialGradient(QPointF(38, 44), 62)
    glow.setColorAt(0.0, QColor(BODY_LIGHT))
    glow.setColorAt(0.6, QColor(BODY_MID))
    glow.setColorAt(1.0, QColor(BODY_DARK))
    painter.setBrush(QBrush(glow))
    painter.drawEllipse(QRectF(10, 20, 80, 72))

    # A small shine.
    painter.setBrush(QColor(255, 255, 255, 90))
    painter.save()
    painter.translate(32, 44)
    painter.rotate(-30)
    painter.drawEllipse(QRectF(-9, -5, 18, 10))
    painter.restore()

    # Green leaves on top: a five-pointed star.
    star = QPolygonF()
    for i in range(10):
        radius = 19 if i % 2 == 0 else 7
        angle = math.radians(-90 + i * 36)
        star.append(QPointF(50 + radius * math.cos(angle), 28 + radius * math.sin(angle)))
    painter.setBrush(QColor(LEAF))
    painter.drawPolygon(star)

    # A short stem.
    painter.setPen(QPen(QColor(STEM), 6, Qt.SolidLine, Qt.RoundCap))
    painter.drawLine(QPointF(50, 24), QPointF(50, 10))

    painter.end()
    return image


def make_app_icon() -> QIcon:
    """The tomato in all the sizes in ``ICON_SIZES``. Needs a running app."""
    icon = QIcon()
    for size in ICON_SIZES:
        icon.addPixmap(QPixmap.fromImage(draw_tomato(size)))
    return icon


def set_windows_app_id() -> None:
    """On Windows, make the taskbar use our icon instead of Python's.

    Call this before the first window is created. It does nothing on other
    systems, and it never stops the app from starting.
    """
    if sys.platform != "win32":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
    except (AttributeError, OSError):
        pass
