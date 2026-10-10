import random
import tempfile
import unittest
from pathlib import Path

from pomodoro.backgrounds import BackgroundPicker, default_folder, find_images


class BackgroundsTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.folder = Path(self._tmp.name)

    def add(self, category: str, *names: str) -> None:
        category_folder = self.folder / category
        category_folder.mkdir(parents=True, exist_ok=True)
        for name in names:
            (category_folder / name).write_bytes(b"fake")

    def test_default_folder_is_inside_the_package(self):
        self.assertEqual(default_folder().name, "backgrounds")
        self.assertEqual(default_folder().parent.name, "assets")

    def test_missing_category_has_no_images(self):
        self.assertEqual(find_images("water", self.folder), [])

    def test_finds_only_picture_files_sorted(self):
        self.add("water", "water_02.jpg", "water_01.PNG", "notes.txt", "x.webp")
        names = [p.name for p in find_images("water", self.folder)]
        self.assertEqual(names, ["water_01.PNG", "water_02.jpg", "x.webp"])

    def test_pick_returns_none_when_no_pictures(self):
        picker = BackgroundPicker(self.folder)
        self.assertIsNone(picker.pick("water"))

    def test_each_round_shows_every_picture_once(self):
        self.add("food", "food_01.jpg", "food_02.jpg", "food_03.jpg")
        picker = BackgroundPicker(self.folder, random.Random(1))
        shown = [picker.pick("food") for _ in range(3)]
        self.assertEqual(len(set(shown)), 3)

    def test_never_repeats_the_same_picture_twice_in_a_row(self):
        self.add("move", "move_01.jpg", "move_02.jpg", "move_03.jpg")
        picker = BackgroundPicker(self.folder, random.Random(4))
        shown = [picker.pick("move") for _ in range(60)]
        for before, after in zip(shown, shown[1:]):
            self.assertNotEqual(before, after)

    def test_single_picture_just_repeats(self):
        self.add("mind", "mind_01.jpg")
        picker = BackgroundPicker(self.folder)
        self.assertEqual(picker.pick("mind"), picker.pick("mind"))

    def test_categories_do_not_mix(self):
        self.add("water", "water_01.jpg")
        self.add("sleep", "sleep_01.jpg")
        picker = BackgroundPicker(self.folder)
        self.assertEqual(picker.pick("water").parent.name, "water")
        self.assertEqual(picker.pick("sleep").parent.name, "sleep")


if __name__ == "__main__":
    unittest.main()
