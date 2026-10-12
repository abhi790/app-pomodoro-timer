# Step 4: Settings and modes

Click **Settings** in the main window to choose a mode and your times.

## Modes

| Mode | Focus | Short break | Long break | Long break after |
|---|---|---|---|---|
| Pomodoro | 25 min | 5 min | 60 min | 4 pomodoros |
| Custom Timer | 1 to 45 min | 5 min or more | 60 min | 4 pomodoros |

There are only these two modes, and **both end every focus block with the full-screen Force Break** (see [05-force-break-overlay.md](05-force-break-overlay.md)). There is no "reminder only" mode.

- **Pomodoro** is the classic (25 / 5), good for lighter work. It has fixed times, and the boxes are greyed out so you can see them but not change them.
- **Custom Timer** lets you set your own focus and short break, with two limits: focus is **at most 45 minutes** (longer than that is not focus any more) and the short break is **at least 5 minutes**. The boxes do not go past these limits. If you switch to the other mode and come back, your custom times are still there.
- **The long break is the same in both modes:** 60 minutes, once after every 4 focus blocks (so after blocks 1 to 3 comes a short break, after block 4 the long one). It is shown in Custom too, but greyed out: it cannot be changed.

## Older settings files

A settings file saved by an older version is fixed when the app starts:

- a focus over 45 minutes, a break under 5 minutes or another long break is brought inside the limits
- the old **Break Reminder** mode becomes **Pomodoro**
- the old **Force Break** mode becomes **Custom** with 45 min focus and a 10 min short break (what Force Break used to be)

## The size of the Settings window

The Settings window always fits on your screen. It is never taller than the usable part of the screen (the part above the taskbar), and it is moved so that the whole window, with its title bar and the **Save** and **Cancel** buttons, can be seen. It opens in the middle of the main window, but is pushed back onto the screen if the main window is close to an edge.

If the content is taller than the window (a small laptop screen), the part above the buttons scrolls. **Save** and **Cancel** stay fixed at the bottom, so you never have to drag the window to reach them.

| File | What it does |
|---|---|
| `src/pomodoro/window_fit.py` | Works out the size and place that keep a window on the screen (no windows, has tests) |
| `src/pomodoro/ui/settings_dialog.py` | Uses it every time the window opens |
| `tests/test_window_fit.py`, `tests/test_settings_fit.py` | Tests for the above |

## Saving

Press **Save** and the timer uses the new times. Your choice is remembered the next time you open the app.

If the timer is stopped, the current block restarts with its new length. If it is running, the current block keeps its remaining time and the new times are used from the next block.

The settings file is here (you can delete it to go back to the defaults):

```
%APPDATA%\PomodoroTimer\settings.json
```

If this file is missing or damaged, the app starts with the default times (30 min focus, 5 min short break, 60 min long break after 4 pomodoros).
