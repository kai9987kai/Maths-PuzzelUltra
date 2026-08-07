import math
import re
from fractions import Fraction
from typing import Any, Dict, List, Optional, Tuple

from mathforge_core import *


def normalize_math(text: str) -> str:
    return (
        (text or "")
        .strip()
        .lower()
        .replace("−", "-")
        .replace("–", "-")
        .replace("×", "x")
        .replace("·", "x")
        .replace("÷", "/")
        .replace("⁻", "-")
        .replace(" ", "")
    )


def parse_scalar(text: str) -> Optional[float]:
    s = normalize_math(text)
    s = re.sub(r"^(x|y)=", "", s)
    if not s:
        return None
    mixed = re.fullmatch(r"(-?\d+)\+([0-9]+)/([1-9][0-9]*)", s)
    if mixed:
        whole, num, den = map(int, mixed.groups())
        sign = -1 if whole < 0 else 1
        return whole + sign * num / den
    sci = re.fullmatch(r"([+-]?(?:\d+(?:\.\d*)?|\.\d+))(?:x|\*)10\^?([+-]?\d+)", s)
    if sci:
        return float(sci.group(1)) * (10 ** int(sci.group(2)))
    if re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)e[+-]?\d+", s):
        try:
            return float(s)
        except ValueError:
            return None
    if re.fullmatch(r"[+-]?\d+/[+-]?\d+", s):
        try:
            return float(Fraction(s))
        except Exception:
            return None
    if re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", s):
        try:
            return float(s)
        except ValueError:
            return None
    return None


def parse_collection(text: str) -> Optional[List[float]]:
    s = normalize_math(text).replace("(", "").replace(")", "")
    s = re.sub(r"[xy]=", "", s)
    parts = [p for p in re.split(r"[,;]", s) if p != ""]
    if not parts:
        return None
    vals = [parse_scalar(p) for p in parts]
    if any(v is None for v in vals):
        return None
    return [float(v) for v in vals if v is not None]


def equivalent(user: str, problem: Dict[str, Any]) -> bool:
    expected = str(problem.get("answer", ""))
    answer_type = problem.get("answer_type", "scalar")
    u_norm, e_norm = normalize_math(user), normalize_math(expected)
    if not u_norm:
        return False
    if answer_type == "ratio":
        def ratio_pair(s: str) -> Optional[Tuple[int, int]]:
            m = re.fullmatch(r"([+-]?\d+):([+-]?\d+)", s)
            return (int(m.group(1)), int(m.group(2))) if m else None
        up, ep = ratio_pair(u_norm), ratio_pair(e_norm)
        if up and ep:
            return up[1] != 0 and ep[1] != 0 and up[0] * ep[1] == ep[0] * up[1]
        return False
    if answer_type == "scientific":
        if problem.get("metadata", {}).get("requires_scientific_format"):
            has_format = bool(re.search(r"e[+-]?\d+", u_norm) or re.search(r"(?:x|\*)10\^?[+-]?\d+", u_norm))
            if not has_format:
                return False
        uv, ev = parse_scalar(user), parse_scalar(expected)
        return uv is not None and ev is not None and math.isclose(uv, ev, rel_tol=1e-9, abs_tol=1e-12)
    if answer_type in {"set", "pair"}:
        uv, ev = parse_collection(user), parse_collection(expected)
        if uv is None or ev is None or len(uv) != len(ev):
            return False
        if answer_type == "set":
            uv, ev = sorted(uv), sorted(ev)
        return all(math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9) for a, b in zip(uv, ev))
    if u_norm == e_norm:
        return True
    uv, ev = parse_scalar(user), parse_scalar(expected)
    return uv is not None and ev is not None and math.isclose(uv, ev, rel_tol=1e-9, abs_tol=1e-9)


def diagnose_mistake(user: str, problem: Dict[str, Any]) -> str:
    if not (user or "").strip():
        return "No answer was entered."
    answer_type = problem.get("answer_type")
    expected = problem.get("answer", "")
    if answer_type in {"set", "pair"}:
        uv, ev = parse_collection(user), parse_collection(expected)
        if uv is not None and ev is not None:
            if len(uv) < len(ev):
                return "Your response appears to be missing one required value."
            if answer_type == "pair" and sorted(uv) == sorted(ev) and uv != ev:
                return "The two values appear to be reversed; the ordered pair must be (x, y)."
    if answer_type == "scientific" and parse_scalar(user) is not None:
        if not re.search(r"e|10", normalize_math(user)):
            return "The numerical value is right only if it is also written in scientific notation; use a × 10^n form."
    u, e = parse_scalar(user), parse_scalar(str(expected))
    if u is not None and e is not None:
        if math.isclose(u, -e, rel_tol=1e-9, abs_tol=1e-9):
            return "This looks like a sign error: the magnitude is correct but the sign is reversed."
        if e != 0 and math.isclose(u, 1 / e, rel_tol=1e-9, abs_tol=1e-9):
            return "This looks like a reciprocal error. Check which quantity should be inverted."
        if math.isclose(u * 100, e, rel_tol=1e-9, abs_tol=1e-9) or math.isclose(u / 100, e, rel_tol=1e-9, abs_tol=1e-9):
            return "This looks like a factor-of-100 error, often caused by percentage conversion."
        if e != 0 and abs(u - e) / max(1.0, abs(e)) < 0.05:
            return "You are numerically close; re-check the final arithmetic or rounding step."
    return f"Re-check the core method for **{problem.get('concept', problem.get('topic', 'this topic'))}**."
