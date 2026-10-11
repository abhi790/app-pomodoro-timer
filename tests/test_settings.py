import json
import tempfile
import unittest
from pathlib import Path

from pomodoro.settings import (
    LONG_BREAK_MINUTES,
    MAX_FOCUS_MINUTES,
    MIN_BREAK_MINUTES,
    POMODOROS_BEFORE_LONG_BREAK,
    PRESETS,
    AppConfig,
    Mode,
    load_config,
    save_config,
)
from pomodoro.timer_logic import Phase, PomodoroTimer, TimerSettings


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
        custom = TimerSettings(focus_minutes=40, short_break_minutes=10)
        config = AppConfig(mode=Mode.CUSTOM, custom=custom)
        self.assertEqual(config.timer_settings(), custom)

    def test_presets_do_not_touch_custom_times(self):
        custom = TimerSettings(focus_minutes=40)
        config = AppConfig(mode=Mode.FORCE_BREAK, custom=custom)
        self.assertEqual(config.timer_settings(), PRESETS[Mode.FORCE_BREAK])
        self.assertEqual(config.custom, custom)


class CustomLimitsTest(unittest.TestCase):
    def test_focus_is_at_most_45_minutes(self):
        config = AppConfig(custom=TimerSettings(focus_minutes=90))
        self.assertEqual(config.custom.focus_minutes, MAX_FOCUS_MINUTES)
        self.assertEqual(config.timer_settings().focus_minutes, 45)

    def test_45_minutes_of_focus_is_allowed(self):
        config = AppConfig(custom=TimerSettings(focus_minutes=45))
        self.assertEqual(config.custom.focus_minutes, 45)

    def test_short_break_is_at_least_5_minutes(self):
        config = AppConfig(custom=TimerSettings(short_break_minutes=2))
        self.assertEqual(config.custom.short_break_minutes, MIN_BREAK_MINUTES)
        self.assertEqual(config.timer_settings().short_break_minutes, 5)

    def test_a_longer_short_break_is_kept(self):
        config = AppConfig(custom=TimerSettings(short_break_minutes=20))
        self.assertEqual(config.custom.short_break_minutes, 20)

    def test_long_break_is_the_common_one_in_custom(self):
        config = AppConfig(
            custom=TimerSettings(
                long_break_minutes=15, pomodoros_before_long_break=2
            )
        )
        self.assertEqual(config.custom.long_break_minutes, LONG_BREAK_MINUTES)
        self.assertEqual(
            config.custom.pomodoros_before_long_break, POMODOROS_BEFORE_LONG_BREAK
        )

    def test_every_mode_has_the_same_long_break(self):
        for mode in Mode:
            s = AppConfig(mode=mode).timer_settings()
            self.assertEqual(s.long_break_minutes, 60, mode)
            self.assertEqual(s.pomodoros_before_long_break, 4, mode)

    def test_presets_stay_inside_the_limits(self):
        for settings in PRESETS.values():
            self.assertLessEqual(settings.focus_minutes, MAX_FOCUS_MINUTES)
            self.assertGreaterEqual(settings.short_break_minutes, MIN_BREAK_MINUTES)

    def test_the_long_break_comes_after_four_focus_blocks(self):
        # After focus blocks 1-3 comes a short break, after block 4 the long one.
        timer = PomodoroTimer(AppConfig(mode=Mode.CUSTOM).timer_settings())
        seen = []
        for _ in range(4):
            timer.start()
            timer.tick(timer.remaining_seconds)  # the focus block ends
            seen.append(timer.phase)  # the break that comes next
            timer.start()
            timer.tick(timer.remaining_seconds)  # the break ends
        self.assertEqual(
            seen,
            [Phase.SHORT_BREAK, Phase.SHORT_BREAK, Phase.SHORT_BREAK, Phase.LONG_BREAK],
        )


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

    def test_an_old_file_with_times_outside_the_limits_is_fixed(self):
        self.path.parent.mkdir(parents=True)
        data = AppConfig().to_dict()
        data["custom"].update(
            focus_minutes=120,
            short_break_minutes=1,
            long_break_minutes=20,
            pomodoros_before_long_break=3,
        )
        self.path.write_text(json.dumps(data), encoding="utf-8")
        loaded = load_config(self.path)
        self.assertEqual(loaded.custom.focus_minutes, 45)
        self.assertEqual(loaded.custom.short_break_minutes, 5)
        self.assertEqual(loaded.custom.long_break_minutes, 60)
        self.assertEqual(loaded.custom.pomodoros_before_long_break, 4)

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
