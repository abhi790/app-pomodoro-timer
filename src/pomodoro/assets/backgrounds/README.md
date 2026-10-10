# Background pictures

The Force Break screen shows one picture behind each healthy tip. Put the pictures in the folder that matches the tip category:

```
water/    food/    move/    eyes/    posture/    sleep/    mind/
```

Name them `<category>_01.jpg`, `<category>_02.jpg`, and so on (for example `water_01.jpg`). `.jpg`, `.jpeg`, `.png` and `.webp` all work.

- Use wide pictures (16:9). The app scales and crops them to fill each monitor.
- Keep each file under about 1 MB. JPG at quality 85 is a good choice.
- Add as many pictures per category as you like. The app shuffles them.
- A category with no pictures just shows a soft colored background, so nothing breaks.

The prompts used to create the pictures are in `docs/background-image-prompts.md`.

## If your pictures are named 0001_scene1.png ... 0028_scene28.png

You do not have to rename or convert them by hand. Put all the raw pictures in one folder **outside** the project (so the big PNG files are never added to Git), then run, in a Command Prompt from the project folder:

```
python tools\prepare_backgrounds.py <folder with the raw pictures>
```

The script reads the number in front of each file name (scene 1-4 water, 5-8 food, 9-12 move, 13-16 eyes, 17-20 posture, 21-24 sleep, 25-28 mind), makes each picture at most 2560 pixels wide, saves it as a small JPG and puts it in the right folder with the right name. Add `--dry-run` to only see what it would do.
