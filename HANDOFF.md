# HANDOFF — Pomodoro Timer

Living status file. Updated after every small step, not just at the end.

## State

- Repo: github.com/abhi790/app-pomodoro-timer (main, public)
- main par pushed: `33a99c1` — "Remove the Reset button; the pomodoro count resets itself" (task 2)
- Pehle: `a2a9126` — task 1 (force rule hataya)

## Task 1: Force rule hatao — DONE, pushed (a2a9126)

- `lock_rules.py`: `can_stop()` hataya. Stop/leave-break ab hamesha offer hota hai, koi daily cap nahi.
- `usage.py`: `DAILY_MATH_LIMIT` aur `math_left` hataye. Sirf `math_used` (din ka count) bacha hai — iska kaam sirf agle math problem ka **level** decide karna hai (1/2/3), cap nahi.
- UI (`unlock_panel.py`, `pause_overlay.py`, `break_overlay.py`, `break_manager.py`, `main_window.py`): "X of 3 left" wali text hatakar "next: level X of 3" dikhaya. Leave/Stop button hamesha visible.
- Math levels **rakhe hain** (user ne confirm kiya) — 1st solve = level 1, 2nd = level 2, 3rd aur uske baad hamesha level 3. Midnight par level 1 se wapas.
- Docs update: `docs/05b-math-unlock.md`, `docs/08-pause-and-locks.md`, `docs/07c-exe.md`.

## Task 2: Reset button hatao — DONE, pushed (33a99c1)

- `main_window.py`: `_reset_button` aur `_on_reset` hataye. Ab sirf Start/Pause + Settings.
- `lock_rules.py`: `controls_enabled()` → `settings_enabled()`.
- `timer_logic.py`: `PomodoroTimer.reset()` method hataya. `completed_pomodoros` khud 0 ho jata hai jab **long break** khatam hoti hai (short break se reset nahi hota).
- Docs update: `docs/02-timer-logic.md`, `docs/03-main-window.md`, `docs/08-pause-and-locks.md`, `docs/05-force-break-overlay.md`, `docs/07b-tray.md`. Isi pass me `05-force-break-overlay.md`/`07b-tray.md` ke stale "3 times a day" (task 1 se bache) references bhi fix kiye.
- Behavior: "Pomodoros done" ab hamesha 0→4 cycle karega, kabhi bhi manually reset karne ki zarurat nahi.

Poora automated suite (dono task ke baad): **431 tests pass** (offscreen, Linux).

## Windows manual checklist — DONE banaya, pushed (push pending is commit ke saath)

User ne specifically maanga: "test cases likho jo mere PC par chala sakun, poori functionality check karne ke liye" — iske liye **`docs/windows-checklist.md`** banaya hai. Ye saari scattered "Checking it on Windows" doc-sections ko ek jagah combine karta hai, numbered checkboxes ke saath:
0. Setup, 1. Main window look/buttons, 2. Settings/modes, 3. Timer cycle + auto-reset (task 2), 4. Math unlock no-cap (task 1), 5. Pause screen, 6. Break screen features (tips/pictures/ideas/emergency exit), 7. Sound, 8. Day/Night, 9. Tray, 10. .exe build.

User isko khud Windows par chalayega, jo fail ho wo mujhe bolega (kaunsa number, kya expect tha vs kya hua).

**Abhi commit/push nahi hua hai — agla step yahi hai.**

## Agla kaam (checklist result ke baad)

- Naya 1-min/10-sec alert system (focus khatam hone se 1 min pehle: chhota taskbar-jaisa slide-up toast + sound; 10 sec pehle: break overlay dheere se neeche se slide-in, 0 sec par poora cover = break start). Break→Focus transition abhi jaisa simple rahega (sirf end sound, koi naya warning nahi). Design discuss/approved ho chuka hai, implementation abhi nahi hui.
- Music delay fix — pehle user se pucho kaunsi awaaz (break shuru / focus khatam / background) delay se sunayi deti hai, tabhi code dekhna.

## Dhyan rakhne wali baatein

- `EMERGENCY_EXIT_ENABLED` (lock_rules.py) abhi `True` hai, testing ke liye. Real release se pehle `False` karna hai.
- Break screen ki min height 855 px hai.
- Mera PC path: `C:\Users\Abhimanyu\Documents\ProductiveTool\app-pomodoro-timer` (purana galat folder `...\Documents\app-pomodoro-timer` — usme kuch mat chalana)
- User ne bola: "test tum code se karoge main khud kuch nahi check karunga" — iska matlab automated suite (offscreen) chalakar khud confirm karna hai push se pehle. Windows par manual checklist user khud chalata hai, apni marzi se.
