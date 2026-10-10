"""Easiest way to start the app: ``python run.py``."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from pomodoro.main import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
