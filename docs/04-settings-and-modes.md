# Step 4: Settings and modes

Click **Settings** in the main window to choose a mode and your times.

## Modes

| Mode | Focus | Short break | Long break | Long break after |
|---|---|---|---|---|
| Break Reminder | 25 min | 5 min | 60 min | 4 pomodoros |
| Force Break | 45 min | 10 min | 60 min | 4 pomodoros |
| Custom Timer | you choose | you choose | you choose | you choose |

- **Break Reminder** and **Force Break** have fixed times. The boxes are greyed out so you can see them but not change them.
- **Custom Timer** lets you set every number. If you switch to another mode and come back, your custom times are still there.
- Today, Force Break only changes the times. The full-screen break arrives in a later step.

## Saving

Press **Save** and the timer uses the new times. Your choice is remembered the next time you open the app.

If the timer is stopped, the current block restarts with its new length. If it is running, the current block keeps its remaining time and the new times are used from the next block.

The settings file is here (you can delete it to go back to the defaults):

```
%APPDATA%\PomodoroTimer\settings.json
```

If this file is missing or damaged, the app starts with the default times (30 min focus, 5 min short break, 60 min long break after 4 pomodoros).
