# Windows par poora manual check (saari functionality)

Ye ek hi jagah hai jahan app ka har feature check kar sakte ho, Windows par, haath se. Automated tests (`python -m unittest`) code ki logic check karte hain, lekin UI, sound, tray, .exe — ye sab sirf asli Windows par dikhte hain.

Suggestion: **Settings me Custom mode chuno, focus = 1 min, short break = 5 min** (minimum allowed) — taaki cycle jaldi complete ho aur har cheez jaldi test ho sake. Long break fix hai 60 min (kisi mode me badal nahi sakta), lekin usse bhi jaldi khatam karne ka tareeka neeche hai (step 6.5).

Har section ke saath checkbox hai — jo check ho jaye uske aage `[x]` kar dena apni copy me, ya bas mujhe bata dena kya fail hua.

---

## 0. Pehle setup

```
cd /d C:\Users\Abhimanyu\Documents\ProductiveTool\app-pomodoro-timer && git pull --ff-only && python run.py
```

- [ ] App khulta hai, koi error nahi aata.
- [ ] Title bar me clock aur phase dikhta hai (jaise `30:00 - Focus`).

## 1. Main window — look aur buttons

- [ ] Window me sirf 2 button hain: **Start/Pause** aur **Settings**. **Reset button nahi hai** (hataya gaya hai — task 2).
- [ ] Start button baaki buttons se alag dikhta hai (blue/filled), Settings plain hai.
- [ ] Timer window ke beech me hai, upar-neeche barabar jagah hai (ek badi khaali jagah upar nahi honi chahiye).
- [ ] Top-right corner me chhota **Day mode / Night mode** button hai.
- [ ] "Pomodoros done: 0" dikhta hai shuru me.

## 2. Settings aur modes

- [ ] **Settings** button dabao: dialog khulta hai, screen ke andar fit hota hai (chahe window kahin bhi ho), **Save** aur **Cancel** hamesha neeche dikhte hain.
- [ ] **Pomodoro** mode: times greyed out hain (25 min focus, 5 min break) — change nahi kar sakte.
- [ ] **Custom Timer** mode: focus 1–45 min ke beech set kar sakte ho, short break 5 min ya usse zyada. Long break hamesha 60 min, greyed out.
- [ ] Custom me focus = **1 min**, short break = **5 min** set karo, **Save** dabao.
- [ ] Timer stopped tha to turant naye time se dikhega. Agar running hota to current block apna time poora karta, agla block naye time se chalta.
- [ ] Settings dubara kholo: tumhare set kiye hue values wahi dikhte hain (saved hain).

## 3. Timer cycle aur auto-reset (task 2)

- [ ] **Start** dabao: countdown chalu hota hai, button "Pause" ho jata hai.
- [ ] Focus khatam hone do (1 min wait karo): sound bajti hai, **break screen apne aap** poori screen cover kar leti hai (koi click nahi karna padta).
- [ ] Break khatam hone do (5 min short break): sound bajti hai, break screen band ho jati hai, "Pomodoros done: 1" dikhta hai. Timer **ruka hua** hai, Start dabana padega.
- [ ] Ye 4 baar karo (4 focus blocks). 4th ke baad **Long break** (60 min) shuru hogi, "Pomodoros done: 4" dikhega.
- [ ] **Long break ko jaldi khatam karne ke liye:** break screen par "Leave break early (solve a math problem)" dabao, answer solve karo. Break turant khatam ho jayegi.
- [ ] Check karo: **"Pomodoros done" khud 0 ho gaya hai** (koi Reset button dabana nahi pada) — ye task 2 ka main point hai.
- [ ] Ek aur chhoti si cheez: agar sirf **short** break khatam hoti hai (4th se pehle), count reset NAHI hota — sirf long break ke baad hota hai.

## 4. Math unlock — break screen (task 1: koi daily cap nahi)

- [ ] Kisi bhi break (short ya long) ke dauraan **"Leave break early (solve a math problem)"** button dabao.
- [ ] Ek simple sum dikhta hai (jaise `47 + 38 + 25 = ?`), text kahta hai "next: level 1 of 3".
- [ ] Sahi answer do: break turant khatam ho jati hai.
- [ ] Ye **baar-baar** karo (kam se kam 4-5 baar alag-alag breaks me). Button **kabhi gayab nahi hota**, kahin bhi "X of 3 left" jaisi cap wali text nahi dikhni chahiye.
- [ ] Problem ki difficulty badhti jati hai: 1st baar level 1 (addition), 2nd baar level 2 (multiplication), 3rd baar aur uske baad hamesha level 3 (bracket mix) — jab tak midnight na ho jaye.
- [ ] Galat answer do: naya problem aata hai, **same level** ka, kuch "use" nahi hota.
- [ ] **Back** button se wapas menu pe aa sakte ho.

## 5. Pause screen

- [ ] Focus chalte waqt **Pause** dabao: poori screen (har monitor par) pause screen se dhak jati hai. Clock ruk jata hai.
- [ ] Healthy tip aur background picture dikhti hai, har 10-20 sec me badalti hai.
- [ ] **Run** dabao: screen gayab, clock wahi se chalu hota hai jahan rukka tha.
- [ ] Pause dabao, phir **Stop (solve a math problem)**: math problem dikhta hai, same level-system jaisa break me.
- [ ] Sahi answer do: focus block "stop" ho jata hai (count nahi hota), timer fresh focus block par wapas aa jata hai, stopped. "Focus stopped" message dikhta hai.
- [ ] Ye bhi **baar-baar** kaam karna chahiye, koi cap nahi.
- [ ] Pause screen ke dauraan Settings button disabled rehta hai.

## 6. Break screen ke features

- [ ] Har break me healthy tip + matching background picture dikhti hai (sirf color gradient nahi — asli picture, agar background images folder me hain).
- [ ] **Long break** (60 min): pehle ek "BE CREATIVE" wala purple-background idea dikhta hai, fir tips ke saath baari-baari chalta hai.
- [ ] Settings me "Your own long-break ideas" box me apni ek line likh kar Save karo — agli long break me wo bhi dikhni chahiye (idea rotate hote hain).
- [ ] **Emergency exit (testing only)** button bottom-right corner me dikhta hai (chhota, floating) — break screen aur pause screen dono par. Dabane se turant bahar nikal jata hai, koi math nahi, koi count nahi badalta. *(Ye sirf testing ke liye hai, release se pehle hata denge.)*

## 7. Sound

- [ ] Settings me "Play a sound..." checkbox ON hai by default.
- [ ] **Test** button dabao: chime bajti hai turant.
- [ ] Focus khatam hone par aur break khatam hone par sound bajti hai (dono baar).
- [ ] Break **early khatam** karne par (math se) sound **nahi** bajni chahiye — sirf natural phase-end par bajti hai.
- [ ] Settings me apna `.wav` file choose kar sakte ho (**Choose...**), **Default** se wapas built-in chime pe aa sakte ho.
- [ ] Checkbox OFF karke dekho: phase end hone par ab sound nahi bajti.

## 8. Day / Night mode

- [ ] Top-right **Day mode** button dabao: poori window light ho jati hai, button ab "Night mode" kehta hai.
- [ ] App band karke dubara kholo: tumne jo mode chhoda tha wahi khulta hai.
- [ ] Day mode me Settings kholo: wo bhi light hai, text/boxes saaf padhne layak hain.
- [ ] Day mode me Pause ya Break screen par jao: **ye dono hamesha dark hi rehti hain** (white text, dark background), chahe main window light ho.
- [ ] Day/Night switch timer chalte waqt dabao: countdown jump ya ruk nahi jata.

## 9. Tray (system tray, taskbar ke corner me)

- [ ] App chalao: taskbar tray me tomato icon dikhta hai (shayad `^` arrow ke andar).
- [ ] Mouse hover karo icon par: time left tooltip me dikhta hai, count down hota hai.
- [ ] Window ka **X** (close) dabao: window gayab ho jati hai lekin **app band nahi hoti**, tray me tomato tooltip chalta rehta hai.
- [ ] Tray icon par click karo: window wapas aa jati hai.
- [ ] Window hide karke, Custom 1-min focus khatam hone do: break screen **tab bhi** poori screen cover karti hai (window hidden hone ke bawajood).
- [ ] Break ke dauraan tray icon par right-click karo: **Quit** greyed out (disabled) hai.
- [ ] Break khatam hone par, agar window hidden thi: tray se ek pop-up/notification aata hai "Break is over. Ready to focus?".
- [ ] Right-click → **Quit**: app poori tarah band ho jati hai, tray se tomato gayab ho jata hai.

## 10. .exe build (agar time ho to)

```
cd /d C:\Users\Abhimanyu\Documents\ProductiveTool\app-pomodoro-timer
```
```
taskkill /F /IM PomodoroTimer.exe
```
```
python tools\build_exe.py
```

- [ ] Build "Done. Start: ...PomodoroTimer.exe" pe khatam hoti hai, koi error nahi.
- [ ] `dist\PomodoroTimer\PomodoroTimer.exe` double-click karo: window khulti hai, **koi black console window nahi** aati.
- [ ] .exe file aur taskbar dono par tomato icon dikhta hai.
- [ ] Start dabao: tray me tomato aur tooltip countdown kaam karta hai.
- [ ] Settings → Test: chime sunayi deti hai.
- [ ] Custom 1-min focus khatam hone do: break screen par picture dikhti hai (sirf color nahi).
- [ ] Day mode dabao, Quit karo, exe dubara kholo: Day mode me hi khulta hai (settings carry over hoti hain `python run.py` wali hi).

## Agar kuch fail ho

Jo bhi step fail ho, mujhe batao:
- Kaunsa number fail hua
- Kya expect kiya tha vs kya hua
- Agar automated test suite ka "FAIL:" block mila ho to wo poora paste kar dena

---

### Automated suite bhi chala sakte ho (optional, code-level check)

```
cd /d C:\Users\Abhimanyu\Documents\ProductiveTool\app-pomodoro-timer
```
```
pip install PySide6-Essentials
```
```
python -m unittest discover -s tests -t . -v
```

Ye upar wali manual checklist ka substitute nahi hai — ye sirf logic (timer math, levels, settings validation) check karta hai, UI/sound/tray asli screen par hi dikhte hain.
