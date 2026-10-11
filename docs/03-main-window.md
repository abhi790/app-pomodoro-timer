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

## Buttons

| Button | What it does |
|---|---|
| Start / Pause | Runs the countdown. Pause covers the screen with the pause screen (Run or Stop), see [08-pause-and-locks.md](08-pause-and-locks.md) |
| Reset | Goes back to a fresh first focus block, count at zero. Locked while the timer runs |

When a block ends, the timer moves to the next block and waits. Press Start when you are ready.

There is no Skip button on purpose: breaks are meant to be taken.
