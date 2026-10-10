# Step 5a: Force Break screen

In **Force Break** mode, a full-screen break window covers every monitor when your focus time ends.

## What happens

1. Your focus block finishes.
2. The break starts by itself and a full-screen window opens on **each monitor**.
3. The window shows the break countdown, a healthy tip and a matching background picture.
4. When the break ends, the windows close by themselves. The timer waits on Focus until you press **Start**.

Break Reminder and Custom Timer modes do not open this screen.

## Healthy tips

There are more than 100 tips in 7 categories:

| Category | Picture folder | Examples |
|---|---|---|
| Stay hydrated | `water` | drink water, sip through the day |
| Eat well | `food` | fruit, vegetables, protein, slow eating |
| Move your body | `move` | squats, stretches, a short walk |
| Rest your eyes | `eyes` | the 20-20-20 rule, blinking |
| Check your posture | `posture` | chair, screen height, shoulders |
| Sleep well | `sleep` | regular bedtime, less caffeine late in the day |
| Calm your mind | `mind` | deep breaths, gratitude, a short pause |

The tips are shuffled. The categories take turns, so you never get the same kind of tip twice in a row, and every tip is shown once before any tip comes back.

**How long a tip stays:** between 10 and 20 seconds. A short tip stays about 10 seconds, a longer tip stays longer so there is time to read it.

To add your own tips, open `src/pomodoro/tips.py` and add a line to the matching list.

## Background pictures

Each tip has a background picture that matches its category. The picture changes with a soft fade when the tip changes.

- The pictures live in `src/pomodoro/assets/backgrounds/<category>/`, named like `water_01.jpg`.
- If a category has no pictures, a soft colored background is shown instead, so the app always works.
- A dark layer is drawn over the picture so the white text stays easy to read.
- The prompts to create the pictures are in [background-image-prompts.md](background-image-prompts.md).

## What you cannot do (on purpose)

- There is no close or minimize button.
- Alt+F4 and Esc do nothing.
- If you click away, the window comes back to the front.

There are no system tricks. Task Manager and Ctrl+Alt+Del still work. In this step the only way out is to wait for the break to end. Solving a math problem to leave early comes in step 5b.

While the break is on, Start, Reset and Settings in the main window are locked.

## Trying it

The main window has a small **Test overlay** button. It shows the break screen for 20 seconds, then closes it. This button is only for testing and will be removed later. 20 seconds is long enough to see one or two tips.

## Code

| File | What it does |
|---|---|
| `src/pomodoro/tips.py` | The tips, their categories, the shuffle and the display time (no windows, has tests) |
| `src/pomodoro/backgrounds.py` | Finds and picks the background pictures (no windows, has tests) |
| `src/pomodoro/ui/break_overlay.py` | The full-screen window and the manager that opens one per monitor |
| `src/pomodoro/ui/main_window.py` | Starts the break and opens or closes the overlay |
