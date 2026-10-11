"""The alert sound: a built-in chime, or your own sound file.

No windows here, so it is easy to test. When a focus block ends, and again when
a break ends, the app plays a sound.

* The default is a soft three-note chime. It is made by this file (no audio
  file to carry around) and saved once as ``chime-v1.wav`` next to
  ``settings.json``.
* You can choose your own sound in Settings. It must be a ``.wav`` file,
  at most 10 MB. If your file goes missing later, the default chime is
  played, so the app is never silent by accident.

Only the Windows built-in player is used (see ``ui/sound_player.py``), so no
extra package is needed. That player plays ``.wav`` files, which is why other
formats such as ``.mp3`` are not accepted yet.
"""

import math
import struct
import wave
from io import BytesIO
from pathlib import Path
from typing import Optional

from pomodoro.settings import config_path

SAMPLE_RATE = 44100
CHIME_SECONDS = 1.9

# The three notes (C, E, G) and when each one starts, in seconds.
CHIME_NOTES = ((523.25, 0.0), (659.25, 0.18), (783.99, 0.36))

# Your own sound: only .wav, and not bigger than this.
SOUND_SUFFIXES = (".wav",)
MAX_SOUND_BYTES = 10 * 1024 * 1024

# A long sound is stopped after this many seconds, so a whole song does not
# play over your break.
PLAY_LIMIT_SECONDS = 15

DEFAULT_CHIME_NAME = "chime-v1.wav"


def make_chime_wav() -> bytes:
    """The default chime as the bytes of a ``.wav`` file (16-bit, mono).

    Three soft bell notes, one after the other, each fading out smoothly. The
    same bytes come out every time.
    """
    total = int(SAMPLE_RATE * CHIME_SECONDS)
    samples = [0.0] * total
    for frequency, start in CHIME_NOTES:
        first = int(start * SAMPLE_RATE)
        for i in range(first, total):
            t = (i - first) / SAMPLE_RATE
            attack = min(1.0, t / 0.012)  # no click at the start
            fade = math.exp(-3.4 * t)
            tone = math.sin(2 * math.pi * frequency * t)
            tone += 0.28 * math.sin(2 * math.pi * 2 * frequency * t)
            samples[i] += attack * fade * tone

    peak = max(abs(value) for value in samples) or 1.0
    scale = 0.7 * 32767 / peak  # leave some room, never clip
    frames = struct.pack(
        f"<{total}h", *(int(round(value * scale)) for value in samples)
    )

    buffer = BytesIO()
    with wave.open(buffer, "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(SAMPLE_RATE)
        out.writeframes(frames)
    return buffer.getvalue()


def default_chime_path() -> Path:
    """Where the default chime is saved (next to ``settings.json``)."""
    return config_path().with_name(DEFAULT_CHIME_NAME)


def ensure_default_chime(path: Optional[Path] = None) -> Optional[Path]:
    """Make sure the default chime file exists. Gives its path, or None if it
    could not be written (then the app is just silent, it does not crash)."""
    path = path or default_chime_path()
    try:
        if not (path.is_file() and path.stat().st_size > 0):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(make_chime_wav())
        return path
    except OSError:
        return None


def check_sound_file(path: str) -> Optional[str]:
    """Is this a sound the app can play? Gives None if yes, or a short message
    saying what is wrong."""
    file = Path(path)
    try:
        if not file.is_file():
            return "That file was not found."
        if file.suffix.lower() not in SOUND_SUFFIXES:
            return "Only .wav files can be used for now."
        if file.stat().st_size > MAX_SOUND_BYTES:
            return "That file is too big (the limit is 10 MB)."
        with wave.open(str(file), "rb") as sound:
            if sound.getnframes() < 1:
                return "That sound file is empty."
    except (wave.Error, EOFError, OSError):
        return "That is not a .wav sound the app can play."
    return None


def resolve_sound(custom: str, default: Optional[Path]) -> Optional[Path]:
    """The file to play: your own sound if you chose one and it still works,
    otherwise the default chime (which can be None if it could not be made)."""
    if custom and check_sound_file(custom) is None:
        return Path(custom)
    return default
