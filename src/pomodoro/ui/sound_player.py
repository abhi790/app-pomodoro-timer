"""Plays the alert sound with the Windows built-in player.

``AlertSound.play()`` never raises and never blocks: the sound plays in the
background, and if anything goes wrong (not Windows, no sound card, a broken
file) the app simply stays quiet. A sound must never be able to crash the
timer.

A long sound is stopped after ``PLAY_LIMIT_SECONDS`` so a whole song does not
play over your break.
"""

from typing import Optional

from PySide6.QtCore import QObject, QTimer

from pomodoro.sound import (
    PLAY_LIMIT_SECONDS,
    default_chime_path,
    ensure_default_chime,
    resolve_sound,
)

try:  # only exists on Windows
    import winsound
except ImportError:  # pragma: no cover (not Windows)
    winsound = None


class AlertSound(QObject):
    def __init__(self, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._stopper = QTimer(self)
        self._stopper.setSingleShot(True)
        self._stopper.timeout.connect(self.stop)

    @property
    def available(self) -> bool:
        """True if this computer can play the sound (Windows only)."""
        return winsound is not None

    def play(self, sound_file: str = "") -> bool:
        """Play your own sound (``sound_file``), or the default chime if it is
        empty or no longer works. Gives True if a sound was started."""
        if not self.available:
            return False
        path = resolve_sound(sound_file, ensure_default_chime(default_chime_path()))
        if path is None:
            return False
        try:
            winsound.PlaySound(
                str(path), winsound.SND_FILENAME | winsound.SND_ASYNC
            )
        except (RuntimeError, OSError):
            return False
        self._stopper.start(PLAY_LIMIT_SECONDS * 1000)
        return True

    def stop(self) -> None:
        if not self.available:
            return
        try:
            winsound.PlaySound(None, winsound.SND_PURGE)
        except (RuntimeError, OSError):
            pass
