"""Healthy tips shown on the Force Break screen.

No windows here, so it is easy to test. Every tip belongs to a category
(water, food, move, ...). The break screen uses the category to pick a
matching background picture.

``TipRotator`` hands out the tips one by one in a shuffled order. It never
shows the same tip twice in a row, and it mixes the categories so you do not
get three water tips in a row.

``tip_display_seconds`` says how long a tip stays on screen: longer tips stay
longer, between 10 and 20 seconds.

To add your own tip, add one line to the right list below. Keep it short and
friendly, and make it something a person can do in a minute.
"""

import random
from collections import deque
from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass(frozen=True)
class Tip:
    category: str
    text: str


CATEGORIES = ("water", "food", "move", "eyes", "posture", "sleep", "mind")

CATEGORY_TITLE = {
    "water": "Stay hydrated",
    "food": "Eat well",
    "move": "Move your body",
    "eyes": "Rest your eyes",
    "posture": "Check your posture",
    "sleep": "Sleep well",
    "mind": "Calm your mind",
}

# How long a tip stays on screen, in seconds. The time grows with the length
# of the tip, so there is always enough time to read it.
MIN_TIP_SECONDS = 10
MAX_TIP_SECONDS = 20
BASE_SECONDS = 6
CHARS_PER_SECOND = 6


def tip_display_seconds(text: str) -> int:
    """How long to show this text, from 10 to 20 seconds.

    A short tip gets a few seconds more than reading needs, and every extra
    6 characters add one more second, up to the maximum.
    """
    seconds = round(BASE_SECONDS + len(text) / CHARS_PER_SECOND)
    return max(MIN_TIP_SECONDS, min(MAX_TIP_SECONDS, seconds))


_WATER = (
    "Drink a glass of water right now.",
    "Keep a bottle on your desk. If it is in sight, you will sip more often.",
    "Thirst is a late signal. Sip water through the day, not only when you feel dry.",
    "Pale yellow urine is a simple sign that you are drinking enough. Dark yellow means drink more.",
    "Start the morning with a glass of water before your first coffee or tea.",
    "Add a slice of lemon, cucumber or mint if plain water feels boring.",
    "Swap one sugary drink today for water or unsweetened tea.",
    "Have a glass of water with every meal.",
    "Water, herbal tea and coconut water all count towards your fluids.",
    "Feeling tired or foggy? A glass of water may help more than another coffee.",
    "Refill your bottle every time you take a break. Make it a habit.",
    "Warm water or herbal tea in a quiet moment can feel calming.",
    "Exercising or sweating? Drink a little extra water to replace what you lose.",
    "Take small, steady sips instead of gulping a litre at once.",
    "Fruits like watermelon, oranges and cucumber also add to your water intake.",
)

_FOOD = (
    "Eat a piece of fruit instead of a packaged snack.",
    "Fill half your plate with vegetables at your next meal.",
    "A handful of nuts is a filling snack with healthy fats and protein.",
    "Choose whole grains like oats, brown rice or whole wheat roti when you can.",
    "Include some protein in each meal: dal, eggs, paneer, fish, chicken, beans or tofu.",
    "Eat slowly and chew well. Your body needs about 20 minutes to feel full.",
    "Try not to eat while staring at a screen. You will notice when you are full.",
    "Keep fruit, roasted chana or nuts nearby, so a healthy snack is the easy choice.",
    "Colorful plates are healthy plates. Aim for different colors of vegetables and fruit.",
    "Fiber keeps you full and your gut happy. Think vegetables, fruit, lentils and whole grains.",
    "Do not skip meals and then overeat later. Regular meals keep your energy steady.",
    "Go easy on salt, deep-fried food and sugary sweets. Enjoy them as a treat, not every day.",
    "Curd, buttermilk or yogurt can be a good friend for your gut.",
    "Cook at home when you can. You decide the oil, salt and sugar.",
    "Read the label on packaged food. A short list of ingredients is usually a good sign.",
)

_MOVE = (
    "Stand up and walk around for a few minutes.",
    "Do ten slow squats. Keep your back straight and your weight on your heels.",
    "Try ten wall push-ups. Stand an arm's length from a wall and push away from it.",
    "Stretch your arms overhead, then lean gently to each side.",
    "Do twenty calf raises. Rise onto your toes, hold for a second, then lower slowly.",
    "Take the stairs instead of the lift whenever you can.",
    "March on the spot for one minute to get your blood flowing.",
    "Reach down towards your toes with soft knees and let your back and legs relax.",
    "Stretch your chest: clasp your hands behind your back and gently lift them.",
    "Aim for at least 150 minutes of moderate activity a week. A brisk walk counts.",
    "Do a few gentle hip circles in each direction to loosen up after sitting.",
    "A 10-minute walk after a meal is good for digestion and blood sugar.",
    "Hold a plank for 20 seconds. Keep your body in a straight line and breathe normally.",
    "Stretch a little in every break. Small habits add up to a lot.",
    "Dance to one song. Moving for fun still counts as exercise.",
)

_EYES = (
    "20-20-20 rule: look at something 20 feet away for 20 seconds.",
    "Blink slowly ten times. We blink much less when we stare at screens.",
    "Close your eyes and rest them for a minute.",
    "Rub your palms together until warm, then cup them gently over your closed eyes.",
    "Look out of a window and let your eyes relax on something far away.",
    "Keep your screen about an arm's length away, with the top at or just below eye level.",
    "Match your screen brightness to the room. A bright screen in a dark room strains the eyes.",
    "Dry eyes? Blink more often, and ask an eye doctor if it continues.",
    "Move your eyes slowly in a circle, clockwise and then back. Keep your head still.",
    "Reduce glare: avoid a bright window or lamp directly in front of or behind your screen.",
    "Make your text larger instead of squinting at small letters.",
    "Get your eyes checked regularly, especially if you spend long hours on screens.",
    "Look at a near object, then a far one, and repeat a few times to relax your focus.",
    "Night mode and warm light in the evening can be easier on your eyes.",
    "Spend some time outdoors in daylight. It is good for your mood and your eyes.",
)

_POSTURE = (
    "Check your posture: back straight, shoulders relaxed.",
    "Sit with your feet flat on the floor and your knees at about a right angle.",
    "Let your back rest against the chair so your lower back is supported.",
    "Roll your shoulders back ten times.",
    "Keep your elbows close to your body and your wrists straight when you type.",
    "Tuck your chin slightly and lengthen your neck. Do not let your head drift forward.",
    "Slowly tilt your head to one side, hold for a few seconds, then change sides.",
    "Shake out your hands and stretch your wrists.",
    "Raise your laptop so you look straight ahead, not down. A stand or a few books can help.",
    "Squeeze your shoulder blades together for five seconds, then relax. Repeat five times.",
    "Do not cross your legs for too long. Change your position often.",
    "The best posture is your next posture. Move and change position often.",
    "Stand up at least once an hour. Your body is built to move, not to sit still.",
    "Open your chest: pull your shoulders back and take one deep breath.",
    "Hold your phone at eye level when you can. Looking down for hours strains your neck.",
)

_SLEEP = (
    "Go to bed and wake up at about the same time every day, even on weekends.",
    "Most adults need seven to nine hours of sleep. Protect your bedtime like an appointment.",
    "Stop screens 30 to 60 minutes before bed. Read a book or listen to calm music instead.",
    "Keep your bedroom dark, quiet and cool. Your body sleeps better that way.",
    "Avoid coffee and strong tea in the late afternoon and evening.",
    "A heavy meal right before bed can disturb your sleep. Try to finish dinner 2 to 3 hours before.",
    "Get some morning sunlight. It helps set your body clock for the night.",
    "A nap of 10 to 20 minutes can refresh you. A long nap late in the day can hurt your night sleep.",
    "Write tomorrow's to-do list before bed so your mind can let go.",
    "Use your bed for sleep, not for work. Your brain learns that bed means rest.",
    "A warm shower or a few slow breaths can help your body wind down.",
    "Tired right now? A short rest for your eyes and mind is better than another coffee.",
    "If you wake at night, try not to look at the clock. It makes it harder to fall asleep again.",
    "Regular exercise helps you sleep better. Just avoid hard workouts right before bed.",
    "Sleep is when your body repairs itself. It is not wasted time.",
)

_MIND = (
    "Take five slow, deep breaths.",
    "Box breathing: in for four, hold for four, out for four, hold for four. Repeat a few times.",
    "Name three things you are grateful for right now.",
    "Look around: name five things you can see, four you can touch and three you can hear.",
    "Step outside for fresh air and a little sunlight if you can.",
    "Message or call someone you care about. A small chat can lift your mood.",
    "Play one song you love and just listen. No phone, no tasks.",
    "Close your eyes and relax your jaw, forehead and shoulders one by one.",
    "You do not have to do everything today. Pick the one thing that matters most.",
    "Be kind to yourself. Rest is part of doing good work, not a prize you must earn.",
    "Doodle, hum, or write a line in a notebook. Let your mind play for a few minutes.",
    "Smile gently, even if you do not feel like it. It can soften your mood a little.",
    "Breathe in slowly through your nose and breathe out longer through your mouth.",
    "Spend a minute watching clouds, trees or birds. Let your thoughts slow down.",
    "Feeling overwhelmed for many days? Talk to a friend, a family member or a professional.",
)

_BY_CATEGORY = {
    "water": _WATER,
    "food": _FOOD,
    "move": _MOVE,
    "eyes": _EYES,
    "posture": _POSTURE,
    "sleep": _SLEEP,
    "mind": _MIND,
}

HEALTHY_TIPS = tuple(
    Tip(category, text)
    for category in CATEGORIES
    for text in _BY_CATEGORY[category]
)


class TipRotator:
    """Gives the next tip each time ``next_tip()`` is called.

    Each round shows every tip once. Inside a round the tips take turns by
    category (water, food, move, ...), and the order is shuffled every round.
    """

    def __init__(
        self,
        tips: Sequence[Tip] = HEALTHY_TIPS,
        rng: Optional[random.Random] = None,
    ) -> None:
        if not tips:
            raise ValueError("tips must not be empty")
        self._tips = tuple(tips)
        self._rng = rng or random.Random()
        self._queue: deque = deque()
        self._last: Optional[Tip] = None

    def next_tip(self) -> Tip:
        if not self._queue:
            self._refill()
        tip = self._queue.popleft()
        self._last = tip
        return tip

    def _refill(self) -> None:
        by_category: dict = {}
        for tip in self._tips:
            by_category.setdefault(tip.category, []).append(tip)
        for items in by_category.values():
            self._rng.shuffle(items)

        names = list(by_category)
        self._rng.shuffle(names)
        # Do not start the new round with the category we just showed.
        if len(names) > 1 and self._last and names[0] == self._last.category:
            names.append(names.pop(0))

        order: list = []
        while any(by_category.values()):
            for name in names:
                if by_category[name]:
                    order.append(by_category[name].pop())

        # With only one category, make sure the same tip does not repeat.
        if len(order) > 1 and order[0] == self._last:
            order[0], order[-1] = order[-1], order[0]
        self._queue = deque(order)
