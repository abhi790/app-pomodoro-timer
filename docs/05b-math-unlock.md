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

## 3. Emergency exit

At the bottom right of the unlock panel there is always a small **Emergency exit** button. One click ends the break at once, with no math. It is not counted in the daily numbers. The timer waits on Focus, and you press **Start** when ready.

It is a safety net in case you get stuck during a long break. It may be removed or limited later.

## The daily count

The count is saved in a small file, separate from the settings:

```
%APPDATA%\PomodoroTimer\usage.json
```

It holds today's date and two numbers (math unlocks used, Important used). When the date changes (after midnight), the count starts again from zero. This also works if the app stays open through midnight.

If the file is missing or damaged, the app simply starts today's count from zero. You could delete the file to get your unlocks back, but then the promise to yourself is broken. It is meant to be an honest helper, not a lock.

## Trying it

The main window has three test buttons (the third, **Test: long break**, is explained in [06-creative-breaks.md](06-creative-breaks.md)). All of them show the break screen for 60 seconds on every monitor, and nothing is counted:

- **Test overlay:** shows the math button with "3 of 3" unlocks left. Solving a problem closes the test screen.
- **Test: no math left:** shows the screen as it looks after the 3 unlocks are used up, with the Important button. Pressing it hides the button and shows the message.

The real thing happens in **Force Break** mode (choose it in Settings): when a focus block ends, the break starts by itself and the screen covers the monitors.

## Code

| File | What it does |
|---|---|
| `src/pomodoro/math_quiz.py` | Makes the problems and checks answers (no windows, has tests) |
| `src/pomodoro/usage.py` | The daily count, saving, midnight reset (no windows, has tests) |
| `src/pomodoro/timer_logic.py` | `limit_remaining()` cuts the break to 3 minutes; `skip()` ends it |
| `src/pomodoro/ui/unlock_panel.py` | The buttons, the quiz and the Emergency exit on the break screen |
| `src/pomodoro/ui/main_window.py` | Counts the unlock and changes the timer |
