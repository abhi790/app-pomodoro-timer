import unittest

from pomodoro.ui.app_icon import APP_ID, ICON_SIZES, draw_tomato


class DrawTomatoTest(unittest.TestCase):
    def test_image_has_the_asked_size(self):
        for size in ICON_SIZES:
            image = draw_tomato(size)
            self.assertFalse(image.isNull(), size)
            self.assertEqual((image.width(), image.height()), (size, size))

    def test_includes_small_and_large_sizes(self):
        self.assertIn(16, ICON_SIZES)
        self.assertIn(32, ICON_SIZES)
        self.assertGreaterEqual(max(ICON_SIZES), 256)

    def test_corner_is_transparent(self):
        for size in ICON_SIZES:
            self.assertEqual(draw_tomato(size).pixelColor(0, 0).alpha(), 0, size)

    def test_body_is_red(self):
        for size in (32, 64, 256):
            color = draw_tomato(size).pixelColor(size // 2, int(size * 0.69))
            self.assertGreater(color.red(), 150, size)
            self.assertLess(color.green(), 110, size)
            self.assertLess(color.blue(), 110, size)

    def test_top_is_green(self):
        for size in (32, 64, 256):
            color = draw_tomato(size).pixelColor(size // 2, int(size * 0.28))
            self.assertGreater(color.green(), color.red(), size)
            self.assertGreater(color.green(), color.blue(), size)

    def test_app_id_has_no_spaces(self):
        self.assertNotIn(" ", APP_ID)


if __name__ == "__main__":
    unittest.main()
