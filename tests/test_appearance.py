import json
import re
import tempfile
import unittest
from dataclasses import fields
from pathlib import Path

from pomodoro.appearance import (
    DAY_PALETTE,
    NIGHT_PALETTE,
    Appearance,
    appearance_from_name,
    contrast_ratio,
    palette_for,
    switch_label,
    toggled,
)
from pomodoro.settings import AppConfig, Mode, load_config, save_config

HEX_COLOR = re.compile(r"^#[0-9a-f]{6}$")


class TogglingTest(unittest.TestCase):
    def test_night_is_the_default_look(self):
        self.assertIs(AppConfig().appearance, Appearance.NIGHT)

    def test_toggling_switches_between_night_and_day(self):
        self.assertIs(toggled(Appearance.NIGHT), Appearance.DAY)
        self.assertIs(toggled(Appearance.DAY), Appearance.NIGHT)

    def test_toggling_twice_gives_the_same_look_back(self):
        for look in Appearance:
            self.assertIs(toggled(toggled(look)), look)

    def test_the_button_names_what_it_will_switch_to(self):
        self.assertEqual(switch_label(Appearance.NIGHT), "Day mode")
        self.assertEqual(switch_label(Appearance.DAY), "Night mode")

    def test_every_look_has_a_palette(self):
        self.assertIs(palette_for(Appearance.NIGHT), NIGHT_PALETTE)
        self.assertIs(palette_for(Appearance.DAY), DAY_PALETTE)


class NameTest(unittest.TestCase):
    def test_known_names(self):
        self.assertIs(appearance_from_name("day"), Appearance.DAY)
        self.assertIs(appearance_from_name("night"), Appearance.NIGHT)

    def test_anything_else_is_night(self):
        for bad in (None, "", "blue", "DAY ", 5, ["day"], {"a": 1}, True):
            self.assertIs(appearance_from_name(bad), Appearance.NIGHT, repr(bad))


class PaletteTest(unittest.TestCase):
    def test_all_colors_are_plain_hex_codes(self):
        for palette in (NIGHT_PALETTE, DAY_PALETTE):
            for field in fields(palette):
                value = getattr(palette, field.name)
                self.assertRegex(value, HEX_COLOR, f"{field.name}={value}")

    def test_contrast_ratio_known_values(self):
        self.assertAlmostEqual(contrast_ratio("#000000", "#ffffff"), 21.0, places=1)
        self.assertAlmostEqual(contrast_ratio("#ffffff", "#ffffff"), 1.0, places=2)
        # The order of the two colors does not matter.
        self.assertAlmostEqual(
            contrast_ratio("#17171c", "#f4f4f7"), contrast_ratio("#f4f4f7", "#17171c")
        )

    def test_the_text_is_easy_to_read_in_both_looks(self):
        for name, palette in (("night", NIGHT_PALETTE), ("day", DAY_PALETTE)):
            for ground in (palette.background, palette.surface):
                self.assertGreaterEqual(
                    contrast_ratio(palette.text, ground), 7.0, f"{name} text"
                )
                self.assertGreaterEqual(
                    contrast_ratio(palette.text_muted, ground), 4.5, f"{name} muted"
                )

    def test_the_text_on_the_main_button_is_readable(self):
        # The button text is bold and big, so 3:1 is enough, but day should do
        # better because its accent color is darker.
        for name, palette in (("night", NIGHT_PALETTE), ("day", DAY_PALETTE)):
            for ground in (palette.accent, palette.accent_hover, palette.accent_pressed):
                self.assertGreaterEqual(
                    contrast_ratio(palette.on_accent, ground), 3.0, f"{name} {ground}"
                )

    def test_day_is_really_lighter_than_night(self):
        self.assertGreater(
            contrast_ratio(DAY_PALETTE.background, "#000000"),
            contrast_ratio(NIGHT_PALETTE.background, "#000000") * 5,
        )

    def test_the_night_palette_is_the_old_look(self):
        # Night must stay exactly what the app looked like before day mode.
        self.assertEqual(NIGHT_PALETTE.background, "#17171c")
        self.assertEqual(NIGHT_PALETTE.surface, "#26262f")
        self.assertEqual(NIGHT_PALETTE.text, "#f4f4f7")
        self.assertEqual(NIGHT_PALETTE.accent, "#4c8dff")


class SavedAppearanceTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "settings.json"

    def test_the_choice_is_saved_and_loaded(self):
        save_config(AppConfig(appearance=Appearance.DAY), self.path)
        self.assertIs(load_config(self.path).appearance, Appearance.DAY)

    def test_it_is_written_in_the_file(self):
        self.assertEqual(
            AppConfig(appearance=Appearance.DAY).to_dict()["appearance"], "day"
        )
        self.assertEqual(AppConfig().to_dict()["appearance"], "night")

    def test_an_old_file_without_it_is_night(self):
        data = AppConfig(mode=Mode.POMODORO).to_dict()
        del data["appearance"]
        self.path.write_text(json.dumps(data), encoding="utf-8")
        loaded = load_config(self.path)
        self.assertIs(loaded.appearance, Appearance.NIGHT)
        self.assertIs(loaded.mode, Mode.POMODORO)  # the rest is kept

    def test_a_bad_value_is_night_and_does_not_lose_the_other_settings(self):
        for bad in ("blue", 7, None, ["day"]):
            data = AppConfig(mode=Mode.POMODORO, sound_enabled=False).to_dict()
            data["appearance"] = bad
            self.path.write_text(json.dumps(data), encoding="utf-8")
            loaded = load_config(self.path)
            self.assertIs(loaded.appearance, Appearance.NIGHT, repr(bad))
            self.assertIs(loaded.mode, Mode.POMODORO, repr(bad))
            self.assertFalse(loaded.sound_enabled, repr(bad))


if __name__ == "__main__":
    unittest.main()
