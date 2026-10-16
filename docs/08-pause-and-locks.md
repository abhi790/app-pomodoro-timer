# Step 8: Pause screen and locked controls

A real Pomodoro is not something you fiddle with halfway. In the classic technique, if you are interrupted, that pomodoro is void and you start again. The app now follows the same idea.

## While the timer runs

- **Settings** is locked (greyed out). You cannot change the times in the middle of a focus block.
- It works again when the timer is stopped: before the first Start, after a break, and after you Stop (see below).
- Settings is also locked during a Force Break, as before. (There is no Reset button: the count of finished pomodoros resets itself once the long break ends, see [02-timer-logic.md](02-timer-logic.md).)

## Pause covers the screen

**Pause** does not quietly stop the clock any more. It covers every monitor with the **pause screen**. The clock stands still and you choose:

- **Run (carry on focusing):** the screen goes away and the clock carries on from where it stopped. It costs nothing.
- **Stop (solve a math problem):** you give this focus block up. A math problem appears, like in a break (the level goes up with every problem solved today, see [05b-math-unlock.md](05b-math-unlock.md)). There is **no daily cap** — Stop is always offered. When you solve it:
  - the block does **not count** as a pomodoro (the ones you already finished stay counted),
  - the timer goes back to a fresh focus block and waits for **Start**,
  - it adds to the **same daily count** that ends a break early (used only to set the next problem's level).
- A wrong answer gives a new problem of the same level and costs nothing. **Back** returns to Run and Stop.

### What the pause screen looks like

- The same **healthy tips and background pictures** as the break screen (water, food, move, eyes, posture, sleep, mind). A tip stays 10 to 20 seconds, then the next one fades in. Every monitor shows the same tip. A pause is a small moment of rest too. (The creative ideas are only for the long break.)
- The **buttons are a little see-through**, so you still see the picture through them.
- The clock is a bit smaller than on the break screen, so the tip and the buttons always fit, even on a small laptop screen (checked at 1366 x 768 and 1920 x 1080). No tip is ever cut off.
- **A tip never gets cut off, whatever the font of your computer.** How tall a text is depends on the font and on the Windows display scale. So the tip is measured first: it is shown at the normal size (36), and only if it would be taller than its box does it get a smaller size (32, 29, 26 or at the smallest 24). Most tips keep the normal size. The next tip starts at the normal size again. The rule lives in `src/pomodoro/fit_text.py` (no windows, has tests).

**Testing only:** the pause screen also has a small **Emergency exit (testing only)** button in the bottom right corner. It gives the focus block up at once, with no math problem and no change to the daily count (the block does not count, the timer waits for Start). It is switched off for a real release, see [05b-math-unlock.md](05b-math-unlock.md#emergency-exit-testing-only).

While the pause screen is up, Start, Settings and Quit (tray) are locked, just like during a break. The screen has no close button, ignores Alt+F4 and Esc, and comes back to the front if you click away. Task Manager and Ctrl+Alt+Del still work, because the app does no system tricks.

Pause is only for focus blocks. During a break the timer is locked anyway (see [05-force-break-overlay.md](05-force-break-overlay.md)).

## Code

| File | What it does |
|---|---|
| `src/pomodoro/lock_rules.py` | When Settings is locked (no windows, has tests) |
| `src/pomodoro/timer_logic.py` | `abandon_focus()` gives the block up without counting it |
| `src/pomodoro/tray_logic.py` | `can_quit()` is also false while the pause screen is up |
| `src/pomodoro/ui/pause_overlay.py` | The pause screen on each monitor: tips, pictures, Run, Stop and the math problem |
| `src/pomodoro/ui/main_window.py` | Opens the pause screen, locks the buttons, handles Run and Stop |
| `src/pomodoro/ui/theme.py` | A disabled button looks greyed out, the see-through pause buttons, the smaller pause clock |
| `tests/test_lock_rules.py`, `tests/test_pause_ui.py` | Tests for the rules above |

## Checking it on Windows

1. Press **Start**: Settings turns grey and does nothing when clicked.
2. Press **Pause**: every monitor shows the pause screen with the time standing still, a healthy tip with a picture (it changes every 10 to 20 seconds) and see-through buttons.
3. Press **Run**: the screen goes and the clock carries on from the same second.
4. Press **Pause**, then **Stop**, solve the problem: the timer is back at a full focus block, stopped. The text says "Focus stopped". Settings works again. "Pomodoros done" did not go up.
5. Do step 4 several times in a day (or mix in breaks ended early): **Stop** is still offered every time, and the problems get harder (level 2, then level 3, then stays at 3).
6. While the pause screen is up, right-click the tomato in the tray: **Quit** is greyed out.
7. On the pause screen press **Emergency exit (testing only)** (bottom right): the screen goes at once, with no math problem. The timer is back at a full focus block, stopped. "Pomodoros done" did not go up, and the day's math count is unchanged.
8. Same on the break screen (Custom, 1 min focus): the button is in the bottom right corner, one press ends the break at once and the day's math count is unchanged.
