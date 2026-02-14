Maths-PuzzelUltra

Maths-PuzzelUltra is an arcade-style math puzzle game built with Pygame. Solve generated problems under different modes, build combo multipliers, fill a power gauge (time-slow), and reveal a picture puzzle piece-by-piece as you answer correctly.

Features

4 game modes

Classic (60s), Blitz (30s + bonus time on correct), Zen (effectively untimed), Daily Challenge (45s seeded by date).

Procedural problem generator with mixed formats:

Standard arithmetic by difficulty (easy / medium / hard)

“Solve for ?” (missing addend)

True/False problems (enter 1 for True, 0 for False).

Puzzle reveal system: each correct answer reveals one more puzzle tile; complete the puzzle to advance levels (except Zen).

Combo + multiplier scoring

Base points: 10 * level

Multiplier: min(3.0, 1.0 + (combo // 3) * 0.5) (resets after timeout or wrong answer).

Power gauge + time-slow

Gauge fills on correct, drops on wrong; when full, press Left Shift to activate a ~5s time-slow effect.

Juice / feedback

Particle burst on success, screen shake on wrong answers.

Sound effects (no asset files required)

Procedurally generated beeps via pygame.mixer + NumPy (correct / wrong / click / powerup).

UI

Hover-scaling buttons + numeric-only input box with blinking cursor.

Requirements

Python 3.x

Dependencies:

pygame

numpy

Install:

pip install pygame numpy

Run
python main.py


The window title is set to “Math Puzzle Pro Ultra” and the main menu title renders “PUZZLE ULTRA”.
