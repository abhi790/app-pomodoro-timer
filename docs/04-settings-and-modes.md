# Step 4: Settings and modes

Click **Settings** in the main window to choose a mode and your times.

## Modes

| Mode | Focus | Short break | Long break | Long break after |
|---|---|---|---|---|
| Break Reminder | 25 min | 5 min | 60 min | 4 pomodoros |
| Force Break | 45 min | 10 min | 60 min | 4 pomodoros |
| Custom Timer | 1 to 45 min | 5 min or more | 60 min | 4 pomodoros |

- **Break Reminder** is the classic Pomodoro (25 / 5), good for lighter work. **Force Break** (45 / 10) is for deep focus. Both have fixed times, and the boxes are greyed out so you can see them but not change them.
- **Custom Timer** lets you set your own focus and short break, with two limits: focus is **at most 45 minutes** (longer than that is not focus any more) and the short break is **at least 5 minutes**. The boxes do not go past these limits. If you switch to another mode and come back, your custom times are still there.
- **The long break is common to every mode:** 60 minutes, once after every 4 focus blocks (so after blocks 1 to 3 comes a short break, after block 4 the long one). It is shown in Custom too, but greyed out: it cannot be changed.
- A settings file saved by an older version, with a focus over 45 minutes, a break under 5 minutes or another long break, is fixed to these limits when the app starts.
- **Force Break** also covers every monitor with a full-screen break when a focus block ends. See [05-force-break-overlay.md](05-force-break-overlay.md).

## Saving

Press **Save** and the timer uses the new times. Your choice is remembered the next time you open the app.

If the timer is stopped, the current block restarts with its new length. If it is running, the current block keeps its remaining time and the new times are used from the next block.

The settings file is here (you can delete it to go back to the defaults):

```
%APPDATA%\PomodoroTimer\settings.json
```

If this file is missing or damaged, the app starts with the default times (30 min focus, 5 min short break, 60 min long break after 4 pomodoros).
