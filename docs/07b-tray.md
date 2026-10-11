# Step 7b: Tray icon

The app now lives in the system tray (the small icons next to the clock). You can close the window and the timer keeps going.

## What you see

- A small **tomato** in the tray.
- Hover over it: you see the time left, like `Focus 24:59`. A stopped timer shows `Focus 25:00 (paused)`.
- Click or double-click the tomato: the window comes back.
- Right-click the tomato: a menu with **Show window** and **Quit**.

## Closing the window

- The **close button (X)** does not stop the app. The window hides to the tray and the timer keeps running. The first time, a small pop-up says so.
- To really close the app, right-click the tomato and choose **Quit**.
- If the tray icon is hidden by Windows (inside the `^` arrow near the clock), click the arrow and drag the tomato out if you want it always visible.

## During a break

- The full-screen **Force Break appears even if the main window is hidden** in the tray.
- **Quit is greyed out during a Force Break**, just like Start, Reset and Settings are locked then. After the break (or after leaving it early) it works again. The Emergency exit on the break screen is still the way out of a break.
- When a break ends while the window is hidden, a small pop-up from the tray says **"Break is over. Ready to focus?"**. The sound plays as usual.

## If there is no tray

If a computer has no system tray, the app does not hide anything: the close button closes the app, as before. The window can never disappear with no way to bring it back.

## Good to know

- The app no longer quits just because no window is open (the break screens open and close by themselves). It quits only with **Quit** (or the close button when there is no tray).
- Closing the app with Quit stops the timer. Nothing is saved except your settings, as before.

## Code

| File | What it does |
|---|---|
| `src/pomodoro/tray_logic.py` | The rules: tooltip text, close button action, when Quit is allowed (no windows, has tests) |
| `src/pomodoro/ui/tray.py` | The tray icon, its menu and pop-ups (does nothing if there is no tray) |
| `src/pomodoro/ui/main_window.py` | Hides to the tray on close, Quit, updates the tooltip |
| `src/pomodoro/main.py` | `setQuitOnLastWindowClosed(False)` |
| `tests/test_tray_logic.py`, `tests/test_tray_ui.py` | Tests for the rules above |

## Checking it on Windows

The tray cannot be seen in the automatic tests. Please check these by hand:

1. The tomato shows in the tray (maybe inside the `^` arrow).
2. Hover: the time left shows and counts down.
3. Press X: the window goes, the app stays, the tooltip keeps counting.
4. Click the tomato: the window comes back.
5. Hidden window + focus ends (Custom, 1 min): the break screen still covers every monitor.
6. During the break, right-click the tomato: **Quit** is greyed out.
7. After the break, a pop-up says the break is over.
8. Right-click, **Quit**: the app closes and the tomato disappears.
