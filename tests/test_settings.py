import json
import tempfile
import unittest
from pathlib import Path

from pomodoro.settings import (
    PRESETS,
    AppConfig,
    Mode,
    load_config,
    save_config,
)
from pomodoro.timer_logic import TimerSettings


class AppConfigTest(unittest.TestCase):
    def test_default_is_custom_with_default_times(self):
        config = AppConfig()
        self.assertEqual(config.mode, Mode.CUSTOM)
        self.assertEqual(config.timer_settings(), TimerSettings())

    def test_break_reminder_preset(self):
        s = AppConfig(mode=Mode.BREAK_REMINDER).timer_settings()
        self.assertEqual(s.focus_minutes, 25)
        self.assertEqual(s.short_break_minutes, 5)

    def test_force_break_preset(self):
        s = AppConfig(mode=Mode.FORCE_BREAK).timer_settings()
        self.assertEqual(s.focus_minutes, 45)
        self.assertEqual(s.short_break_minutes, 10)

    def test_custom_uses_the_custom_times(self):
        custom = TimerSettings(focus_minutes=50, short_break_minutes=10)
        config = AppConfig(mode=Mode.CUSTOM, custom=custom)
        self.assertEqual(config.timer_settings(), custom)

    def test_presets_do_not_touch_custom_times(self):
        custom = TimerSettings(focus_minutes=50)
        config = AppConfig(mode=Mode.FORCE_BREAK, custom=custom)
        self.assertEqual(config.timer_settings(), PRESETS[Mode.FORCE_BREAK])
        self.assertEqual(config.custom, custom)


class SaveAndLoadTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "PomodoroTimer" / "settings.json"

    def test_round_trip(self):
        config = AppConfig(
            mode=Mode.FORCE_BREAK,
            custom=TimerSettings(focus_minutes=40, long_break_minutes=30),
        )
        save_config(config, self.path)
        self.assertEqual(load_config(self.path), config)

    def test_missing_file_gives_defaults(self):
        self.assertEqual(load_config(self.path), AppConfig())

    def test_broken_json_gives_defaults(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{ not json", encoding="utf-8")
        self.assertEqual(load_config(self.path), AppConfig())

    def test_unknown_mode_gives_defaults(self):
        self.path.parent.mkdir(parents=True)
        data = AppConfig().to_dict()
        data["mode"] = "something_else"
        self.path.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(load_config(self.path), AppConfig())

    def test_invalid_times_give_defaults(self):
        self.path.parent.mkdir(parents=True)
        data = AppConfig().to_dict()
        data["custom"]["focus_minutes"] = 0
        self.path.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(load_config(self.path), AppConfig())

    def test_missing_keys_give_defaults(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps({"mode": "custom"}), encoding="utf-8")
        self.assertEqual(load_config(self.path), AppConfig())

    def test_your_ideas_are_saved_and_loaded(self):
        config = AppConfig(ideas=("Juggle three socks", "Write a limerick"))
        save_config(config, self.path)
        self.assertEqual(load_config(self.path).ideas, config.ideas)

    def test_old_file_without_ideas_still_loads(self):
        self.path.parent.mkdir(parents=True)
        data = AppConfig(mode=Mode.FORCE_BREAK).to_dict()
        del data["ideas"]
        self.path.write_text(json.dumps(data), encoding="utf-8")
        loaded = load_config(self.path)
        self.assertEqual(loaded.mode, Mode.FORCE_BREAK)
        self.assertEqual(loaded.ideas, ())

    def test_saved_ideas_are_tidied_when_loaded(self):
        self.path.parent.mkdir(parents=True)
        data = AppConfig().to_dict()
        data["ideas"] = ["  paint   a rock ", "", "Paint a rock"]
        self.path.write_text(json.dumps(data), encoding="utf-8")
        self.assertEqual(load_config(self.path).ideas, ("paint a rock",))

    def test_ideas_of_the_wrong_type_give_defaults(self):
        self.path.parent.mkdir(parents=True)
        for bad in ("just text", 5, [1, 2]):
            data = AppConfig().to_dict()
            data["ideas"] = bad
            self.path.write_text(json.dumps(data), encoding="utf-8")
            self.assertEqual(load_config(self.path), AppConfig(), bad)


if __name__ == "__main__":
    unittest.main()
