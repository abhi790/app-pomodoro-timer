"""Packs pictures into a Windows ``.ico`` file, without any windows.

The ``.exe`` needs an icon *file* (the tomato it shows in Explorer, on the
desktop and in the taskbar). The app draws its tomato with code, so
``tools/make_icon.py`` draws it in every size, turns each size into a PNG and
gives the PNGs to ``build_ico``. Windows (Vista and newer) reads PNG pictures
inside an ``.ico`` file.

Layout of an ``.ico`` file: a 6 byte header, then 16 bytes per picture (size,
colors, how many bytes, where they start), then the pictures themselves.
"""

import struct
from dataclasses import dataclass
from typing import List, Sequence, Tuple

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"

_HEADER = "<HHH"  # always 0, 1 = icon, how many pictures
_ENTRY = "<BBBBHHII"  # width, height, colors, 0, planes, bits, bytes, offset
_HEADER_SIZE = struct.calcsize(_HEADER)
_ENTRY_SIZE = struct.calcsize(_ENTRY)
_ICON_TYPE = 1
_BIGGEST = 256  # an icon picture is at most 256 x 256


@dataclass(frozen=True)
class IconEntry:
    """One picture of an icon file: its size in pixels and its PNG bytes."""

    size: int
    data: bytes


def build_ico(images: Sequence[Tuple[int, bytes]]) -> bytes:
    """Make the bytes of an ``.ico`` file from ``(size, png_bytes)`` pairs.

    Raises ValueError for nothing to pack, a size outside 1 to 256, or data that
    is not a PNG picture (the file would be broken).
    """
    if not images:
        raise ValueError("an icon needs at least one picture")
    for size, data in images:
        if not isinstance(size, int) or not 1 <= size <= _BIGGEST:
            raise ValueError(f"a picture size must be 1 to {_BIGGEST}, not {size!r}")
        if not data.startswith(PNG_SIGNATURE):
            raise ValueError(f"the {size} px picture is not a PNG")

    header = struct.pack(_HEADER, 0, _ICON_TYPE, len(images))
    offset = _HEADER_SIZE + _ENTRY_SIZE * len(images)
    entries = b""
    pictures = b""
    for size, data in images:
        byte = 0 if size == _BIGGEST else size  # 256 is written as 0
        entries += struct.pack(
            _ENTRY, byte, byte, 0, 0, 1, 32, len(data), offset + len(pictures)
        )
        pictures += data
    return header + entries + pictures


def read_ico_entries(data: bytes) -> List[IconEntry]:
    """The pictures inside an ``.ico`` file. Raises ValueError if the bytes are
    not an icon file."""
    if len(data) < _HEADER_SIZE:
        raise ValueError("too short to be an icon file")
    reserved, kind, count = struct.unpack_from(_HEADER, data, 0)
    if reserved != 0 or kind != _ICON_TYPE or count < 1:
        raise ValueError("this is not an icon file")
    if len(data) < _HEADER_SIZE + _ENTRY_SIZE * count:
        raise ValueError("the icon file is cut short")

    entries = []
    for index in range(count):
        width, _h, _colors, _zero, _planes, _bits, length, offset = struct.unpack_from(
            _ENTRY, data, _HEADER_SIZE + _ENTRY_SIZE * index
        )
        if offset + length > len(data):
            raise ValueError("a picture points outside the icon file")
        entries.append(IconEntry(width or _BIGGEST, data[offset : offset + length]))
    return entries
