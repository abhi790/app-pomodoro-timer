# Step 9: Day and Night look

The app has two looks. **Night** is the dark look the app always had. **Day** is a light look for bright rooms.

## How to switch

A small button in the top right corner of the main window names the other look: **Day mode** while you are in Night, **Night mode** while you are in Day. Press it and every window changes at once.

- It works at any time, also while the timer runs. It is only a look, so it never touches the timer.
- Your choice is **remembered**. The next time you open the app it starts in the look you left.
- The app starts in **Night** the first time. Old settings files without the choice also start in Night, and nothing else in them is lost.

## What stays dark

The full-screen **break screen** and **pause screen** always stay dark, in both looks. They show a picture with white text on top, and that only reads well on a dark layer.

## Colors

All colors of both looks are in `src/pomodoro/appearance.py` (`NIGHT_PALETTE` and `DAY_PALETTE`). Change a color there and the whole app follows. The tests check that the text can be read easily in both looks (the contrast is at least 7:1 for the main text, 4.5:1 for the grey text, and 3:1 for the text on the blue Start button).

The settings file keeps the choice as `"appearance": "night"` or `"day"`:

```
%APPDATA%\PomodoroTimer\settings.json
```

If the value is missing or damaged, the app uses Night and keeps all your other settings.

## Code

| File | What it does |
|---|---|
| `src/pomodoro/appearance.py` | The two palettes, the switch rules and the contrast check (no windows, has tests) |
| `src/pomodoro/settings.py` | `AppConfig.appearance` is saved and loaded with the other settings |
| `src/pomodoro/ui/theme.py` | `build_style()` makes the style from a palette; `apply_theme()` can be called again to switch |
| `src/pomodoro/ui/main_window.py` | The switch button, saves your choice |
| `src/pomodoro/ui/break_overlay.py`, `pause_overlay.py` | Keep their own dark style |
| `tests/test_appearance.py`, `tests/test_theme_ui.py` | Tests for the rules above |

## Checking it on Windows

1. The small **Day mode** button shows in the top right corner. Press it: the window turns light and the button says **Night mode**.
2. Close the app (tray, **Quit**) and open it again: it starts in the look you left.
3. In Day, open **Settings**: it is light too, and all texts and boxes are easy to read.
4. In Day, press **Start**, then **Pause**: the pause screen is still dark with a picture, white text and see-through buttons.
5. In Day, let a focus block end (Custom, 1 min): the break screen is still dark.
6. Press the switch while the timer runs: the countdown does not jump or stop.
