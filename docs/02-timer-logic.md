# Step 2: Timer logic

The "brain" of the app lives in `src/pomodoro/timer_logic.py`. It has no window and no sound. It only counts time and decides what comes next.

## The cycle

With the default settings:

1. **Focus** for 30 minutes
2. **Short break** for 5 minutes
3. Repeat focus and short break
4. After the **4th** focus block, take a **long break** of 60 minutes
5. Start again from focus

## Customizable settings

| Setting | Default | Meaning |
|---|---|---|
| `focus_minutes` | 30 | Length of one focus block |
| `short_break_minutes` | 5 | Length of a short break |
| `long_break_minutes` | 60 | Length of the long break |
| `pomodoros_before_long_break` | 4 | Focus blocks before the long break |

All values must be whole numbers of at least 1.

## How it behaves

- The timer starts **stopped**. Press Start to run it.
- When a block ends, the timer moves to the next block and **stops**. This gives the app a moment to tell you, and you press Start when you are ready.
- **Skip** jumps to the next block. A skipped focus block does not count as done.
- **Reset** goes back to a fresh first focus block with the count at zero.

## Run the tests

From the project folder:

```
python -m unittest discover -s tests -t . -v
```

All tests should say `ok`.
