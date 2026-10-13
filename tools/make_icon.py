"""Makes the tomato icon file (``pomodoro.ico``) that the .exe gets.

The app draws its tomato with code (``pomodoro/ui/app_icon.py``), so there is no
picture to download. This script draws it in every size Windows asks for and
packs the sizes into one ``.ico`` file:

    src/pomodoro/assets/pomodoro.ico

You only need it if you change the tomato. ``tools/build_exe.py`` also runs it
by itself when the icon file is missing.

Usage (in a Command Prompt, from the project folder):

    python tools\\make_icon.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from PySide6.QtCore import QBuffer, QIODevice  # noqa: E402
from PySide6.QtGui import QImage  # noqa: E402

from pomodoro.icon_file import build_ico  # noqa: E402
from pomodoro.ui.app_icon import ICON_SIZES, draw_tomato  # noqa: E402

ICON_PATH = ROOT / "src" / "pomodoro" / "assets" / "pomodoro.ico"


def png_bytes(image: QImage) -> bytes:
    """The picture as the bytes of a PNG file."""
    buffer = QBuffer()
    buffer.open(QIODevice.WriteOnly)
    if not image.save(buffer, "PNG"):
        raise RuntimeError("could not make a PNG picture")
    return bytes(buffer.data())


def write_icon(path: Path = ICON_PATH) -> Path:
    """Draw the tomato in every size and write the ``.ico`` file."""
    images = [(size, png_bytes(draw_tomato(size))) for size in ICON_SIZES]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(build_ico(images))
    return path


def main() -> int:
    path = write_icon()
    print(f"Wrote {path} ({path.stat().st_size} bytes, sizes {list(ICON_SIZES)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
