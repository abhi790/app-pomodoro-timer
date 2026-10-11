import os
import tempfile
import unittest
import wave
from pathlib import Path
from unittest import mock

# Run without a real screen if nobody chose a Qt platform already.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from pomodoro.settings import AppConfig, Mode, load_config, save_config
from pomodoro.timer_logic import Phase
from pomodoro.ui import sound_player
from pomodoro.ui.main_window import MainWindow
from pomodoro.ui.settings_dialog import SettingsDialog
from pomodoro.ui.sound_player import AlertSound
from pomodoro.usage import UsageTracker

_app = QApplication.instance() or QApplication([])


def write_wav(path: Path, frames: int = 4410) -> str:
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(44100)
        out.writeframes(b"\x00\x00" * frames)
    return str(path)


class FakeSound:
    """Stands in for AlertSound: remembers what it was asked to play."""

    def __init__(self, available: bool = True) -> None:
        self.available = available
        self.played: list = []

    def play(self, sound_file: str = "") -> bool:
        self.played.append(sound_file)
        return True


class FakeWinsound:
    SND_FILENAME = 1
    SND_ASYNC = 2
    SND_PURGE = 64

    def __init__(self, fail: bool = False) -> None:
        self.calls: list = []
        self.fail = fail

    def PlaySound(self, what, flags):
        if self.fail:
            raise RuntimeError("no sound card")
        self.calls.append((what, flags))


class TempDirTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)


class SettingsFileTest(TempDirTest):
    def test_sound_settings_are_saved_and_loaded(self):
        path = self.dir / "settings.json"
        config = AppConfig(sound_enabled=False, sound_file=r"C:\Sounds\bell.wav")
        save_config(config, path)
        loaded = load_config(path)
        self.assertFalse(loaded.sound_enabled)
        self.assertEqual(loaded.sound_file, r"C:\Sounds\bell.wav")

    def test_a_new_config_has_the_sound_on_with_the_default_chime(self):
        config = AppConfig()
        self.assertTrue(config.sound_enabled)
        self.assertEqual(config.sound_file, "")

    def test_old_settings_file_without_sound_still_loads_with_sound_on(self):
        path = self.dir / "settings.json"
        data = AppConfig(mode=Mode.POMODORO).to_dict()
        del data["sound_enabled"], data["sound_file"]
        path.write_text(__import__("json").dumps(data), encoding="utf-8")
        loaded = load_config(path)
        self.assertEqual(loaded.mode, Mode.POMODORO)
        self.assertTrue(loaded.sound_enabled)
        self.assertEqual(loaded.sound_file, "")

    def test_sound_settings_of_the_wrong_type_give_defaults(self):
        path = self.dir / "settings.json"
        for key, bad in (("sound_enabled", "yes"), ("sound_enabled", 1),
                         ("sound_file", 5), ("sound_file", ["a.wav"])):
            data = AppConfig().to_dict()
            data[key] = bad
            path.write_text(__import__("json").dumps(data), encoding="utf-8")
            self.assertEqual(load_config(path), AppConfig(), (key, bad))

    def test_the_sound_path_is_tidied_when_loaded(self):
        path = self.dir / "settings.json"
        data = AppConfig().to_dict()
        data["sound_file"] = "  C:\\a.wav  "
        path.write_text(__import__("json").dumps(data), encoding="utf-8")
        self.assertEqual(load_config(path).sound_file, "C:\\a.wav")


class AlertSoundTest(TempDirTest):
    def setUp(self):
        super().setUp()
        self.chime = self.dir / "chime-v1.wav"
        patcher = mock.patch.object(sound_player, "default_chime_path",
                                    return_value=self.chime)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_without_windows_it_is_quiet_and_does_not_fail(self):
        with mock.patch.object(sound_player, "winsound", None):
            alert = AlertSound()
            self.assertFalse(alert.available)
            self.assertFalse(alert.play(""))
            alert.stop()  # must not fail either

    def test_plays_the_default_chime_in_the_background(self):
        fake = FakeWinsound()
        with mock.patch.object(sound_player, "winsound", fake):
            self.assertTrue(AlertSound().play(""))
        self.assertEqual(fake.calls, [(str(self.chime), 1 | 2)])
        self.assertTrue(self.chime.is_file())

    def test_plays_your_own_sound(self):
        mine = write_wav(self.dir / "mine.wav")
        fake = FakeWinsound()
        with mock.patch.object(sound_player, "winsound", fake):
            self.assertTrue(AlertSound().play(mine))
        self.assertEqual(fake.calls[0][0], mine)

    def test_a_missing_own_sound_plays_the_default_chime(self):
        fake = FakeWinsound()
        with mock.patch.object(sound_player, "winsound", fake):
            AlertSound().play(str(self.dir / "gone.wav"))
        self.assertEqual(fake.calls[0][0], str(self.chime))

    def test_a_player_that_fails_does_not_crash_the_app(self):
        with mock.patch.object(sound_player, "winsound", FakeWinsound(fail=True)):
            self.assertFalse(AlertSound().play(""))

    def test_stop_purges_the_sound(self):
        fake = FakeWinsound()
        with mock.patch.object(sound_player, "winsound", fake):
            AlertSound().stop()
        self.assertEqual(fake.calls, [(None, 64)])


class MainWindowSoundTest(TempDirTest):
    def make_window(self, **config) -> tuple:
        sound = FakeSound()
        window = MainWindow(
            AppConfig(mode=Mode.CUSTOM, **config),
            UsageTracker(path=self.dir / "usage.json"),
            sound,
        )
        self.windows = getattr(self, "windows", []) + [window]  # keep them alive
        self.addCleanup(window._overlay.hide)
        return window, sound

    def end_focus(self, window) -> None:
        window._timer.start()
        window._timer.tick(window._timer.remaining_seconds)
        window._announce(Phase.FOCUS)

    def test_a_sound_plays_when_focus_ends(self):
        window, sound = self.make_window()
        self.end_focus(window)
        self.assertEqual(sound.played, [""])

    def test_your_own_sound_is_the_one_played(self):
        window, sound = self.make_window(sound_file="C:\\mine.wav")
        self.end_focus(window)
        self.assertEqual(sound.played, ["C:\\mine.wav"])

    def test_a_sound_plays_again_when_the_break_ends(self):
        window, sound = self.make_window()
        self.end_focus(window)
        window._timer.tick(window._timer.remaining_seconds)  # the break ends
        window._announce(Phase.SHORT_BREAK)
        self.assertEqual(len(sound.played), 2)

    def test_no_sound_when_it_is_switched_off(self):
        window, sound = self.make_window(sound_enabled=False)
        self.end_focus(window)
        window._announce(Phase.SHORT_BREAK)
        self.assertEqual(sound.played, [])

    def test_leaving_the_break_early_plays_no_sound(self):
        window, sound = self.make_window()
        self.end_focus(window)
        before = len(sound.played)
        window._on_math_unlocked()
        self.assertEqual(len(sound.played), before)


class SettingsDialogSoundTest(TempDirTest):
    def make(self, **config) -> tuple:
        sound = FakeSound()
        dialog = SettingsDialog(AppConfig(**config), None, sound)
        return dialog, sound

    def test_starts_with_the_default_chime_and_sound_on(self):
        dialog, _ = self.make()
        self.assertTrue(dialog._sound_check.isChecked())
        self.assertIn("default chime", dialog._sound_label.text())
        result = dialog.result_config()
        self.assertTrue(result.sound_enabled)
        self.assertEqual(result.sound_file, "")

    def test_the_sound_can_be_switched_off(self):
        dialog, _ = self.make()
        dialog._sound_check.setChecked(False)
        self.assertFalse(dialog.result_config().sound_enabled)

    def test_choosing_a_good_wav_uses_it(self):
        dialog, _ = self.make()
        mine = write_wav(self.dir / "mine.wav")
        self.assertIsNone(dialog.use_sound_file(mine))
        self.assertEqual(dialog.result_config().sound_file, mine)
        self.assertIn("mine.wav", dialog._sound_label.text())

    def test_a_bad_file_is_refused_and_the_old_sound_stays(self):
        old = write_wav(self.dir / "old.wav")
        dialog, _ = self.make(sound_file=old)
        bad = self.dir / "song.mp3"
        bad.write_bytes(b"ID3")
        self.assertIn(".wav", dialog.use_sound_file(str(bad)))
        self.assertEqual(dialog.result_config().sound_file, old)
        self.assertIn("not changed", dialog._sound_label.text())

    def test_default_button_goes_back_to_the_chime(self):
        mine = write_wav(self.dir / "mine.wav")
        dialog, _ = self.make(sound_file=mine)
        dialog._default_button.click()
        self.assertEqual(dialog.result_config().sound_file, "")
        self.assertIn("default chime", dialog._sound_label.text())

    def test_a_saved_sound_that_went_missing_says_so(self):
        dialog, _ = self.make(sound_file=str(self.dir / "gone.wav"))
        text = dialog._sound_label.text()
        self.assertIn("not found", text)
        self.assertIn("default chime is used", text)

    def test_test_button_plays_the_chosen_sound_even_when_off(self):
        mine = write_wav(self.dir / "mine.wav")
        dialog, sound = self.make(sound_file=mine, sound_enabled=False)
        dialog._test_button.click()
        self.assertEqual(sound.played, [mine])

    def test_test_button_says_so_when_sound_cannot_play(self):
        sound = FakeSound(available=False)
        dialog = SettingsDialog(AppConfig(), None, sound)
        dialog._test_button.click()
        self.assertEqual(sound.played, [])
        self.assertIn("Windows", dialog._sound_label.text())

    def test_the_window_never_gets_taller_than_the_screen(self):
        dialog, _ = self.make()
        dialog.show()
        self.addCleanup(dialog.close)
        screen = dialog.screen().availableGeometry().height()
        self.assertLessEqual(dialog.height(), screen)

    def test_the_other_settings_still_come_back(self):
        dialog, _ = self.make(mode=Mode.POMODORO)
        result = dialog.result_config()
        self.assertEqual(result.mode, Mode.POMODORO)
        self.assertEqual(result.ideas, ())


if __name__ == "__main__":
    unittest.main()
