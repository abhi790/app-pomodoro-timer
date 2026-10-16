# Step 3: The main window

The window lives in `src/pomodoro/ui/main_window.py`. It only shows the timer on screen and passes button clicks to the timer logic from Step 2.

## Install and start

You need Python 3.10 or newer. In a Command Prompt, inside the project folder:

```
python -m pip install -r requirements.txt
python run.py
```

## What you see

- The current phase: **Focus** (red), **Short break** (green) or **Long break** (blue)
- A big countdown, for example `30:00`
- How many pomodoros you finished
- A short message when a block ends

The countdown also appears in the window title (for example `29:59 - Focus`), so you can read it in the taskbar.

## How it looks

- The timer block (phase, countdown, count, mode, message) sits in the **middle** of the window, with the same free space above and below it. It does not hang at the top any more.
- A small **Day mode / Night mode** button in the top right corner switches the look, see [09-day-night.md](09-day-night.md).
- **Start / Pause** is the main button, filled with the blue accent color. **Settings** is a plain button, so the one you press most is easy to find. The colors live in `src/pomodoro/ui/theme.py` (`QPushButton#primary`).
- `tests/test_main_window_look.py` checks both things.

## Buttons

| Button | What it does |
|---|---|
| Start / Pause | Runs the countdown. Pause covers the screen with the pause screen (Run or Stop), see [08-pause-and-locks.md](08-pause-and-locks.md) |

There is no Reset button. The count of finished pomodoros goes back to zero by itself once the long break ends.

When a block ends, the timer moves to the next block and waits. Press Start when you are ready.

There is no Skip button on purpose: breaks are meant to be taken.
