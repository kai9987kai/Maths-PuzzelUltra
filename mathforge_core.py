import csv
import hashlib
import html
import json
import math
import random
import re
import tempfile
import zipfile
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


APP_TITLE = "MathForge X — Adaptive Mathematics Engine"
APP_VERSION = "2.0.0"

DIFFICULTY_ORDER = ["Beginner", "Easy", "Medium", "Hard", "Expert"]
DIFFICULTY = {
    "Beginner": {"level": 1, "rating": 800, "min": 1, "max": 10, "coeff": 5},
    "Easy": {"level": 2, "rating": 950, "min": 1, "max": 25, "coeff": 8},
    "Medium": {"level": 3, "rating": 1100, "min": -20, "max": 75, "coeff": 12},
    "Hard": {"level": 4, "rating": 1250, "min": -100, "max": 250, "coeff": 20},
    "Expert": {"level": 5, "rating": 1400, "min": -500, "max": 1000, "coeff": 35},
}

TOPICS = [
    "Mixed",
    "Addition",
    "Subtraction",
    "Multiplication",
    "Division",
    "Fractions",
    "Percentages",
    "Powers & Roots",
    "Order of Operations",
    "Ratios & Proportions",
    "Averages",
    "Scientific Notation",
    "Sequences",
    "Absolute Values",
    "Number Theory",
    "Probability",
    "Linear Equations",
    "Systems of Equations",
    "Quadratics",
]

SKILL_TOPICS = TOPICS[1:]

TOPIC_GROUPS = {
    "Arithmetic": ["Addition", "Subtraction", "Multiplication", "Division", "Order of Operations", "Averages"],
    "Number": ["Fractions", "Percentages", "Ratios & Proportions", "Scientific Notation", "Number Theory", "Probability"],
    "Algebra": ["Powers & Roots", "Sequences", "Absolute Values", "Linear Equations", "Systems of Equations", "Quadratics"],
}


# ----------------------------
# State helpers
# ----------------------------

def blank_profile() -> Dict[str, Any]:
    return {
        "version": APP_VERSION,
        "skills": {
            topic: {"rating": 1000.0, "attempts": 0, "correct": 0, "streak": 0, "best_streak": 0}
            for topic in SKILL_TOPICS
        },
        "total_attempts": 0,
        "total_correct": 0,
    }


def ensure_profile(profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    base = blank_profile()
    if not isinstance(profile, dict):
        return base
    old_skills = profile.get("skills", {}) if isinstance(profile.get("skills", {}), dict) else {}
    for topic in SKILL_TOPICS:
        old = old_skills.get(topic, {}) if isinstance(old_skills.get(topic, {}), dict) else {}
        for key in ["rating", "attempts", "correct", "streak", "best_streak"]:
            if key in old:
                try:
                    base["skills"][topic][key] = float(old[key]) if key == "rating" else int(old[key])
                except Exception:
                    pass
    base["total_attempts"] = sum(int(v["attempts"]) for v in base["skills"].values())
    base["total_correct"] = sum(int(v["correct"]) for v in base["skills"].values())
    return base


def _rng(seed: Any) -> random.Random:
    if seed in (None, ""):
        return random.Random()
    try:
        return random.Random(int(float(seed)))
    except Exception:
        return random.Random(str(seed))


def fmt_num(value: float, places: int = 8) -> str:
    if math.isfinite(value) and abs(value - round(value)) < 1e-10:
        return str(int(round(value)))
    return f"{value:.{places}f}".rstrip("0").rstrip(".")


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def problem_id(topic: str, question: str, answer: str, difficulty: str) -> str:
    raw = f"{APP_VERSION}|{topic}|{difficulty}|{question}|{answer}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:12]


def make_problem(
    topic: str,
    question: str,
    answer: str,
    hint: str,
    solution: str,
    concept: str,
    difficulty: str,
    answer_type: str = "scalar",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    p = {
        "id": problem_id(topic, question, answer, difficulty),
        "topic": topic,
        "question": question,
        "answer": answer,
        "hint": hint,
        "solution": solution,
        "concept": concept,
        "difficulty": difficulty,
        "rating": DIFFICULTY[difficulty]["rating"],
        "answer_type": answer_type,
        "metadata": metadata or {},
    }
    return p
