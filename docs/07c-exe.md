# Step 7c: A Windows `.exe`

You can turn the app into a normal Windows program, so you can start it with a double click and no Python window. It uses **PyInstaller**.

## Build it

In a Command Prompt, from the project folder:

```
cd /d C:\Users\Abhimanyu\Documents\ProductiveTool\app-pomodoro-timer && git pull --ff-only && python -m pip install pyinstaller && python tools\build_exe.py
```

When it ends, you find the app here:

```
dist\PomodoroTimer\PomodoroTimer.exe
```

Start that file. **Keep the whole `dist\PomodoroTimer` folder together** (the exe needs the files next to it). You can copy the folder anywhere, or make a shortcut to the exe on the desktop.

Other ways to run the script:

| Command | What it does |
|---|---|
| `python tools\build_exe.py --dry-run` | Only shows the PyInstaller command, builds nothing |
| `python tools\build_exe.py --onefile` | One single `dist\PomodoroTimer.exe`. Simpler to copy, but it starts slower, because it unpacks itself every time |

The first build takes a minute or two. `build\` and `dist\` are not saved in git.

## What is inside

- the code and the Qt parts the app uses
- the background pictures (`src/pomodoro/assets`), kept at `pomodoro/assets` inside the bundle. `src/pomodoro/paths.py` finds them both with `python run.py` and in the exe
- the tomato icon `src/pomodoro/assets/pomodoro.ico`, used for the exe in Explorer and on the desktop. The window and the taskbar still use the tomato the app draws itself
- no black console window (`--windowed`)

Settings, the daily count and the default chime are written to `%APPDATA%\PomodoroTimer` when the app runs, **the same files as with `python run.py`**. So your settings and your 3 daily unlocks carry over, and the exe leaves nothing inside its own folder.

## The icon

The tomato is drawn by code, so there is no picture to download. `tools\make_icon.py` draws it in 7 sizes (16 to 256 pixels) and packs them into `pomodoro.ico`. `build_exe.py` makes the icon by itself if the file is missing. You only run `python tools\make_icon.py` if you change the tomato.

## The Emergency exit button

The exe still has the **Emergency exit (testing only)** button on the break and pause screens, because the app is in its testing phase. Before a real release, set `EMERGENCY_EXIT_ENABLED = False` in `src/pomodoro/lock_rules.py` and build again. See [05b-math-unlock.md](05b-math-unlock.md).

## Code

| File | What it does |
|---|---|
| `tools/build_exe.py` | Makes the PyInstaller command and runs it (`--onefile`, `--dry-run`) |
| `tools/make_icon.py` | Draws the tomato and writes `pomodoro.ico` |
| `src/pomodoro/icon_file.py` | Packs pictures into the bytes of an `.ico` file (no windows, has tests) |
| `src/pomodoro/paths.py` | Where the app's own files are: next to the code, or inside the exe (no windows, has tests) |
| `src/pomodoro/backgrounds.py` | Asks `paths.py` where the pictures are |
| `tests/test_build_exe.py`, `test_icon_file.py`, `test_paths.py` | Tests for the above |

## What was checked, and what was not

Checked by the automatic tests and by a trial build on Linux: the command is right, the icon file is a valid `.ico` with all 7 sizes, all 36 background pictures land in the bundle at the place the code looks, and the built program starts without an import error.

**Not checked (needs your Windows PC):** the build itself on Windows, the icon in Explorer, the tray, the alert sound (`winsound`), the files in `%APPDATA%`. Please run the list below and send me any error text.

## Checking it on Windows

1. Run the build command above. It ends with `Done. Start: ...PomodoroTimer.exe`. If it stops with an error, send me the text.
2. Double click `dist\PomodoroTimer\PomodoroTimer.exe`. The window opens and **no black console window** appears.
3. The exe in Explorer shows the **tomato** icon, and the taskbar shows it too.
4. Press **Start**. The tomato shows in the tray and its tooltip counts down.
5. Press **Settings**, then **Test** (sound): you hear the chime.
6. Custom, 1 min focus: when it ends, the full-screen break shows **a picture** behind the tip (not only a colored background).
7. Press **Day mode**, close the app (tray, **Quit**), start the exe again: it opens in Day. Your settings are the same as with `python run.py`.
