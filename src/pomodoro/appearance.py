"""Night and Day looks: the colors and the switching rules, without any windows.

The app has two looks. Night is the dark look the app always had (and the
default). Day is a light look for bright rooms. The choice is remembered in the
settings file. This file only holds the colors and the rules, so it is easy to
test. ``ui/theme.py`` turns a palette into the real style.

The full-screen break and pause screens always stay dark in both looks. They
show a picture with white text on top, and that only reads well on a dark layer.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class Appearance(Enum):
    NIGHT = "night"
    DAY = "day"


@dataclass(frozen=True)
class Palette:
    """All the colors of one look, as ``#rrggbb``."""

    background: str
    surface: str
    surface_hover: str
    surface_pressed: str
    border: str
    text: str
    text_muted: str
    text_disabled: str
    accent: str
    accent_hover: str
    accent_pressed: str
    on_accent: str  # the text on a button filled with the accent color


# The look the app had before day mode existed. Do not change these values.
NIGHT_PALETTE = Palette(
    background="#17171c",
    surface="#26262f",
    surface_hover="#31313d",
    surface_pressed="#3a3a49",
    border="#3a3a48",
    text="#f4f4f7",
    text_muted="#a3a3b3",
    text_disabled="#6c6c7a",
    accent="#4c8dff",
    accent_hover="#4285f4",  # a little darker, so the white text stays readable
    accent_pressed="#3a78e6",
    on_accent="#ffffff",
)

DAY_PALETTE = Palette(
    background="#f4f4f8",
    surface="#ffffff",
    surface_hover="#ececf3",
    surface_pressed="#e0e0ea",
    border="#cdcddb",
    text="#1b1b22",
    text_muted="#585868",
    text_disabled="#9a9aa8",
    accent="#2f6fe0",
    accent_hover="#2860c8",
    accent_pressed="#2150a8",
    on_accent="#ffffff",
)

_PALETTES = {
    Appearance.NIGHT: NIGHT_PALETTE,
    Appearance.DAY: DAY_PALETTE,
}


def palette_for(appearance: Appearance) -> Palette:
    return _PALETTES[appearance]


def toggled(appearance: Appearance) -> Appearance:
    """The other look: Night becomes Day and Day becomes Night."""
    return Appearance.DAY if appearance is Appearance.NIGHT else Appearance.NIGHT


def switch_label(appearance: Appearance) -> str:
    """The text of the switch button: it names the look you get by pressing it."""
    return "Day mode" if appearance is Appearance.NIGHT else "Night mode"


def appearance_from_name(name: Any) -> Appearance:
    """Read a saved name. Anything that is not a known look gives Night, so a
    damaged value never loses the rest of the settings."""
    if isinstance(name, str):
        for appearance in Appearance:
            if appearance.value == name:
                return appearance
    return Appearance.NIGHT


def _channel(value: int) -> float:
    c = value / 255
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def _luminance(color: str) -> float:
    red, green, blue = (int(color[i : i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * _channel(red) + 0.7152 * _channel(green) + 0.0722 * _channel(blue)


def contrast_ratio(first: str, second: str) -> float:
    """How well two ``#rrggbb`` colors can be told apart (WCAG): 1 is the same,
    21 is black on white. Normal text should have at least 4.5."""
    a, b = _luminance(first), _luminance(second)
    lighter, darker = max(a, b), min(a, b)
    return (lighter + 0.05) / (darker + 0.05)
