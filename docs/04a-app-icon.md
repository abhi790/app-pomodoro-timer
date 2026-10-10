# Step 4a-1: App icon

The app has its own icon: a small red tomato with green leaves. ("Pomodoro" means tomato in Italian.)

You can see it:

- in the top-left corner of the app window
- on the taskbar
- in the Alt+Tab list

## How it is made

The tomato is drawn with code, so there is no picture file to carry around. It is drawn in seven sizes (16 to 256 pixels), and Windows picks the sharpest one for each place.

| File | What it does |
|---|---|
| `src/pomodoro/ui/app_icon.py` | Draws the tomato and packs the sizes into one icon |
| `src/pomodoro/main.py` | Sets the icon when the app starts |
| `tests/test_app_icon.py` | Checks the sizes, the red body, the green leaves and the transparent corners |

## Why the Windows ID line?

When you start the app with `python run.py`, Windows thinks it is just Python and shows the Python icon on the taskbar. One line, `set_windows_app_id()`, tells Windows this is its own app, so the taskbar shows the tomato. It does nothing on other systems.

## Later

The `.exe` in Step 7 needs an icon file (`.ico`). It will be made from this same tomato.
