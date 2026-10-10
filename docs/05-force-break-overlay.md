# Step 5a: Force Break screen

In **Force Break** mode, a full-screen break window covers every monitor when your focus time ends.

## What happens

1. Your focus block finishes.
2. The break starts by itself and a dark full-screen window opens on **each monitor**.
3. The window shows the break countdown and a healthy tip. The tip changes every 12 seconds.
4. When the break ends, the windows close by themselves. The timer waits on Focus until you press **Start**.

Break Reminder and Custom Timer modes do not open this screen.

## What you cannot do (on purpose)

- There is no close or minimize button.
- Alt+F4 and Esc do nothing.
- If you click away, the window comes back to the front.

There are no system tricks. Task Manager and Ctrl+Alt+Del still work. In this step the only way out is to wait for the break to end. Solving a math problem to leave early comes in step 5b.

While the break is on, Start, Reset and Settings in the main window are locked.

## Trying it

The main window has a small **Test overlay** button. It shows the break screen for 20 seconds, then closes it. This button is only for testing and will be removed later.

## Code

| File | What it does |
|---|---|
| `src/pomodoro/tips.py` | The tips and the shuffle (no windows, has tests) |
| `src/pomodoro/ui/break_overlay.py` | The full-screen window and the manager that opens one per monitor |
| `src/pomodoro/ui/main_window.py` | Starts the break and opens or closes the overlay |
