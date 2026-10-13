import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import pomodoro
from pomodoro.backgrounds import default_folder
from pomodoro.paths import package_dir


class PackageDirTest(unittest.TestCase):
    """Where the app's own files are: next to the code when run with Python,
    inside the bundle when run as the Windows .exe (PyInstaller)."""

    def test_run_with_python_it_is_the_folder_of_the_code(self):
        self.assertEqual(package_dir(), Path(pomodoro.__file__).resolve().parent)

    def test_run_as_an_exe_it_is_inside_the_bundle(self):
        with tempfile.TemporaryDirectory() as bundle:
            with mock.patch.object(sys, "frozen", True, create=True), mock.patch.object(
                sys, "_MEIPASS", bundle, create=True
            ):
                self.assertEqual(package_dir(), Path(bundle) / "pomodoro")

    def test_an_exe_without_a_bundle_folder_uses_the_folder_of_the_exe(self):
        with mock.patch.object(sys, "frozen", True, create=True), mock.patch.object(
            sys, "executable", str(Path("app") / "PomodoroTimer.exe")
        ):
            if hasattr(sys, "_MEIPASS"):
                self.skipTest("this Python really is a PyInstaller bundle")
            self.assertEqual(package_dir(), Path("app") / "pomodoro")

    def test_the_background_pictures_are_found_inside_the_bundle(self):
        with tempfile.TemporaryDirectory() as bundle:
            with mock.patch.object(sys, "frozen", True, create=True), mock.patch.object(
                sys, "_MEIPASS", bundle, create=True
            ):
                self.assertEqual(
                    default_folder(),
                    Path(bundle) / "pomodoro" / "assets" / "backgrounds",
                )

    def test_the_background_pictures_are_found_when_run_with_python(self):
        self.assertEqual(
            default_folder(), package_dir() / "assets" / "backgrounds"
        )
        self.assertTrue(default_folder().is_dir())


if __name__ == "__main__":
    unittest.main()
