import csv
import html
import json
import math
import re
import tempfile
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional

from mathforge_core import *
from mathforge_core import _rng
from mathforge_generators import generate_one


def weighted_topic_choice(profile: Dict[str, Any], r: random.Random, allowed: List[str]) -> str:
    p = ensure_profile(profile)
    weights = []
    for t in allowed:
        skill = p["skills"][t]
        rating = float(skill["rating"])
        attempts = int(skill["attempts"])
        weakness = max(0.15, (1300.0 - rating) / 350.0)
        exploration = 1.0 + 2.0 / math.sqrt(attempts + 1)
        weights.append(max(0.05, weakness * exploration))
    return r.choices(allowed, weights=weights, k=1)[0]


def difficulty_from_rating(rating: float) -> str:
    if rating < 875:
        return "Beginner"
    if rating < 1025:
        return "Easy"
    if rating < 1175:
        return "Medium"
    if rating < 1325:
        return "Hard"
    return "Expert"


def topic_plan(topic: str, count: int, strategy: str, profile: Dict[str, Any], r: random.Random) -> List[str]:
    if topic != "Mixed":
        return [topic] * count
    allowed = SKILL_TOPICS.copy()
    if strategy == "Balanced":
        plan = []
        while len(plan) < count:
            batch = allowed.copy()
            r.shuffle(batch)
            plan.extend(batch)
        return plan[:count]
    if strategy == "Mastery-aware":
        return [weighted_topic_choice(profile, r, allowed) for _ in range(count)]
    return [r.choice(allowed) for _ in range(count)]


def generate_problems(topic: str, difficulty: str, count: int, seed: Any, strategy: str, profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    r = _rng(seed)
    count = max(1, min(int(count), 100))
    plan = topic_plan(topic, count, strategy, profile, r)
    rows: List[Dict[str, Any]] = []
    seen = set()
    attempts = 0
    while len(rows) < count and attempts < count * 80:
        attempts += 1
        planned = plan[len(rows)] if len(rows) < len(plan) else topic
        p = generate_one(planned, difficulty, r)
        key = (p["topic"], p["question"])
        if key in seen:
            continue
        seen.add(key)
        rows.append(p)
    return rows


def worksheet_markdown(rows: List[Dict[str, Any]], topic: str, difficulty: str, include_hints: bool) -> str:
    lines = [f"# {APP_TITLE}", f"**Difficulty:** {difficulty}  ", f"**Mode:** {topic}  ", "", "## Questions", ""]
    for i, row in enumerate(rows, 1):
        lines.append(f"**{i}.** {row['question']}")
        lines.append(f"<sub>{row['topic']} · {row['concept']} · ID {row['id']}</sub>")
        if include_hints:
            lines.append(f"*Hint:* {row['hint']}")
        lines.append("")
    return "\n".join(lines)


def answer_markdown(rows: List[Dict[str, Any]]) -> str:
    lines = ["## Answer Key", ""]
    for i, row in enumerate(rows, 1):
        lines.append(f"**{i}.** `{row['answer']}` — *{row['topic']}*")
        lines.append(f"{row['solution']}")
        lines.append("")
    return "\n".join(lines)


def quality_report(rows: List[Dict[str, Any]]) -> str:
    if not rows:
        return "No questions generated."
    counts = Counter(row["topic"] for row in rows)
    unique = len({(r["topic"], r["question"]) for r in rows})
    types = Counter(row.get("answer_type", "scalar") for row in rows)
    lines = [
        "### Generation audit",
        f"- **Unique questions:** {unique}/{len(rows)}",
        f"- **Topic coverage:** {len(counts)} skill areas",
        f"- **Answer representations:** {', '.join(f'{k}={v}' for k, v in sorted(types.items()))}",
        "- **Determinism:** same settings + seed reproduce the same set",
        "- **Leakage protection:** answers are kept outside the worksheet view unless explicitly opened",
        "",
        "**Distribution:** " + " · ".join(f"{k} {v}" for k, v in counts.most_common()),
    ]
    return "\n".join(lines)


def generate_set(topic: str, difficulty: str, count: int, seed: Any, strategy: str, include_hints: bool, profile: Dict[str, Any]):
    rows = generate_problems(topic, difficulty, int(count), seed, strategy, profile)
    return worksheet_markdown(rows, topic, difficulty, include_hints), answer_markdown(rows), quality_report(rows), rows


def safe_filename_piece(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower() or "mathforge"


def export_bundle(topic: str, difficulty: str, rows: List[Dict[str, Any]], include_answers: bool, include_hints: bool) -> Optional[str]:
    if not rows:
        return None
    tmpdir = Path(tempfile.mkdtemp(prefix="mathforge_"))
    stem = f"mathforge-{safe_filename_piece(topic)}-{safe_filename_piece(difficulty)}"

    txt = [APP_TITLE, f"Version: {APP_VERSION}", f"Difficulty: {difficulty}", f"Mode: {topic}", "=" * 78, ""]
    for i, row in enumerate(rows, 1):
        txt.append(f"{i}. {row['question']}")
        if include_hints:
            txt.append(f"   Hint: {row['hint']}")
        txt.append("")
    if include_answers:
        txt += ["=" * 78, "ANSWER KEY", ""]
        for i, row in enumerate(rows, 1):
            txt += [f"{i}. {row['answer']} ({row['topic']})", f"   {row['solution']}", ""]
    (tmpdir / f"{stem}.txt").write_text("\n".join(txt), encoding="utf-8")

    with (tmpdir / f"{stem}.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["number", "id", "topic", "difficulty", "concept", "question", "answer", "hint", "solution"])
        writer.writeheader()
        for i, row in enumerate(rows, 1):
            writer.writerow({
                "number": i,
                "id": row["id"],
                "topic": row["topic"],
                "difficulty": row["difficulty"],
                "concept": row["concept"],
                "question": row["question"],
                "answer": row["answer"] if include_answers else "",
                "hint": row["hint"] if include_hints else "",
                "solution": row["solution"] if include_answers else "",
            })

    payload = {
        "app": APP_TITLE,
        "version": APP_VERSION,
        "topic": topic,
        "difficulty": difficulty,
        "questions": [
            {k: v for k, v in row.items() if include_answers or k not in {"answer", "solution"}}
            for row in rows
        ],
    }
    if not include_hints:
        for row in payload["questions"]:
            row.pop("hint", None)
    (tmpdir / f"{stem}.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    q_html = []
    for i, row in enumerate(rows, 1):
        q_html.append(f"<article class='q'><b>{i}.</b> {html.escape(row['question'])}<div class='meta'>{html.escape(row['topic'])} · {html.escape(row['concept'])}</div>")
        if include_hints:
            q_html.append(f"<div class='hint'>Hint: {html.escape(row['hint'])}</div>")
        q_html.append("<div class='work'></div></article>")
    a_html = ""
    if include_answers:
        blocks = "".join(f"<li><b>{i}.</b> {html.escape(row['answer'])}<br><span>{html.escape(row['solution'])}</span></li>" for i, row in enumerate(rows, 1))
        a_html = f"<section class='answers'><h2>Answer key</h2><ol>{blocks}</ol></section>"
    page = f"""<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(APP_TITLE)}</title><style>
    body{{font-family:Inter,Arial,sans-serif;max-width:900px;margin:40px auto;padding:0 24px;color:#111}}h1{{margin-bottom:4px}}.sub{{color:#555;margin-bottom:28px}}.q{{page-break-inside:avoid;margin:0 0 24px}}.meta{{font-size:11px;color:#777;margin-top:4px}}.hint{{font-size:13px;color:#555;margin-top:6px}}.work{{height:56px;border-bottom:1px solid #ddd}}.answers{{page-break-before:always}}li{{margin:12px 0}}li span{{color:#444}}@media print{{body{{margin:0;max-width:none}}}}
    </style></head><body><h1>{html.escape(APP_TITLE)}</h1><div class='sub'>{html.escape(topic)} · {html.escape(difficulty)} · {len(rows)} questions</div>{''.join(q_html)}{a_html}</body></html>"""
    (tmpdir / f"{stem}.html").write_text(page, encoding="utf-8")

    zip_path = tmpdir / f"{stem}-bundle.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for ext in ["txt", "csv", "json", "html"]:
            file = tmpdir / f"{stem}.{ext}"
            zf.write(file, file.name)
    return str(zip_path)
