# Pomodoro Timer

A simple, free and open-source Pomodoro timer for your desktop (Windows).

> **Status:** just getting started. The app is being built step by step, and this README grows with every step.

## What is a Pomodoro timer?

A Pomodoro timer helps you focus. You work for a fixed block of time (a "pomodoro"), then take a short break. After a few blocks, you take a longer break.

## What this app will do

- **Customizable times:** choose your own focus length, short break and long break.
- **Focus blocks:** for example, 30 minutes of focus per pomodoro.
- **Long break:** after every 4 pomodoros, take a longer break (for example 1 hour).
- **Creative breaks:** the long break suggests something fun and creative, not studying (sketch, play music, go for a walk, write a poem...). You can add your own ideas.
- **Light and simple:** no account, no internet, no ads.

## Tech stack

- **Python** with **PySide6** (Qt) for the desktop window
- **PyInstaller** to build a Windows `.exe` later
- **Git** and **GitHub** for version control

## How to run it

Not ready yet. The app window comes in a later step. This section will explain, in simple words, how to install and start the app.

## Project layout

```
app-pomodoro-timer/
├── README.md          What you are reading
├── LICENSE            MIT license
├── requirements.txt   Python packages the app needs
├── src/pomodoro/      The app code
├── tests/             Automatic tests
└── docs/              Step-by-step guides
```

## Roadmap

- [x] Step 1: project setup (repo, license, README)
- [x] Step 2: timer logic (focus, short break, long break) with tests
- [ ] Step 3: a simple window with Start, Pause and Reset
- [ ] Step 4: settings screen (customize times)
- [ ] Step 5: creative long-break suggestions
- [ ] Step 6: sound, notifications and tray icon
- [ ] Step 7: build a Windows `.exe` and finish the docs

## Run the tests

You only need Python 3.10 or newer. In a Command Prompt, inside the project folder:

```
python -m unittest discover -s tests -t . -v
```

All tests should say `ok`. See [docs/02-timer-logic.md](docs/02-timer-logic.md) for what the timer does.

## Contributing

Ideas and improvements are welcome. Open an issue or a pull request on GitHub.

## License

Released under the [MIT License](LICENSE). You can use, copy and change this project freely.
