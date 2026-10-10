import unittest

from PySide6.QtCore import QRectF
from PySide6.QtGui import QImage, QPainter

from pomodoro.tips import CATEGORIES
from pomodoro.ui.break_overlay import CATEGORY_GRADIENT, Scene


def paint_scene(category: str) -> QImage:
    image = QImage(320, 180, QImage.Format_ARGB32)
    image.fill(0)
    painter = QPainter(image)
    Scene(category).paint(painter, QRectF(0, 0, 320, 180))
    painter.end()
    return image


class ScenePaintTest(unittest.TestCase):
    def test_every_category_has_gradient_colors(self):
        for category in CATEGORIES:
            self.assertIn(category, CATEGORY_GRADIENT)

    def test_scene_without_picture_paints_every_pixel(self):
        for category in list(CATEGORIES) + ["", "unknown"]:
            image = paint_scene(category)
            self.assertEqual(image.pixelColor(160, 90).alpha(), 255, category)
            self.assertEqual(image.pixelColor(0, 0).alpha(), 255, category)

    def test_categories_look_different(self):
        water = paint_scene("water").pixelColor(300, 170).name()
        move = paint_scene("move").pixelColor(300, 170).name()
        self.assertNotEqual(water, move)


if __name__ == "__main__":
    unittest.main()
