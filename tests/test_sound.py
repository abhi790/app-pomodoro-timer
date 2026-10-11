import struct
import tempfile
import unittest
import wave
from io import BytesIO
from pathlib import Path

from pomodoro.sound import (
    CHIME_SECONDS,
    MAX_SOUND_BYTES,
    SAMPLE_RATE,
    check_sound_file,
    ensure_default_chime,
    make_chime_wav,
    resolve_sound,
)


def write_wav(path: Path, frames: int = 4410, width: int = 2) -> None:
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(width)
        out.setframerate(SAMPLE_RATE)
        out.writeframes(b"\x00" * frames * width)


class ChimeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = make_chime_wav()

    def test_is_a_valid_wav_file(self):
        with wave.open(BytesIO(self.data), "rb") as sound:
            self.assertEqual(sound.getnchannels(), 1)
            self.assertEqual(sound.getsampwidth(), 2)
            self.assertEqual(sound.getframerate(), SAMPLE_RATE)

    def test_is_about_two_seconds_long(self):
        with wave.open(BytesIO(self.data), "rb") as sound:
            seconds = sound.getnframes() / sound.getframerate()
        self.assertAlmostEqual(seconds, CHIME_SECONDS, places=1)

    def test_is_not_silent_and_does_not_clip(self):
        with wave.open(BytesIO(self.data), "rb") as sound:
            raw = sound.readframes(sound.getnframes())
        values = struct.unpack(f"<{len(raw) // 2}h", raw)
        peak = max(abs(v) for v in values)
        self.assertGreater(peak, 10000)
        self.assertLess(peak, 32767)

    def test_fades_out_to_nearly_nothing(self):
        with wave.open(BytesIO(self.data), "rb") as sound:
            raw = sound.readframes(sound.getnframes())
        values = struct.unpack(f"<{len(raw) // 2}h", raw)
        self.assertLess(max(abs(v) for v in values[-500:]), 600)

    def test_starts_softly_without_a_click(self):
        with wave.open(BytesIO(self.data), "rb") as sound:
            raw = sound.readframes(20)
        self.assertLess(max(abs(v) for v in struct.unpack("<20h", raw)), 1500)

    def test_is_the_same_every_time(self):
        self.assertEqual(self.data, make_chime_wav())


class EnsureDefaultChimeTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "PomodoroTimer" / "chime-v1.wav"

    def test_creates_the_file_and_the_folder(self):
        self.assertEqual(ensure_default_chime(self.path), self.path)
        self.assertIsNone(check_sound_file(str(self.path)))

    def test_keeps_a_file_that_is_already_there(self):
        ensure_default_chime(self.path)
        before = self.path.stat().st_mtime_ns
        ensure_default_chime(self.path)
        self.assertEqual(self.path.stat().st_mtime_ns, before)

    def test_rewrites_an_empty_file(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_bytes(b"")
        ensure_default_chime(self.path)
        self.assertGreater(self.path.stat().st_size, 1000)

    def test_gives_none_when_it_cannot_write(self):
        blocker = Path(self._tmp.name) / "blocker"
        blocker.write_text("a file, not a folder")
        self.assertIsNone(ensure_default_chime(blocker / "chime-v1.wav"))


class CheckSoundFileTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)

    def test_a_good_wav_is_accepted(self):
        good = self.dir / "ding.wav"
        write_wav(good)
        self.assertIsNone(check_sound_file(str(good)))

    def test_capital_suffix_is_accepted(self):
        good = self.dir / "DING.WAV"
        write_wav(good)
        self.assertIsNone(check_sound_file(str(good)))

    def test_missing_file(self):
        self.assertIn("not found", check_sound_file(str(self.dir / "nope.wav")))

    def test_a_folder_is_not_a_sound(self):
        self.assertIn("not found", check_sound_file(str(self.dir)))

    def test_mp3_is_not_accepted(self):
        mp3 = self.dir / "song.mp3"
        mp3.write_bytes(b"ID3" + b"\x00" * 100)
        self.assertIn(".wav", check_sound_file(str(mp3)))

    def test_text_renamed_to_wav_is_not_accepted(self):
        fake = self.dir / "fake.wav"
        fake.write_text("this is not a sound")
        self.assertIn("not a .wav", check_sound_file(str(fake)))

    def test_empty_wav_is_not_accepted(self):
        empty = self.dir / "empty.wav"
        write_wav(empty, frames=0)
        self.assertIn("empty", check_sound_file(str(empty)))

    def test_too_big_is_not_accepted(self):
        big = self.dir / "big.wav"
        write_wav(big, frames=MAX_SOUND_BYTES // 2 + 1000)
        self.assertGreater(big.stat().st_size, MAX_SOUND_BYTES)
        self.assertIn("too big", check_sound_file(str(big)))


class ResolveSoundTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.dir = Path(self._tmp.name)
        self.default = self.dir / "default.wav"
        write_wav(self.default)

    def test_no_custom_sound_gives_the_default(self):
        self.assertEqual(resolve_sound("", self.default), self.default)

    def test_a_good_custom_sound_wins(self):
        mine = self.dir / "mine.wav"
        write_wav(mine)
        self.assertEqual(resolve_sound(str(mine), self.default), mine)

    def test_a_missing_custom_sound_falls_back_to_the_default(self):
        self.assertEqual(
            resolve_sound(str(self.dir / "gone.wav"), self.default), self.default
        )

    def test_a_broken_custom_sound_falls_back_to_the_default(self):
        broken = self.dir / "broken.wav"
        broken.write_text("nope")
        self.assertEqual(resolve_sound(str(broken), self.default), self.default)

    def test_no_default_and_no_custom_gives_none(self):
        self.assertIsNone(resolve_sound("", None))


if __name__ == "__main__":
    unittest.main()
