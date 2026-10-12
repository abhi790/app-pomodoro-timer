import unittest

from pomodoro.fit_text import TIP_FONT_SIZES, pick_font_px


class PickFontPxTest(unittest.TestCase):
    def test_the_normal_size_is_kept_when_it_fits(self):
        self.assertEqual(pick_font_px(lambda px: px * 3, 190), TIP_FONT_SIZES[0])

    def test_a_smaller_size_is_used_when_the_normal_one_is_too_tall(self):
        # 6 lines per size unit: 36 -> 216 (too tall), 32 -> 192 (too tall),
        # 29 -> 174 (fits).
        self.assertEqual(pick_font_px(lambda px: px * 6, 190), 29)

    def test_the_biggest_size_that_fits_is_chosen(self):
        sizes = (40, 30, 20)
        self.assertEqual(pick_font_px(lambda px: px * 5, 160, sizes), 30)

    def test_the_smallest_size_is_used_when_nothing_fits(self):
        self.assertEqual(pick_font_px(lambda px: 10_000, 190), TIP_FONT_SIZES[-1])

    def test_the_height_function_is_asked_only_until_one_fits(self):
        asked = []

        def height_at(px):
            asked.append(px)
            return 100

        pick_font_px(height_at, 190)
        self.assertEqual(asked, [TIP_FONT_SIZES[0]])

    def test_the_sizes_go_from_big_to_small(self):
        self.assertEqual(list(TIP_FONT_SIZES), sorted(TIP_FONT_SIZES, reverse=True))


if __name__ == "__main__":
    unittest.main()
