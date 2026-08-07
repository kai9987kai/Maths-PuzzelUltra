import math
import random
from typing import Any, Dict, List, Optional

from mathforge_core import *
from mathforge_generators import generate_one
from mathforge_evaluation import equivalent, diagnose_mistake
from mathforge_worksheet import weighted_topic_choice, difficulty_from_rating


def choose_adaptive_topic(focus: str, profile: Dict[str, Any], r: random.Random) -> str:
    if focus != "Mixed":
        return focus
    return weighted_topic_choice(profile, r, SKILL_TOPICS)


def target_difficulty_for_topic(topic: str, profile: Dict[str, Any], challenge_bias: int) -> str:
    p = ensure_profile(profile)
    rating = float(p["skills"][topic]["rating"]) + int(challenge_bias) * 55
    return difficulty_from_rating(rating)


def render_problem(problem: Optional[Dict[str, Any]], session: Dict[str, Any]) -> str:
    if not problem:
        return "### Adaptive problem\nPress **Start / New Problem** to begin."
    n = int(session.get("question_number", 1))
    score = int(session.get("score", 0))
    return (
        f"### Adaptive problem {n}\n\n"
        f"## {problem['question']}\n\n"
        f"<sub>{problem['topic']} · {problem['difficulty']} · {problem['concept']} · challenge {problem['id']}</sub>\n\n"
        f"**Session score:** {score}/{max(0, n-1)} completed"
    )


def start_adaptive(focus: str, seed: Any, challenge_bias: int, profile: Dict[str, Any]):
    p = ensure_profile(profile)
    try:
        seed_i = int(float(seed)) if seed not in (None, "") else random.SystemRandom().randint(1, 2_000_000_000)
    except Exception:
        seed_i = random.SystemRandom().randint(1, 2_000_000_000)
    session = {"seed": seed_i, "step": 0, "question_number": 1, "score": 0, "answered": False, "current": None}
    r = random.Random(seed_i)
    t = choose_adaptive_topic(focus, p, r)
    diff = target_difficulty_for_topic(t, p, int(challenge_bias))
    problem = generate_one(t, diff, r)
    session["current"] = problem
    return render_problem(problem, session), "", "", session, p, mastery_markdown(p), recommendation_markdown(p), ""


def update_mastery(profile: Dict[str, Any], topic: str, problem_rating: float, correct: bool) -> Dict[str, Any]:
    p = ensure_profile(profile)
    skill = p["skills"][topic]
    rating = float(skill["rating"])
    expected = 1.0 / (1.0 + 10 ** ((problem_rating - rating) / 400.0))
    outcome = 1.0 if correct else 0.0
    k = 36.0 if int(skill["attempts"]) < 10 else 24.0
    delta = k * (outcome - expected)
    skill["rating"] = round(max(650.0, min(1550.0, rating + delta)), 2)
    skill["attempts"] = int(skill["attempts"]) + 1
    if correct:
        skill["correct"] = int(skill["correct"]) + 1
        skill["streak"] = int(skill["streak"]) + 1
        skill["best_streak"] = max(int(skill["best_streak"]), int(skill["streak"]))
    else:
        skill["streak"] = 0
    p["total_attempts"] = int(p.get("total_attempts", 0)) + 1
    p["total_correct"] = int(p.get("total_correct", 0)) + (1 if correct else 0)
    return p


def adaptive_check(user_answer: str, session: Dict[str, Any], profile: Dict[str, Any], history: List[Dict[str, Any]]):
    p = ensure_profile(profile)
    history = list(history or [])
    session = dict(session or {})
    problem = session.get("current")
    if not problem:
        return "Start a problem first.", "", session, p, history, mastery_markdown(p), recommendation_markdown(p)
    if session.get("answered"):
        return "This problem has already been scored. Use **Next adaptive problem**.", problem["solution"], session, p, history, mastery_markdown(p), recommendation_markdown(p)
    correct = equivalent(user_answer, problem)
    p = update_mastery(p, problem["topic"], float(problem["rating"]), correct)
    session["answered"] = True
    session["score"] = int(session.get("score", 0)) + (1 if correct else 0)
    record = {
        "n": int(session.get("question_number", 1)),
        "topic": problem["topic"],
        "difficulty": problem["difficulty"],
        "question": problem["question"],
        "user_answer": user_answer,
        "expected": problem["answer"],
        "correct": correct,
        "id": problem["id"],
    }
    history.append(record)
    history = history[-100:]
    if correct:
        feedback = f"✅ **Correct.** `{problem['answer']}`\n\nMastery updated for **{problem['topic']}**."
        diagnostic = "No error detected."
    else:
        diagnostic = diagnose_mistake(user_answer, problem)
        feedback = f"❌ **Not correct.** {diagnostic}\n\n**Hint:** {problem['hint']}"
    solution = f"**Worked solution:** {problem['solution']}"
    return feedback, solution, session, p, history, mastery_markdown(p), recommendation_markdown(p)


def adaptive_next(focus: str, challenge_bias: int, session: Dict[str, Any], profile: Dict[str, Any]):
    p = ensure_profile(profile)
    session = dict(session or {})
    if not session:
        return start_adaptive(focus, 42, challenge_bias, p)[:5] + ("",)
    step = int(session.get("step", 0)) + 1
    base_seed = int(session.get("seed", 42))
    r = random.Random(base_seed + step * 104729)
    t = choose_adaptive_topic(focus, p, r)
    diff = target_difficulty_for_topic(t, p, int(challenge_bias))
    problem = generate_one(t, diff, r)
    session.update({"step": step, "question_number": int(session.get("question_number", 1)) + 1, "answered": False, "current": problem})
    return render_problem(problem, session), "", "", session, ""


def history_markdown(history: List[Dict[str, Any]]) -> str:
    if not history:
        return "No adaptive attempts yet."
    rows = ["| # | Topic | Difficulty | Result | Challenge |", "|---:|---|---|:---:|---|"]
    for h in list(history)[-20:][::-1]:
        rows.append(f"| {h['n']} | {h['topic']} | {h['difficulty']} | {'✅' if h['correct'] else '❌'} | `{h['id']}` |")
    return "\n".join(rows)


def mastery_markdown(profile: Dict[str, Any]) -> str:
    p = ensure_profile(profile)
    ranked = sorted(SKILL_TOPICS, key=lambda t: p["skills"][t]["rating"], reverse=True)
    lines = ["| Skill | Mastery | Level | Accuracy | Attempts |", "|---|---:|---|---:|---:|"]
    for t in ranked:
        s = p["skills"][t]
        attempts = int(s["attempts"])
        acc = (100 * int(s["correct"]) / attempts) if attempts else 0.0
        lines.append(f"| {t} | {float(s['rating']):.0f} | {difficulty_from_rating(float(s['rating']))} | {acc:.0f}% | {attempts} |")
    return "\n".join(lines)


def recommendation_markdown(profile: Dict[str, Any]) -> str:
    p = ensure_profile(profile)
    attempted = [t for t in SKILL_TOPICS if p["skills"][t]["attempts"] > 0]
    if not attempted:
        return "### Coach signal\nComplete a few adaptive problems and MathForge X will identify weak areas and calibrate difficulty."
    weakest = sorted(attempted, key=lambda t: (p["skills"][t]["rating"], p["skills"][t]["attempts"]))[:3]
    strongest = sorted(attempted, key=lambda t: p["skills"][t]["rating"], reverse=True)[:2]
    total = int(p["total_attempts"])
    correct = int(p["total_correct"])
    acc = 100 * correct / total if total else 0.0
    return (
        "### Coach signal\n"
        f"**Overall:** {correct}/{total} correct ({acc:.0f}%).  \n"
        f"**Priority skills:** {', '.join(weakest)}.  \n"
        f"**Current strengths:** {', '.join(strongest)}.  \n"
        "The adaptive selector increases exposure to lower-rated and under-sampled skills while matching problem difficulty to the current mastery rating."
    )


def refresh_history(history: List[Dict[str, Any]]) -> str:
    return history_markdown(history)


def reset_profile():
    p = blank_profile()
    return p, [], mastery_markdown(p), recommendation_markdown(p), "No adaptive attempts yet.", "Profile reset."
