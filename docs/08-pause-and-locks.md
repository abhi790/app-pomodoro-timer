# Step 8: Pause screen and locked controls

A real Pomodoro is not something you fiddle with halfway. In the classic technique, if you are interrupted, that pomodoro is void and you start again. The app now follows the same idea.

## While the timer runs

- **Reset** and **Settings** are locked (greyed out). You cannot change the times or start over in the middle of a focus block.
- They work again when the timer is stopped: before the first Start, after a break, and after you Stop (see below).
- Start and Reset are also locked during a Force Break, as before.

## Pause covers the screen

**Pause** does not quietly stop the clock any more. It covers every monitor with the **pause screen**. The clock stands still and you choose:

- **Run (carry on focusing):** the screen goes away and the clock carries on from where it stopped. It costs nothing.
- **Stop (solve a math problem):** you give this focus block up. A math problem appears, like in a break. When you solve it:
  - the block does **not count** as a pomodoro (the ones you already finished stay counted),
  - the timer goes back to a fresh focus block and waits for **Start**,
  - it uses **one of the 3 daily math unlocks**, the same ones that end a break early.
- A wrong answer gives a new problem and costs nothing. **Back** returns to Run and Stop.

When the 3 math unlocks are used up, there is **no Stop button**. You can only Run. A focus block you started has to go on.

While the pause screen is up, Start, Reset, Settings and Quit (tray) are locked, just like during a break. The screen has no close button, ignores Alt+F4 and Esc, and comes back to the front if you click away. Task Manager and Ctrl+Alt+Del still work, because the app does no system tricks.

Pause is only for focus blocks. During a break the timer is locked anyway (see [05-force-break-overlay.md](05-force-break-overlay.md)).

## Code

| File | What it does |
|---|---|
| `src/pomodoro/lock_rules.py` | When Reset and Settings are locked, when Stop is offered (no windows, has tests) |
| `src/pomodoro/timer_logic.py` | `abandon_focus()` gives the block up without counting it |
| `src/pomodoro/tray_logic.py` | `can_quit()` is also false while the pause screen is up |
| `src/pomodoro/ui/pause_overlay.py` | The pause screen on each monitor: Run, Stop and the math problem |
| `src/pomodoro/ui/main_window.py` | Opens the pause screen, locks the buttons, handles Run and Stop |
| `src/pomodoro/ui/theme.py` | A disabled button now looks greyed out |
| `tests/test_lock_rules.py`, `tests/test_pause_ui.py` | Tests for the rules above |

## Checking it on Windows

1. Press **Start**: Reset and Settings turn grey and do nothing when clicked.
2. Press **Pause**: every monitor shows the pause screen with the time standing still.
3. Press **Run**: the screen goes and the clock carries on from the same second.
4. Press **Pause**, then **Stop**, solve the problem: the timer is back at a full focus block, stopped. The text says "Focus stopped". Reset and Settings work again. "Pomodoros done" did not go up.
5. Do step 4 three times in a day (or let breaks use the unlocks): the next Pause has only **Run**.
6. While the pause screen is up, right-click the tomato in the tray: **Quit** is greyed out.
