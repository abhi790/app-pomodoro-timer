# Step 6: Creative long breaks

A long break is the time to do something fun and creative, not something that feels like studying. The app now suggests an idea such as "Sketch the object nearest to you" or "Write a six-word story about this week". You can add your own ideas too.

## Where you see the ideas

**Both modes (Pomodoro and Custom Timer).** When a long break starts, the full-screen break window shows a creative idea first, under the title **BE CREATIVE**, on a purple background. After that, an idea and a healthy tip take turns, so you still get the water, posture and eye tips. Short breaks only show the healthy tips, as before.

## Your own ideas

1. Open **Settings**.
2. Write one idea per line in the box **Your own long-break ideas**.
3. Press **Save**.

Your ideas are mixed in with the built-in ones, and every idea is shown once before any idea comes back. The same idea never shows twice in a row.

A few rules keep the screen readable. These are applied automatically when you save:

- extra spaces are squeezed and empty lines are dropped
- an idea longer than 140 characters is cut at 140
- repeats are dropped (capital letters do not matter), also when your idea is already a built-in one
- the first 100 ideas are kept

Your ideas can use any alphabet. They are saved in the same file as the other settings (the file is created or updated when you press Save):

```
%APPDATA%\PomodoroTimer\settings.json
```

Settings files from older versions still work. They simply have no ideas of your own.

To change the built-in list, open `src/pomodoro/ideas.py` and edit `CREATIVE_IDEAS`.

## Trying it

The main window has a third test button, **Test: long break**. It shows the break screen for 60 seconds on every monitor, the way a long break looks, with an idea first. Nothing is counted. Like the other two test buttons, it is only for testing and will be removed later.

## Code

| File | What it does |
|---|---|
| `src/pomodoro/ideas.py` | The built-in ideas, tidying your ideas, and the shuffle (no windows, has tests) |
| `src/pomodoro/settings.py` | `AppConfig.ideas` is saved and loaded with the other settings |
| `src/pomodoro/ui/settings_dialog.py` | The box for your own ideas |
| `src/pomodoro/ui/break_manager.py` | In a long break, an idea and a tip take turns |
| `src/pomodoro/ui/break_overlay.py` | The "Be creative" title and the purple background |
| `src/pomodoro/ui/main_window.py` | Starts the long break with the idea |
| `tests/test_ideas.py`, `tests/test_long_break_ui.py` | Tests for the rules above |

## Later

The ideas have no background pictures yet. If you add pictures in `src/pomodoro/assets/backgrounds/creative/`, they will be used automatically, just like the other categories.
