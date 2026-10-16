# HANDOFF — Pomodoro Timer

Living status file. Updated after every small step, not just at the end.

## State

- Repo: github.com/abhi790/app-pomodoro-timer (main, public)
- main par pushed: `a2a9126` — "Remove daily cap on the math unlock (force rule)" (task 1)
- Task 2 (Reset button hatana) local me DONE, test pass, push abhi baaki

## Task 1: Force rule hatao — DONE, pushed (a2a9126)

Kya badla:
- `lock_rules.py`: `can_stop()` hataya. Stop/leave-break ab hamesha offer hota hai, koi daily cap nahi.
- `usage.py`: `DAILY_MATH_LIMIT` aur `math_left` hataye. Sirf `math_used` (din ka count) bacha hai — iska kaam sirf agle math problem ka **level** decide karna hai (1/2/3), cap nahi.
- UI (`unlock_panel.py`, `pause_overlay.py`, `break_overlay.py`, `break_manager.py`, `main_window.py`): "X of 3 left" wali text aur cap-based button-hiding hatakar "next: level X of 3" dikhaya. Leave/Stop button hamesha visible.
- Math levels: **rakhe hain** (user ne confirm kiya) — 1st solve = level 1, 2nd = level 2, 3rd aur uske baad hamesha level 3. Koi daily reset nahi except midnight (naya din = level 1 se wapas).
- Tests: purane cap-wale tests hataye/update kiye. `tests/test_break_full_length.py` → `tests/test_no_important_button.py` (rename, kyunki "full length break" concept hi gaya).
- Docs update: `docs/05b-math-unlock.md`, `docs/08-pause-and-locks.md`, `docs/07c-exe.md`.

Windows par abhi real-device test nahi hua (task 5 me pending check list me hai).

## Task 2: Reset button hatao — DONE (local), push pending

Kya badla:
- `main_window.py`: `_reset_button` aur `_on_reset` hataye. Button bar me ab sirf Start/Pause + Settings.
- `lock_rules.py`: `controls_enabled()` → `settings_enabled()` (naam aur doc update, ab sirf Settings ke liye hai, Reset ka zikr nahi).
- `timer_logic.py`: `PomodoroTimer.reset()` method hataya (koi caller nahi bacha tha). Iski jagah: `completed_pomodoros` khud 0 ho jata hai jab long break khatam hoti hai (`_go_to_next_phase` me, chahe `skip()` se ho ya normal `tick()` se phase khatam ho). Short break is reset ko trigger nahi karta, sirf long break.
- Tests update: `test_lock_rules.py`, `test_pause_ui.py`, `test_emergency_exit.py`, `test_timer_logic.py`, `test_main_window_look.py` — Reset-wale asserts hataye/badle, naye tests add kiye (`test_there_is_no_reset_method_any_more`, `test_long_break_count_resets_itself`, `test_a_short_break_does_not_reset_the_count`, `test_there_is_no_reset_button_any_more`).
- Docs update: `docs/02-timer-logic.md`, `docs/03-main-window.md`, `docs/08-pause-and-locks.md`, `docs/05-force-break-overlay.md`, `docs/07b-tray.md`. (Isi pass me `05-force-break-overlay.md` aur `07b-tray.md` ke stale "3 times a day" task-1 references bhi fix kiye, jo pehle miss ho gaye the.)
- Poora suite: **431 tests pass** (offscreen, Linux).

Behavior: "Pomodoros done" ab hamesha 0→4 cycle karega (long break khatam hote hi 0 ho jayega), kabhi bhi manually reset karne ki zarurat nahi.

## Agla kaam

3. **Naya alert system** (discuss ho chuka, approved, abhi implement nahi hua):
   - Jab **focus chal raha ho aur 1 min baaki ho**: chhota taskbar-jaisa popup/toast screen ke bottom se slide-up ho kar aaye, 2 sec dikhe, ek chhota (non-continuous) sound bajaye, fir gayab ho jaye. ("Break aane wala hai" warning.)
   - Jab **focus me 10 sec baaki ho**: break ka overlay screen *dheere-dheere neeche se upar slide* hona shuru ho — countdown jaisa feel. Jab 0 sec par pahunche, overlay poori screen cover kar chuka ho — yahi break ka asli start hai, koi alag switch nahi.
   - **Break → Focus transition**: abhi jaisa simple rahega. Sirf ek sound end par, koi naya 1-min/10-sec warning nahi. (Auto-start next focus — purana task 3 — alag se discuss hoga, abhi scope me nahi.)
   - Implementation se pehle: current single end-of-phase chime (`sound.py` / `sound_player.py`) ke saath isko kaise integrate karna hai (replace ya saath me) — user se confirm karna.
4. Music delay fix (pehle Abhimanyu se pucho: kaunsi awaaz — break shuru/focus khatam/background. Abhi tak nahi poocha gaya, pichle context me reasoning kiya tha ki `winsound.PlaySound(..., SND_ASYNC)` turant chalna chahiye, delay ka exact source bina asli device check kiye pata nahi).
5. Windows par pending real checks (Day/Night, Settings position, pause tip, naya task-1 aur task-2 behavior, 2 purane failing tests dobara check karna).

## Dhyan rakhne wali baatein

- `EMERGENCY_EXIT_ENABLED` (lock_rules.py) abhi `True` hai, testing ke liye. Real release se pehle `False` karna hai.
- Break screen ki min height 855 px hai.
- Mera PC path: `C:\Users\Abhimanyu\Documents\ProductiveTool\app-pomodoro-timer` (purana galat folder `...\Documents\app-pomodoro-timer` — usme kuch mat chalana)
- User ne bola hai: "test tum code se karoge main khud kuch nahi check karunga" — matlab local suite (offscreen) chalakar hi confirm karna hai, Windows real-check sirf tab jab user khud chahe (task 5).
