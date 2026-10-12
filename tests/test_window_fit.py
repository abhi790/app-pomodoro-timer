import unittest

from pomodoro.window_fit import EDGE_MARGIN, fit_in_area

# A 1366 x 768 laptop: the taskbar takes the bottom 40 pixels.
LAPTOP = (0, 0, 1366, 728)
FRAME = (16, 39)  # borders and title bar


def outer(result, frame=FRAME):
    """The whole window (with title bar) as x, y, right, bottom."""
    x, y, width, height = result
    return x, y, x + width + frame[0], y + height + frame[1]


class FitInAreaTest(unittest.TestCase):
    def assert_inside(self, result, area=LAPTOP, frame=FRAME):
        left, top, right, bottom = outer(result, frame)
        area_x, area_y, area_width, area_height = area
        self.assertGreaterEqual(left, area_x)
        self.assertGreaterEqual(top, area_y)
        self.assertLessEqual(right, area_x + area_width)
        self.assertLessEqual(bottom, area_y + area_height)

    def test_a_small_window_stays_as_big_as_wanted_and_is_centered(self):
        x, y, width, height = fit_in_area((480, 400), FRAME, LAPTOP, (683, 364))
        self.assertEqual((width, height), (480, 400))
        self.assertEqual(x + (width + FRAME[0]) // 2, 683)
        self.assertEqual(y + (height + FRAME[1]) // 2, 364)

    def test_a_tall_window_is_cut_to_fit_the_screen(self):
        result = fit_in_area((480, 1200), FRAME, LAPTOP, (683, 364))
        self.assertLess(result[3], 1200)
        self.assert_inside(result)

    def test_a_window_started_near_the_bottom_is_moved_up(self):
        # Centered on a point at the very bottom, so it would hang below the
        # taskbar. It must be moved up until all of it is visible.
        result = fit_in_area((480, 600), FRAME, LAPTOP, (683, 720))
        self.assert_inside(result)
        self.assertEqual(outer(result)[3], LAPTOP[3] - EDGE_MARGIN)

    def test_a_window_started_near_the_top_is_moved_down(self):
        result = fit_in_area((480, 600), FRAME, LAPTOP, (683, 5))
        self.assert_inside(result)
        self.assertEqual(result[1], EDGE_MARGIN)

    def test_a_window_started_off_to_the_right_is_moved_left(self):
        result = fit_in_area((480, 400), FRAME, LAPTOP, (1360, 364))
        self.assert_inside(result)

    def test_a_window_started_off_to_the_left_is_moved_right(self):
        result = fit_in_area((480, 400), FRAME, LAPTOP, (-300, 364))
        self.assert_inside(result)

    def test_works_when_the_screen_does_not_start_at_zero(self):
        # A second monitor to the right, with its own taskbar at the top.
        area = (1920, 40, 1920, 1040)
        result = fit_in_area((480, 1500), FRAME, area, (2800, 1000))
        self.assert_inside(result, area)

    def test_the_save_row_stays_reachable_on_a_very_small_screen(self):
        area = (0, 0, 800, 560)
        result = fit_in_area((480, 900), FRAME, area, (400, 280))
        self.assert_inside(result, area)

    def test_never_gives_a_zero_or_negative_size(self):
        result = fit_in_area((480, 400), FRAME, (0, 0, 10, 10), (5, 5))
        self.assertGreaterEqual(result[2], 1)
        self.assertGreaterEqual(result[3], 1)

    def test_the_size_is_never_bigger_than_wanted(self):
        result = fit_in_area((300, 200), (0, 0), LAPTOP, (683, 364))
        self.assertEqual((result[2], result[3]), (300, 200))


if __name__ == "__main__":
    unittest.main()
