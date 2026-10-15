# HANDOFF — Pomodoro Timer

Living status file. Updated after every small step, not just at the end.

## State

- Repo: github.com/abhi790/app-pomodoro-timer (main, public)
- main par commit (abhi push hona baaki): force-rule removal (task 1)
- Pehle jo latest tha: `ebe47a0` — "feat: multilevel math problems - harder with every unlock used in a day"

## Task 1: Force rule hatao — DONE (local, test pass, push pending)

Kya badla:
- `lock_rules.py`: `can_stop()` hataya. Stop/leave-break ab hamesha offer hota hai, koi daily cap nahi.
- `usage.py`: `DAILY_MATH_LIMIT` aur `math_left` hataye. Sirf `math_used` (din ka count) bacha hai — iska kaam sirf agle math problem ka **level** decide karna hai (1/2/3), cap nahi.
- UI (`unlock_panel.py`, `pause_overlay.py`, `break_overlay.py`, `break_manager.py`, `main_window.py`): "X of 3 left" wali text aur cap-based button-hiding hatakar "next: level X of 3" dikhaya. Leave/Stop button hamesha visible.
- Math levels: **rakhe hain** (user ne confirm kiya) — 1st solve = level 1, 2nd = level 2, 3rd aur uske baad hamesha level 3. Koi daily reset nahi except midnight (naya din = level 1 se wapas).
- Tests: purane cap-wale tests hataye/update kiye. `tests/test_break_full_length.py` → `tests/test_no_important_button.py` (rename, kyunki "full length break" concept hi gaya).
- Docs update: `docs/05b-math-unlock.md`, `docs/08-pause-and-locks.md`, `docs/07c-exe.md`.
- Poora suite: **428 tests pass** (offscreen, Linux).

Windows par abhi test nahi hua (task 5 me pending check list me add hoga).

## Agla kaam (order se)

2. Reset button hatao (pehle check: kahin aur to use nahi ho raha)
3. Break ke baad agla focus auto-start (chhota countdown ke saath)
4. Music delay fix (pehle Abhimanyu se pucho: kaunsi awaaz — break shuru/focus khatam/background)
5. Windows par pending real checks (Day/Night, Settings position, pause tip, 2 failing tests)

## Dhyan rakhne wali baatein

- `EMERGENCY_EXIT_ENABLED` (lock_rules.py) abhi `True` hai, testing ke liye. Real release se pehle `False` karna hai.
- Break screen min height 855px.
- Mera PC path: `C:\Users\Abhimanyu\Documents\ProductiveTool\app-pomodoro-timer` (purana galat folder `...\Documents\app-pomodoro-timer` — usme kuch mat chalana)
