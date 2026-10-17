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

## 1-min/10-sec alert system — IN PROGRESS, main_window.py wiring baaki

User ne bola "jaldi implement karo" aur phir session limit ke karan "stop, jo bana hai de do". Isliye ye feature **adha bana hai**, abhi kahin call nahi hoti (purani app ka behavior nahi badla, sab 441 tests pass).

Ban chuka hai:
- `src/pomodoro/warning_timing.py` (NAYA): pure logic, no Qt. `should_show_one_minute_warning(remaining, total)` — 1 min left par True, lekin sirf agar block khud 1 min se lamba hai (1-min Custom block shuru hote hi warn nahi karta). `should_start_slide_in(remaining)` — True jab tak remaining 1-10 sec ke beech ho (pause ke baad resume par bhi turant trigger ho sake). Tests: `tests/test_warning_timing.py` (10 tests, sab pass).
- `src/pomodoro/ui/warning_toast.py` (NAYA): `WarningToast` (ek chhota frameless widget, har monitor ke liye) — neeche se slide-up (350ms), 2 sec hold, slide-down (350ms), khud close ho jata hai. `WarningToastManager.show_message(text)` — har screen par ek toast kholta hai.
- `src/pomodoro/ui/break_overlay.py`: `BreakOverlay` me `slide_in(final_rect, duration_ms)` aur `finish_slide(final_rect)` methods add kiye (QPropertyAnimation on geometry, neeche se upar). `close_for_real()` ab chalti animation ko bhi stop karta hai.
- `src/pomodoro/ui/break_manager.py`: `BreakOverlayManager` me `begin_slide_in(math_used, seconds, long_break=False)` (naya method — windows ko screen ke neeche khol kar `seconds` second me upar slide karta hai) aur `cancel_slide_in()` (pause hone par cancel karne ke liye) add kiye. `show()` ab agar overlay pehle se slide ho raha hai to usko **finalize** karta hai (snap to full position + real math_used/clock update) bajaye dobara kholne ke.

**Baaki hai (agli session me):**
1. `main_window.py` me wiring — abhi kuch bhi call nahi hota:
   - `__init__` me `self._one_minute_warned = False`, `self._slide_in_started = False`, `self._toast = WarningToastManager(self)` add karna.
   - `_on_toggle` me: fresh focus block start hone par (`remaining == full duration`) dono flags reset karna; Pause dabane par agar `self._overlay.is_active and not self._force_break_active` to `self._overlay.cancel_slide_in()` + `self._slide_in_started = False`.
   - Naya method `_check_focus_warnings()`: phase FOCUS + running ho to check karo `should_show_one_minute_warning` (toast dikhao + `_play_alert()`) aur `should_start_slide_in` (predicted long_break compute karke `self._overlay.begin_slide_in(...)` call karo). `_on_clock_check` ke **sabse upar** ye call karna hai (whole_seconds<1 wale early-return se pehle), warna check miss ho sakta hai.
   - Import add karna: `from pomodoro.warning_timing import should_show_one_minute_warning, should_start_slide_in` aur `from pomodoro.ui.warning_toast import WarningToastManager`.
2. Naye Qt-level tests likhna (break_manager slide-in/cancel, main_window ke naye flags/triggers) — abhi sirf pure-logic tests bane hain.
3. Poora suite chalana, docs update karna (naya behavior kahin docs me explain karna — shayad naya `docs/05c-...md` ya `08-pause-and-locks.md`/`05-force-break-overlay.md` me section), phir commit+push.
4. `docs/windows-checklist.md` me is feature ka naya section add karna.

Break → Focus transition **jaisa hai waisa hi rahega** — koi naya warning nahi, sirf end sound (jaisa pehle discuss hua tha).

## Baaki pending (checklist/alert system ke baad)

- Music delay fix — pehle user se pucho kaunsi awaaz (break shuru / focus khatam / background) delay se sunayi deti hai, tabhi code dekhna.

## Dhyan rakhne wali baatein

- `EMERGENCY_EXIT_ENABLED` (lock_rules.py) abhi `True` hai, testing ke liye. Real release se pehle `False` karna hai.
- Break screen ki min height 855 px hai.
- Mera PC path: `C:\Users\Abhimanyu\Documents\ProductiveTool\app-pomodoro-timer` (purana galat folder `...\Documents\app-pomodoro-timer` — usme kuch mat chalana)
- User ne bola: "test tum code se karoge main khud kuch nahi check karunga" — iska matlab automated suite (offscreen) chalakar khud confirm karna hai push se pehle. Windows par manual checklist user khud chalata hai, apni marzi se.
