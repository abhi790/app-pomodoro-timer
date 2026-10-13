import os
import struct
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QImage

from pomodoro.icon_file import PNG_SIGNATURE, build_ico, read_ico_entries
from pomodoro.paths import package_dir
from pomodoro.ui.app_icon import ICON_SIZES

ICON_PATH = package_dir() / "assets" / "pomodoro.ico"


def fake_png(tag: bytes) -> bytes:
    return PNG_SIGNATURE + tag


class BuildIcoTest(unittest.TestCase):
    def test_the_header_says_icon_and_how_many_pictures(self):
        data = build_ico([(16, fake_png(b"a")), (32, fake_png(b"b"))])
        reserved, kind, count = struct.unpack_from("<HHH", data, 0)
        self.assertEqual((reserved, kind, count), (0, 1, 2))

    def test_every_picture_comes_back_unchanged(self):
        images = [(16, fake_png(b"one")), (48, fake_png(b"two!")), (256, fake_png(b"3"))]
        entries = read_ico_entries(build_ico(images))
        self.assertEqual([e.size for e in entries], [16, 48, 256])
        self.assertEqual([e.data for e in entries], [png for _, png in images])

    def test_256_is_written_as_zero_like_windows_wants(self):
        data = build_ico([(256, fake_png(b"x"))])
        self.assertEqual(data[6], 0)  # width byte of the first entry
        self.assertEqual(data[7], 0)  # height byte
        self.assertEqual(read_ico_entries(data)[0].size, 256)

    def test_the_entries_say_32_bits_and_point_at_their_data(self):
        images = [(16, fake_png(b"aaaa")), (32, fake_png(b"bb"))]
        data = build_ico(images)
        for index, (size, png) in enumerate(images):
            width, height, _colors, _res, planes, bits, length, offset = struct.unpack_from(
                "<BBBBHHII", data, 6 + 16 * index
            )
            self.assertEqual((width, height), (size, size))
            self.assertEqual((planes, bits), (1, 32))
            self.assertEqual(length, len(png))
            self.assertEqual(data[offset : offset + length], png)

    def test_it_refuses_things_that_would_make_a_broken_icon(self):
        for bad in (
            [],  # nothing to pack
            [(0, fake_png(b"x"))],  # no size
            [(257, fake_png(b"x"))],  # bigger than an icon can be
            [(16, b"not a png")],  # not a PNG picture
        ):
            with self.assertRaises(ValueError, msg=repr(bad)):
                build_ico(bad)

    def test_reading_something_that_is_not_an_icon_fails_clearly(self):
        for bad in (b"", b"abc", struct.pack("<HHH", 0, 2, 1)):
            with self.assertRaises(ValueError, msg=repr(bad)):
                read_ico_entries(bad)


class CommittedIconTest(unittest.TestCase):
    """The icon file that the .exe gets (made by tools/make_icon.py)."""

    def test_the_file_is_there(self):
        self.assertTrue(ICON_PATH.is_file(), f"missing {ICON_PATH}")

    def test_it_holds_every_size_windows_asks_for(self):
        entries = read_ico_entries(ICON_PATH.read_bytes())
        self.assertEqual([e.size for e in entries], list(ICON_SIZES))

    def test_every_picture_is_a_real_tomato_of_the_right_size(self):
        for entry in read_ico_entries(ICON_PATH.read_bytes()):
            self.assertTrue(entry.data.startswith(PNG_SIGNATURE), entry.size)
            image = QImage()
            self.assertTrue(image.loadFromData(entry.data), entry.size)
            self.assertEqual((image.width(), image.height()), (entry.size, entry.size))
            middle = image.pixelColor(entry.size // 2, int(entry.size * 0.6))
            self.assertGreater(middle.alpha(), 200, entry.size)  # the body, not air
            self.assertGreater(middle.red(), middle.green() + 40, entry.size)  # red
            corner = image.pixelColor(0, 0)
            self.assertEqual(corner.alpha(), 0, entry.size)  # transparent corner


if __name__ == "__main__":
    unittest.main()
