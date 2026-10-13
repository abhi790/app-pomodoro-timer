import os
import unittest
from pathlib import Path

from tools.build_exe import APP_NAME, build_command, exe_path, missing_inputs

ROOT = Path(__file__).resolve().parent.parent


def value_after(command: list, flag: str) -> str:
    return command[command.index(flag) + 1]


class BuildCommandTest(unittest.TestCase):
    def setUp(self):
        self.command = build_command(ROOT, python="PY")

    def test_it_runs_pyinstaller_with_the_given_python(self):
        self.assertEqual(self.command[:3], ["PY", "-m", "PyInstaller"])

    def test_there_is_no_black_console_window(self):
        self.assertIn("--windowed", self.command)
        self.assertNotIn("--console", self.command)

    def test_the_exe_is_called_pomodorotimer(self):
        self.assertEqual(APP_NAME, "PomodoroTimer")
        self.assertEqual(value_after(self.command, "--name"), "PomodoroTimer")

    def test_the_exe_gets_the_tomato_icon(self):
        icon = Path(value_after(self.command, "--icon"))
        self.assertEqual(icon.name, "pomodoro.ico")
        self.assertTrue(icon.is_file())

    def test_the_pictures_travel_inside_the_exe_where_the_code_looks_for_them(self):
        spec = value_after(self.command, "--add-data")
        source, destination = spec.split(os.pathsep)
        self.assertEqual(Path(source), ROOT / "src" / "pomodoro" / "assets")
        self.assertTrue((Path(source) / "backgrounds").is_dir())
        # package_dir() in the bundle is <bundle>/pomodoro, and the pictures
        # are looked for in <that>/assets/backgrounds.
        self.assertEqual(destination, "pomodoro/assets")

    def test_the_code_folder_is_on_the_search_path(self):
        self.assertEqual(Path(value_after(self.command, "--paths")), ROOT / "src")

    def test_the_windows_sound_module_is_not_left_out(self):
        self.assertEqual(value_after(self.command, "--hidden-import"), "winsound")

    def test_it_starts_from_run_py(self):
        self.assertEqual(Path(self.command[-1]), ROOT / "run.py")
        self.assertTrue(Path(self.command[-1]).is_file())

    def test_it_builds_a_folder_by_default_and_one_file_if_asked(self):
        self.assertIn("--onedir", self.command)
        self.assertNotIn("--onefile", self.command)
        single = build_command(ROOT, onefile=True, python="PY")
        self.assertIn("--onefile", single)
        self.assertNotIn("--onedir", single)

    def test_old_builds_are_cleaned_and_nothing_asks_questions(self):
        self.assertIn("--clean", self.command)
        self.assertIn("--noconfirm", self.command)

    def test_the_output_goes_to_dist_and_build_which_git_ignores(self):
        self.assertEqual(Path(value_after(self.command, "--distpath")), ROOT / "dist")
        self.assertEqual(Path(value_after(self.command, "--workpath")), ROOT / "build")
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8").split()
        for name in ("dist/", "build/", "*.spec"):
            self.assertIn(name, ignored)


class InputsTest(unittest.TestCase):
    def test_nothing_is_missing_in_this_project(self):
        self.assertEqual(missing_inputs(ROOT), [])

    def test_a_missing_file_is_named(self):
        empty = ROOT / "no-such-folder"
        missing = missing_inputs(empty)
        self.assertTrue(any("run.py" in item for item in missing))
        self.assertTrue(any("pomodoro.ico" in item for item in missing))
        self.assertTrue(any("backgrounds" in item for item in missing))


class ExePathTest(unittest.TestCase):
    def test_a_folder_build_puts_the_exe_inside_a_folder(self):
        self.assertEqual(
            exe_path(ROOT), ROOT / "dist" / "PomodoroTimer" / "PomodoroTimer.exe"
        )

    def test_a_one_file_build_puts_the_exe_in_dist(self):
        self.assertEqual(
            exe_path(ROOT, onefile=True), ROOT / "dist" / "PomodoroTimer.exe"
        )


if __name__ == "__main__":
    unittest.main()
