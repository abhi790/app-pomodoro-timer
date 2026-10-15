# Step 5b: Leaving a Force Break early

The Force Break screen has no close button. There is one way out before the break ends: solve a math problem. There is **no daily cap** — it works every time, as many times a day as you need.

## 1. Solve a math problem

At the bottom of the break screen you see **Leave break early (solve a math problem)** and which level the next problem will be ("next: level 2 of 3").

1. Press the button. A problem appears, like `47 + 38 + 25 = ?` (see the levels below).
2. Type the answer and press **Enter** (or **Check**).
3. **Right answer:** the break ends right away. The timer waits on Focus, and you press **Start** when you are ready.
4. **Wrong answer:** you get a new problem of the same level.
5. **Back** returns to the first screen.

## The three levels

The problems need a moment of thought, so nobody solves one by reflex. They get **harder with every problem you solve in a day**, and the screen tells you the level of the next one ("next: level 2 of 3"):

| Solved today | Level | What it is | Examples |
|---|---|---|---|
| 1st | 1 | Two additions (sometimes one subtraction), two-digit numbers | `47 + 38 + 25`, `60 + 25 - 18` |
| 2nd | 2 | Two multiplications, times tables up to 12 | `4 × 6 × 7`, `7 × 8 + 6 × 4`, `9 × 8 - 5 × 7` |
| 3rd and every one after | 3 | A mix, with brackets and 3 or more signs | `(12 + 8) × 5 - 9`, `20 + 6 × 7 - 9`, `4 × 6 + 7 × 5 + 18` |

- Times is worked out before plus and minus, like in school. Brackets first.
- The answer is always a whole number from 1 up (and at most 600), and no step on the way goes below zero.
- A wrong answer gives a new problem of the **same level**.
- The pause screen (Stop) uses the same levels, because it reads the same daily count.
- The level follows the daily count in `usage.json`. After midnight you start at level 1 again.

There used to be a 3-a-day cap on this (and, before that, an **Important** button that cut the break to 3 minutes). Both were removed on purpose: solving the problem is itself the friction, so the count no longer runs out. An old `usage.json` that still has the old `important_used` number loads fine, and your math count is kept.

## Emergency exit (testing only)

While the app is still being tested, the break screen (and the pause screen) have a small **Emergency exit (testing only)** button in the bottom right corner. It has **no logic**: one press and you are out. No math problem, no count.

- On the **break screen** the break ends at once and the timer waits on Focus.
- On the **pause screen** the focus block is given up (it does not count) and the timer waits for Start. See [08-pause-and-locks.md](08-pause-and-locks.md).
- It floats in the corner and is not part of the layout, so it never makes the screen taller.
- It is **not part of the final product**. One switch removes it from both screens, before a real release: set `EMERGENCY_EXIT_ENABLED = False` in `src/pomodoro/lock_rules.py`. Nothing else has to change.

Without it (or if it is switched off), the only way out of a break early is a math problem. If you ever get really stuck, Task Manager still works, because the app does no system tricks (see [05-force-break-overlay.md](05-force-break-overlay.md)).

## The daily count

The count is saved in a small file, separate from the settings:

```
%APPDATA%\PomodoroTimer\usage.json
```

It holds today's date and one number (how many math problems were solved today). It is not a cap — it only decides how hard the next problem is. When the date changes (after midnight), the count starts again from zero, so the next problem is level 1 again. This also works if the app stays open through midnight.

If the file is missing or damaged, the app simply starts today's count from zero (tomorrow's first problem would be level 1 again).

## Trying it

The test buttons are gone. The real thing happens in both modes (Pomodoro and Custom): when a focus block ends, the break starts by itself and the screen covers the monitors, and every solved problem counts toward the next one's level. To try it quickly, use Custom with 1 minute of focus.

## Code

| File | What it does |
|---|---|
| `src/pomodoro/math_quiz.py` | Makes the problems of the 3 levels and checks answers (no windows, has tests) |
| `src/pomodoro/usage.py` | The daily count, saving, midnight reset (no windows, has tests) |
| `src/pomodoro/timer_logic.py` | `skip()` ends the break |
| `src/pomodoro/ui/unlock_panel.py` | The button and the quiz on the break screen (asks for the level of the next problem) |
| `src/pomodoro/ui/pause_overlay.py` | The same quiz on the pause screen |
| `tests/test_math_quiz.py`, `tests/test_math_levels_ui.py` | Tests for the levels |
| `src/pomodoro/ui/main_window.py` | Counts the solve and changes the timer |
