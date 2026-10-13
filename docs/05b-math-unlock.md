# Step 5b: Leaving a Force Break early

The Force Break screen has no close button. There are two ways out before the break ends, and both are limited on purpose.

## 1. Solve a math problem (3 times a day)

At the bottom of the break screen you see **Leave break early (solve a math problem)** and how many unlocks are left today ("2 of 3").

1. Press the button. A problem appears, like `47 + 38 = ?` or `7 × 8 = ?`.
2. Type the answer and press **Enter** (or **Check**).
3. **Right answer:** the break ends right away. The timer waits on Focus, and you press **Start** when you are ready.
4. **Wrong answer:** you get a new problem. A wrong answer does not use up an unlock.
5. **Back** returns to the first screen.

Only a *solved* problem counts. You have 3 of them each day.

The problems are easy but need a moment of thought: adding two numbers from 10 to 99, taking a smaller number from a bigger one, and times tables from 3 to 12.

## 2. The Important button

When the 3 math unlocks are used up, the math button goes away. In its place you get **Important: shorten the break to 3 minutes**.

- The break keeps going, but at most 3 more minutes remain (even if the real break was 10 or 60 minutes).
- If less than 3 minutes were left already, nothing gets longer. The break just continues as it was.
- There is no daily limit for Important yet. A limit can be added later in the settings.

While math unlocks are left, Important is hidden, because solving a problem is the better way out: it ends the break completely.

## Emergency exit (testing only)

While the app is still being tested, the break screen (and the pause screen) have a small **Emergency exit (testing only)** button in the bottom right corner. It has **no logic**: one press and you are out. No math problem, no daily count, no Important, no limit.

- On the **break screen** the break ends at once and the timer waits on Focus. No math unlock and no Important is used.
- On the **pause screen** the focus block is given up (it does not count) and the timer waits for Start. No math unlock is used. See [08-pause-and-locks.md](08-pause-and-locks.md).
- It floats in the corner and is not part of the layout, so it never makes the screen taller.
- It is **not part of the final product**. One switch removes it from both screens, before a real release: set `EMERGENCY_EXIT_ENABLED = False` in `src/pomodoro/lock_rules.py`. Nothing else has to change.

Without it (or if it is switched off), the way out of a break early is a math problem, or Important once those are used up. If you ever get really stuck, Task Manager still works, because the app does no system tricks (see [05-force-break-overlay.md](05-force-break-overlay.md)).

## The daily count

The count is saved in a small file, separate from the settings:

```
%APPDATA%\PomodoroTimer\usage.json
```

It holds today's date and two numbers (math unlocks used, Important used). When the date changes (after midnight), the count starts again from zero. This also works if the app stays open through midnight.

If the file is missing or damaged, the app simply starts today's count from zero. You could delete the file to get your unlocks back, but then the promise to yourself is broken. It is meant to be an honest helper, not a lock.

## Trying it

The test buttons are gone. The real thing happens in both modes (Pomodoro and Custom): when a focus block ends, the break starts by itself and the screen covers the monitors, and every solved problem counts. To try it quickly, use Custom with 1 minute of focus.

## Code

| File | What it does |
|---|---|
| `src/pomodoro/math_quiz.py` | Makes the problems and checks answers (no windows, has tests) |
| `src/pomodoro/usage.py` | The daily count, saving, midnight reset (no windows, has tests) |
| `src/pomodoro/timer_logic.py` | `limit_remaining()` cuts the break to 3 minutes; `skip()` ends it |
| `src/pomodoro/ui/unlock_panel.py` | The buttons and the quiz on the break screen |
| `src/pomodoro/ui/main_window.py` | Counts the unlock and changes the timer |
