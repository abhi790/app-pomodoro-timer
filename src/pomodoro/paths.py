"""Where the app's own files are, without any windows.

When you start the app with Python (``python run.py``), its files are next to
the code. In the Windows ``.exe`` (built with PyInstaller) they are inside the
bundle instead, so the code cannot just trust ``__file__``. Everything that
reads a file the app carries with it (the background pictures) asks this file.

Settings and the daily count are not here: they live in ``%APPDATA%`` and are
the same in both cases (see ``settings.py`` and ``usage.py``).
"""

import sys
from pathlib import Path


def package_dir() -> Path:
    """The folder that holds ``assets/`` (and the rest of the ``pomodoro``
    package): next to the code, or ``<bundle>/pomodoro`` inside the .exe."""
    if getattr(sys, "frozen", False):
        bundle = getattr(sys, "_MEIPASS", None)
        base = Path(bundle) if bundle else Path(sys.executable).parent
        return base / "pomodoro"
    return Path(__file__).resolve().parent
