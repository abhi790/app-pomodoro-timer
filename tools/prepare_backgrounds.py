"""Turns raw generated pictures into the pictures the app uses.

The raw pictures are named like ``0001_scene1.png`` ... ``0028_scene28.png``.
The number in front is the scene number, in the same order as
``docs/background-image-prompts.md``:

    scenes  1-4   water        scenes 17-20  posture
    scenes  5-8   food         scenes 21-24  sleep
    scenes  9-12  move         scenes 25-28  mind
    scenes 13-16  eyes

Each picture is scaled down if it is very wide, saved as a JPG, and put in
``src/pomodoro/assets/backgrounds/<category>/<category>_0N.jpg``.

Usage (in a Command Prompt, from the project folder):

    python tools\\prepare_backgrounds.py <folder with the raw pictures>

Add ``--dry-run`` to only print what would happen.
"""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from pomodoro.tips import CATEGORIES  # noqa: E402

PER_CATEGORY = 4
TOTAL_SCENES = len(CATEGORIES) * PER_CATEGORY
SOURCE_SUFFIXES = (".png", ".jpg", ".jpeg", ".webp")
MAX_WIDTH = 2560
JPG_QUALITY = 88
OUTPUT_FOLDER = ROOT / "src" / "pomodoro" / "assets" / "backgrounds"


def scene_target(number: int) -> tuple:
    """Scene number (1-28) -> (category, picture number inside the category)."""
    if not 1 <= number <= TOTAL_SCENES:
        raise ValueError(f"scene number must be 1 to {TOTAL_SCENES}, not {number}")
    category = CATEGORIES[(number - 1) // PER_CATEGORY]
    return category, (number - 1) % PER_CATEGORY + 1


def find_sources(folder: Path) -> tuple:
    """Look for files that start with the scene number.

    Returns (pictures, problems). ``pictures`` maps scene number to the file.
    """
    pictures: dict = {}
    problems: list = []
    for path in sorted(folder.iterdir()):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        match = re.match(r"(\d+)", path.name)
        if not match:
            problems.append(f"skipped (name does not start with a number): {path.name}")
            continue
        number = int(match.group(1))
        if not 1 <= number <= TOTAL_SCENES:
            problems.append(f"skipped (scene number {number} is not 1-{TOTAL_SCENES}): {path.name}")
        elif number in pictures:
            problems.append(f"skipped (scene {number} already has a file): {path.name}")
        else:
            pictures[number] = path
    return pictures, problems


def convert(source: Path, destination: Path) -> int:
    """Save ``source`` as a JPG at ``destination``. Returns the size in bytes."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QImage

    image = QImage(str(source))
    if image.isNull():
        raise OSError(f"could not read the picture {source.name}")
    if image.width() > MAX_WIDTH:
        image = image.scaledToWidth(MAX_WIDTH, Qt.SmoothTransformation)
    image = image.convertToFormat(QImage.Format_RGB32)  # JPG has no transparency
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not image.save(str(destination), "JPG", JPG_QUALITY):
        raise OSError(f"could not save {destination}")
    return destination.stat().st_size


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("folder", type=Path, help="folder with the raw pictures")
    parser.add_argument("--dry-run", action="store_true", help="only print the plan")
    args = parser.parse_args(argv)

    if not args.folder.is_dir():
        print(f"Folder not found: {args.folder}")
        return 1

    pictures, problems = find_sources(args.folder)
    for problem in problems:
        print(problem)
    if not pictures:
        print("No pictures found. Names should look like 0001_scene1.png")
        return 1

    total_bytes = 0
    for number in sorted(pictures):
        category, index = scene_target(number)
        destination = OUTPUT_FOLDER / category / f"{category}_{index:02d}.jpg"
        label = f"scene {number:2d}  {pictures[number].name}  ->  {category}/{destination.name}"
        if args.dry_run:
            print(label)
            continue
        size = convert(pictures[number], destination)
        total_bytes += size
        print(f"{label}  ({size // 1024} KB)")

    missing = [n for n in range(1, TOTAL_SCENES + 1) if n not in pictures]
    if missing:
        print(f"Missing scenes: {', '.join(str(n) for n in missing)}")
    if not args.dry_run:
        print(f"Done. {len(pictures)} pictures, {total_bytes // 1024} KB in total.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
