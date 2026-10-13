"""Builds the Windows .exe with PyInstaller.

Usage (in a Command Prompt, from the project folder):

    python -m pip install pyinstaller
    python tools\\build_exe.py

By default it makes a folder, ``dist\\PomodoroTimer\\``, with ``PomodoroTimer.exe``
inside. Start that exe (keep the folder together). A folder starts faster than
one single file, because nothing has to be unpacked at every start.

    python tools\\build_exe.py --onefile       one single dist\\PomodoroTimer.exe
    python tools\\build_exe.py --dry-run       only show the command

What goes into the exe: the code, the Qt parts the app uses, the background
pictures (``src/pomodoro/assets``) and the tomato icon. There is no black console
window (``--windowed``). The settings, the daily count and the default chime are
written to ``%APPDATA%\\PomodoroTimer`` when the app runs, the same as without
the exe.

See docs/07c-exe.md.
"""

import argparse
import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

APP_NAME = "PomodoroTimer"


def _icon_path(root: Path) -> Path:
    return root / "src" / "pomodoro" / "assets" / "pomodoro.ico"


def _assets_path(root: Path) -> Path:
    return root / "src" / "pomodoro" / "assets"


def build_command(
    root: Path, onefile: bool = False, python: str = sys.executable
) -> List[str]:
    """The PyInstaller command (a list of words) for this project folder."""
    return [
        python,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",  # no black console window
        "--name",
        APP_NAME,
        "--icon",
        str(_icon_path(root)),
        "--paths",
        str(root / "src"),
        # The background pictures. They land in <bundle>/pomodoro/assets, which
        # is where pomodoro.paths.package_dir() looks for them.
        "--add-data",
        f"{_assets_path(root)}{os.pathsep}pomodoro/assets",
        # winsound is imported inside a try block, so make sure it is included.
        "--hidden-import",
        "winsound",
        "--distpath",
        str(root / "dist"),
        "--workpath",
        str(root / "build"),
        "--specpath",
        str(root / "build"),
        "--onefile" if onefile else "--onedir",
        str(root / "run.py"),
    ]


def exe_path(root: Path, onefile: bool = False) -> Path:
    """Where the finished exe is."""
    if onefile:
        return root / "dist" / f"{APP_NAME}.exe"
    return root / "dist" / APP_NAME / f"{APP_NAME}.exe"


def missing_inputs(root: Path) -> List[str]:
    """What the build needs but cannot find (empty if all is there)."""
    needed = {
        "run.py": root / "run.py",
        "the background pictures": _assets_path(root) / "backgrounds",
        "the icon pomodoro.ico": _icon_path(root),
    }
    return [f"{name} ({path})" for name, path in needed.items() if not path.exists()]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build PomodoroTimer.exe")
    parser.add_argument(
        "--onefile", action="store_true", help="one single exe instead of a folder"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="only show the command"
    )
    args = parser.parse_args(argv)

    if not _icon_path(ROOT).exists():
        from tools.make_icon import write_icon  # needs PySide6, so only here

        print(f"Making the icon {_icon_path(ROOT)} ...")
        write_icon(_icon_path(ROOT))

    missing = missing_inputs(ROOT)
    if missing:
        print("Cannot build. Missing: " + "; ".join(missing))
        return 1

    command = build_command(ROOT, onefile=args.onefile)
    print("Command:\n  " + " ".join(f'"{word}"' if " " in word else word for word in command))
    if args.dry_run:
        return 0

    if importlib.util.find_spec("PyInstaller") is None:
        print("PyInstaller is not installed. Run this first:")
        print("  python -m pip install pyinstaller")
        return 1

    code = subprocess.call(command, cwd=ROOT)
    if code != 0:
        print(f"PyInstaller stopped with an error (code {code}). Send me the text above.")
        return code
    print(f"\nDone. Start: {exe_path(ROOT, onefile=args.onefile)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
