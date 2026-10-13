# Pomodoro Timer

A simple, free and open-source Pomodoro timer for your desktop (Windows).

> **Status:** work in progress. The app is being built step by step, and this README grows with every step.

## What is a Pomodoro timer?

A Pomodoro timer helps you focus. You work for a fixed block of time (a "pomodoro"), then take a short break. After a few blocks, you take a longer break.

## What this app does (and will do)

- **Classic Pomodoro:** 25 minutes of focus and a 5 minute break, for lighter work.
- **Custom timer:** choose your own focus (up to 45 minutes, for deep focus) and short break (at least 5 minutes).
- **Long break:** the same in both modes. After every 4 focus blocks you get a 1 hour break.
- **Force Break in both modes:** every break is a full-screen break on every monitor with healthy tips. There is no "reminder only" mode. You can only leave early by solving a simple math problem (3 times a day), or with the Important button once those are used up.
- **Testing phase only:** while the app is being tested, the break and pause screens have a small **Emergency exit** button in the bottom right corner. It leaves at once, with no math problem. It is removed before a real release with one switch (`EMERGENCY_EXIT_ENABLED` in `src/pomodoro/lock_rules.py`).
- **Alert sound:** a soft chime when a focus block or a break ends. You can switch it off or choose your own `.wav` sound in Settings.
- **Creative breaks:** the long break suggests something fun and creative, not studying (sketch, play music, go for a walk, write a poem...). You can add your own ideas in Settings.
- **A real Pomodoro, not a toy:** while the timer runs, Reset and Settings are locked. Pause covers the screen with Run and Stop. Stop needs a math problem (one of the 3 daily unlocks) and the interrupted block does not count. With no unlocks left, you can only Run.
- **Tray icon:** the app lives in the system tray. Hover to see the time left, close the window and the timer keeps running, and use **Quit** in the tray menu to close it for real.
- **Day and Night look:** a small button in the corner of the window switches between the dark Night look and a light Day look. The app remembers your choice. The break and pause screens always stay dark.
- **Light and simple:** no account, no internet, no ads.

## Tech stack

- **Python** with **PySide6** (Qt) for the desktop window
- **PyInstaller** to build a Windows `.exe` later
- **Git** and **GitHub** for version control

## How to run it

You need **Python 3.10 or newer** and **Git**. Open a Command Prompt and run these one by one:

```
git clone https://github.com/abhi790/app-pomodoro-timer
cd app-pomodoro-timer
python -m pip install -r requirements.txt
python run.py
```

A window opens with a countdown. Press **Start** to begin focusing. Once it runs, **Reset** and **Settings** are locked, like a real Pomodoro. **Pause** covers the screen, where you choose **Run** (carry on) or **Stop** (give the block up, after a math problem).

## Project layout

```
app-pomodoro-timer/
├── README.md          What you are reading
├── LICENSE            MIT license
├── run.py             Starts the app
├── requirements.txt   Python packages the app needs
├── src/pomodoro/      The app code
├── tests/             Automatic tests
└── docs/              Step-by-step guides
```

## Roadmap

- [x] Step 1: project setup (repo, license, README)
- [x] Step 2: timer logic (focus, short break, long break) with tests
- [x] Step 3: a simple window with Start, Pause and Reset
- [x] Step 4: settings screen and modes (Pomodoro and Custom, both with Force Break)
- [x] Step 4a-1: app icon (a tomato) for the window and the taskbar
- [x] Step 5a: Force Break full-screen overlay with healthy tips (all monitors)
- [x] Step 5b: math unlock, daily limit and the Important button
- [x] Test buttons and the Emergency exit removed (they were only for testing)
- [x] Step 8: Reset and Settings locked while running, Pause screen with Run and Stop (math)
- [x] Step 6: creative long-break suggestions (with your own ideas)
- [x] Step 7a: alert sound (a default chime, or your own `.wav`)
- [x] Step 7b: tray icon (the timer keeps running when you close the window)
- [x] Step 9: Day and Night look (a switch in the main window, remembered)
- [ ] Step 7c: a Windows `.exe`

## Run the tests

In a Command Prompt, inside the project folder:

```
python -m unittest discover -s tests -t . -v
```

All tests should say `ok`. The tests run without a real screen. On Windows that also means without real fonts, so the two tests that measure how tall a text is are **skipped** there (they say "skipped"; that is normal).

See [docs/02-timer-logic.md](docs/02-timer-logic.md) for what the timer does.

## Contributing

Ideas and improvements are welcome. Open an issue or a pull request on GitHub.

## License

Released under the [MIT License](LICENSE). You can use, copy and change this project freely.
