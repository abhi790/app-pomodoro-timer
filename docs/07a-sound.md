# Step 7a: Alert sound

The app plays a sound when something ends, so you notice even if the window is hidden.

## When it plays

- when a **focus block ends** (the break screen opens)
- when a **break ends** (time to focus again)

It does **not** play when you leave a break early (math problem or Emergency exit), and the test buttons stay silent.

## The default chime

A soft three-note chime (about 2 seconds). It is made by the app itself, so there is no audio file to carry around. The first time it is needed, it is saved here:

```
%APPDATA%\PomodoroTimer\chime-v1.wav
```

## Settings

Open **Settings**:

- **Play a sound when a focus block or a break ends:** tick it on or off.
- **Choose...:** pick your own sound file.
- **Default:** go back to the built-in chime.
- **Test:** play the current sound right now (works even when the sound is switched off).

## Your own sound

- It must be a **`.wav`** file, at most **10 MB**. Other formats (like `.mp3`) are not supported yet, and the app tells you so if you pick one. If you only have an mp3, any free converter can turn it into a wav.
- A long sound is stopped after **15 seconds**, so a whole song does not play over your break.
- The same sound is used for both the focus end and the break end.
- If your file is moved or deleted later, the app plays the default chime instead, and Settings shows a note about it. The app is never silent by accident.
- The path is saved in `settings.json` (`sound_enabled` and `sound_file`). Old settings files without them still work: the sound is on, with the default chime.

## Good to know

- Sounds play only on **Windows**, using its built-in player, so no extra package is needed and the `.exe` stays small. On other systems the app stays quiet and nothing breaks.
- A sound problem (no sound card, a damaged file) never stops the timer. The app just stays quiet.
- The Settings window now scrolls. On a small screen it is never taller than the screen, and **Save** and **Cancel** always stay in sight.

## Code

| File | What it does |
|---|---|
| `src/pomodoro/sound.py` | Makes the default chime, checks your file, picks which file to play (no windows, has tests) |
| `src/pomodoro/ui/sound_player.py` | Plays the file in the background with the Windows player, never raises |
| `src/pomodoro/settings.py` | `sound_enabled` and `sound_file` are saved with the other settings |
| `src/pomodoro/ui/settings_dialog.py` | The checkbox and the Choose, Default and Test buttons |
| `src/pomodoro/ui/main_window.py` | Plays the sound when focus or a break ends |
| `tests/test_sound.py`, `tests/test_sound_ui.py` | Tests for the rules above |
