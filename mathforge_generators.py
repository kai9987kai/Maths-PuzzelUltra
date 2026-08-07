from fractions import Fraction
import math
import random

from mathforge_core import *


def arithmetic_problem(topic: str, diff: str, r: random.Random) -> Dict[str, Any]:
    cfg = DIFFICULTY[diff]
    lo, hi = cfg["min"], cfg["max"]
    if topic == "Addition":
        a, b = r.randint(lo, hi), r.randint(lo, hi)
        return make_problem(topic, f"{a} + {b}", str(a + b), "Add the two values.", f"{a} + {b} = {a + b}", "integer addition", diff)
    if topic == "Subtraction":
        a, b = r.randint(lo, hi), r.randint(lo, hi)
        if diff in ("Beginner", "Easy") and b > a:
            a, b = b, a
        return make_problem(topic, f"{a} − {b}", str(a - b), "Subtract the second value from the first.", f"{a} − {b} = {a - b}", "integer subtraction", diff)
    if topic == "Multiplication":
        cap = max(5, int(math.sqrt(abs(hi))) + cfg["coeff"] // 3)
        a = r.randint(1 if diff in ("Beginner", "Easy") else -cap, cap)
        b = r.randint(1, cap)
        return make_problem(topic, f"{a} × {b}", str(a * b), "Multiply the factors.", f"{a} × {b} = {a * b}", "integer multiplication", diff)
    cap = max(6, cfg["coeff"])
    divisor = r.randint(1, cap)
    quotient = r.randint(1 if diff in ("Beginner", "Easy") else -cap, cap)
    dividend = divisor * quotient
    return make_problem(topic, f"{dividend} ÷ {divisor}", str(quotient), "Ask: how many groups of the divisor fit into the dividend?", f"{dividend} ÷ {divisor} = {quotient}", "exact integer division", diff)


def fraction_problem(diff: str, r: random.Random) -> Dict[str, Any]:
    max_den = {"Beginner": 8, "Easy": 12, "Medium": 16, "Hard": 24, "Expert": 40}[diff]
    d1, d2 = r.randint(2, max_den), r.randint(2, max_den)
    n1, n2 = r.randint(1, d1 - 1), r.randint(1, d2 - 1)
    f1, f2 = Fraction(n1, d1), Fraction(n2, d2)
    ops = ["+", "−"] if diff == "Beginner" else ["+", "−", "×", "÷"]
    op = r.choice(ops)
    if op == "+":
        ans = f1 + f2
        step = "Use a common denominator, add the numerators, then simplify."
    elif op == "−":
        if diff in ("Beginner", "Easy") and f2 > f1:
            f1, f2 = f2, f1
        ans = f1 - f2
        step = "Use a common denominator, subtract the numerators, then simplify."
    elif op == "×":
        ans = f1 * f2
        step = "Multiply numerators and denominators, then simplify."
    else:
        ans = f1 / f2
        step = "Multiply by the reciprocal of the second fraction, then simplify."
    a, b = fraction_text(f1), fraction_text(f2)
    answer = fraction_text(ans)
    solution = f"{step} Result: {a} {op} {b} = {answer}."
    return make_problem("Fractions", f"{a} {op} {b}", answer, step, solution, "fraction arithmetic", diff, "scalar")


def percentage_problem(diff: str, r: random.Random) -> Dict[str, Any]:
    level = DIFFICULTY[diff]["level"]
    if level <= 2:
        pct = r.choice([5, 10, 20, 25, 50, 75])
        base = r.choice([20, 40, 50, 80, 100, 120, 200, 400])
        ans = base * pct / 100
        return make_problem("Percentages", f"What is {pct}% of {base}?", fmt_num(ans), f"Convert {pct}% to {pct/100:g} and multiply.", f"{pct}/100 × {base} = {fmt_num(ans)}.", "percentage of an amount", diff)
    if level == 3:
        original = r.randint(20, 300)
        pct = r.choice([10, 15, 20, 25, 30, 40])
        increase = r.choice([True, False])
        ans = original * (1 + pct / 100 if increase else 1 - pct / 100)
        verb = "increased" if increase else "decreased"
        return make_problem("Percentages", f"{original} is {verb} by {pct}%. What is the new value?", fmt_num(ans), "Find the percentage change, then add or subtract it.", f"Change = {original} × {pct/100:g} = {fmt_num(original*pct/100)}. New value = {fmt_num(ans)}.", "percentage change", diff)
    pct = r.choice([10, 20, 25, 40, 50]) if level == 4 else r.choice([5, 12.5, 15, 20, 25, 30, 40])
    original = r.choice([40, 80, 100, 120, 160, 200, 240, 320, 400])
    increase = r.choice([True, False])
    final = original * (1 + pct / 100 if increase else 1 - pct / 100)
    wording = "after an increase" if increase else "after a decrease"
    factor = 1 + pct/100 if increase else 1 - pct/100
    return make_problem("Percentages", f"A value is {fmt_num(final)} {wording} of {pct}%. What was the original value?", str(original), f"Reverse the percentage by dividing by the multiplier {fmt_num(factor)}.", f"Original = {fmt_num(final)} ÷ {fmt_num(factor)} = {original}.", "reverse percentages", diff)


def power_root_problem(diff: str, r: random.Random) -> Dict[str, Any]:
    level = DIFFICULTY[diff]["level"]
    if level >= 4 and r.random() < 0.25:
        base = r.randint(2, 8)
        exp = r.randint(1, 3)
        ans = Fraction(1, base ** exp)
        return make_problem("Powers & Roots", f"{base}^−{exp}", fraction_text(ans), "A negative exponent means take the reciprocal.", f"{base}^−{exp} = 1/{base}^{exp} = {fraction_text(ans)}.", "negative exponents", diff)
    if level >= 3 and r.random() < 0.3:
        root = r.randint(2, 12 + level * 2)
        cube = root ** 3
        return make_problem("Powers & Roots", f"∛{cube}", str(root), "Find the number that multiplies by itself three times to make the radicand.", f"{root}³ = {cube}, so ∛{cube} = {root}.", "cube roots", diff)
    if r.random() < 0.5:
        max_base = {"Beginner": 8, "Easy": 12, "Medium": 15, "Hard": 20, "Expert": 30}[diff]
        max_exp = {"Beginner": 2, "Easy": 3, "Medium": 4, "Hard": 5, "Expert": 6}[diff]
        base, exp = r.randint(2, max_base), r.randint(2, max_exp)
        ans = base ** exp
        return make_problem("Powers & Roots", f"{base}^{exp}", str(ans), f"Multiply {base} by itself {exp} times.", f"{base}^{exp} = {ans}.", "integer exponents", diff)
    root = r.randint(2, {"Beginner": 10, "Easy": 15, "Medium": 25, "Hard": 40, "Expert": 75}[diff])
    square = root * root
    return make_problem("Powers & Roots", f"√{square}", str(root), "Find the positive number whose square is the radicand.", f"{root}² = {square}, so √{square} = {root}.", "square roots", diff)


def order_operations_problem(diff: str, r: random.Random) -> Dict[str, Any]:
    level = DIFFICULTY[diff]["level"]
    a, b, c = r.randint(2, 5 + level * 3), r.randint(2, 6 + level * 2), r.randint(2, 7 + level * 2)
    if level <= 2:
        ans = a + b * c
        q = f"{a} + {b} × {c}"
        sol = f"Multiply first: {b} × {c} = {b*c}. Then add {a}: {a} + {b*c} = {ans}."
    elif level == 3:
        d = r.randint(2, 8)
        ans = (a + b) * c - d
        q = f"({a} + {b}) × {c} − {d}"
        sol = f"Parentheses: {a}+{b}={a+b}. Multiply: {a+b}×{c}={(a+b)*c}. Subtract {d}: {ans}."
    else:
        d = r.randint(2, 9)
        e = r.randint(2, 4)
        ans = a + b * (c - d) ** e
        q = f"{a} + {b} × ({c} − {d})^{e}"
        sol = f"Parentheses: {c}−{d}={c-d}. Power: ({c-d})^{e}={(c-d)**e}. Multiply by {b}: {b*((c-d)**e)}. Add {a}: {ans}."
    return make_problem("Order of Operations", q, str(ans), "Use brackets, powers, multiplication/division, then addition/subtraction.", sol, "order of operations", diff)


def ratio_problem(diff: str, r: random.Random) -> Dict[str, Any]:
    level = DIFFICULTY[diff]["level"]
    if level <= 2 or r.random() < 0.45:
        g = r.randint(2, 4 + level)
        a, b = r.randint(1, 9), r.randint(1, 9)
        while math.gcd(a, b) != 1:
            a, b = r.randint(1, 9), r.randint(1, 9)
        A, B = a * g, b * g
        return make_problem("Ratios & Proportions", f"Simplify the ratio {A}:{B}", f"{a}:{b}", "Divide both parts by their greatest common factor.", f"gcd({A}, {B}) = {g}. Dividing both by {g} gives {a}:{b}.", "simplifying ratios", diff, "ratio")
    a, b = r.randint(2, 12 + level), r.randint(2, 12 + level)
    k = r.randint(2, 9 + level)
    c = a * k
    d = b * k
    if r.random() < 0.5:
        q = f"{a}:{b} = {c}:x. Find x."
        ans = d
        sol = f"The scale factor is {c} ÷ {a} = {k}. Therefore x = {b} × {k} = {d}."
    else:
        q = f"{a}:{b} = x:{d}. Find x."
        ans = c
        sol = f"The scale factor is {d} ÷ {b} = {k}. Therefore x = {a} × {k} = {c}."
    return make_problem("Ratios & Proportions", q, str(ans), "Find the scale factor linking corresponding parts.", sol, "direct proportion", diff)


def averages_problem(diff: str, r: random.Random) -> Dict[str, Any]:
    level = DIFFICULTY[diff]["level"]
    n = min(3 + level, 7)
    values = [r.randint(2, 15 + 10 * level) for _ in range(n - 1)]
    target_mean = r.randint(4, 12 + 8 * level)
    last = target_mean * n - sum(values)
    if last < 0 or last > 100 + 20 * level:
        values = [r.randint(2, 10 + 4 * level) for _ in range(n)]
        mean = sum(values) / n
        return make_problem("Averages", f"Find the mean of: {', '.join(map(str, values))}", fmt_num(mean), "Add all values, then divide by how many values there are.", f"Sum = {sum(values)}. There are {n} values. Mean = {sum(values)} ÷ {n} = {fmt_num(mean)}.", "arithmetic mean", diff)
    values.append(last)
    r.shuffle(values)
    return make_problem("Averages", f"Find the mean of: {', '.join(map(str, values))}", str(target_mean), "Add all values, then divide by how many values there are.", f"Sum = {sum(values)}. There are {n} values. Mean = {sum(values)} ÷ {n} = {target_mean}.", "arithmetic mean", diff)


def scientific_problem(diff: str, r: random.Random) -> Dict[str, Any]:
    level = DIFFICULTY[diff]["level"]
    sig = r.randint(11, 99 if level <= 2 else 999)
    decimals = 1 if sig < 100 else 2
    coeff = sig / (10 ** decimals)
    exp = r.randint(2, 4 + level)
    if level >= 3 and r.random() < 0.35:
        exp = -exp
    value = coeff * (10 ** exp)
    answer = f"{fmt_num(coeff)}e{exp}"
    if exp >= 0:
        shown = fmt_num(value)
    else:
        shown = f"{value:.{abs(exp)+decimals+2}f}".rstrip("0")
    return make_problem("Scientific Notation", f"Write {shown} in scientific notation.", answer, "Move the decimal point so the coefficient is at least 1 but less than 10; count the places moved.", f"{shown} = {fmt_num(coeff)} × 10^{exp}.", "scientific notation", diff, "scientific", {"requires_scientific_format": True})


def sequence_problem(diff: str, r: random.Random) -> Dict[str, Any]:
    level = DIFFICULTY[diff]["level"]
    if level <= 2 or r.random() < 0.6:
        d = r.randint(2, 5 + 2 * level) * (-1 if level >= 3 and r.random() < 0.25 else 1)
        start = r.randint(1, 20 + 5 * level)
        seq = [start + i * d for i in range(5)]
        ans = seq[-1] + d
        return make_problem("Sequences", f"Find the next term: {', '.join(map(str, seq))}, …", str(ans), "Look for the constant difference between consecutive terms.", f"Each term changes by {d}. Therefore the next term is {seq[-1]} + ({d}) = {ans}.", "arithmetic sequences", diff)
    ratio = r.choice([2, 3, -2] if level >= 4 else [2, 3])
    start = r.randint(1, 5 + level)
    seq = [start * (ratio ** i) for i in range(4)]
    ans = seq[-1] * ratio
    return make_problem("Sequences", f"Find the next term: {', '.join(map(str, seq))}, …", str(ans), "Look for a constant multiplier between consecutive terms.", f"Each term is multiplied by {ratio}. Therefore the next term is {seq[-1]} × {ratio} = {ans}.", "geometric sequences", diff)


def absolute_problem(diff: str, r: random.Random) -> Dict[str, Any]:
    level = DIFFICULTY[diff]["level"]
    if level <= 2 or r.random() < 0.45:
        a = r.randint(-30 * level, 30 * level)
        b = r.randint(-10 * level, 10 * level)
        ans = abs(a) + b
        return make_problem("Absolute Values", f"|{a}| + ({b})", str(ans), "Evaluate the absolute value first; it is the distance from zero.", f"|{a}| = {abs(a)}. Then {abs(a)} + ({b}) = {ans}.", "absolute value evaluation", diff)
    center = r.randint(-10 * level, 10 * level)
    distance = r.randint(1, 5 + level * 2)
    roots = sorted([center - distance, center + distance])
    sign = "+" if center < 0 else "−"
    inner = f"x {sign} {abs(center)}" if center != 0 else "x"
    return make_problem("Absolute Values", f"Solve: |{inner}| = {distance}", f"{roots[0]}, {roots[1]}", "An absolute-value equation |u| = k has two cases: u = k and u = −k.", f"{inner} = {distance} or {inner} = −{distance}. Therefore x = {roots[1]} or x = {roots[0]}.", "absolute value equations", diff, "set")


def number_theory_problem(diff: str, r: random.Random) -> Dict[str, Any]:
    level = DIFFICULTY[diff]["level"]
    a, b = r.randint(4, 20 + level * 15), r.randint(4, 20 + level * 15)
    if r.random() < 0.5:
        g = math.gcd(a, b)
        return make_problem("Number Theory", f"Find gcd({a}, {b}).", str(g), "List common factors or use the Euclidean algorithm.", f"The greatest common divisor of {a} and {b} is {g}.", "greatest common divisor", diff)
    l = abs(a * b) // math.gcd(a, b)
    return make_problem("Number Theory", f"Find lcm({a}, {b}).", str(l), "Use lcm(a,b) = |ab| / gcd(a,b).", f"gcd({a},{b}) = {math.gcd(a,b)}. So lcm = {a}×{b}/{math.gcd(a,b)} = {l}.", "least common multiple", diff)


def probability_problem(diff: str, r: random.Random) -> Dict[str, Any]:
    level = DIFFICULTY[diff]["level"]
    red = r.randint(1, 3 + level)
    blue = r.randint(1, 3 + level)
    green = r.randint(1, 2 + level)
    total = red + blue + green
    target, count = r.choice([("red", red), ("blue", blue), ("green", green)])
    ans = Fraction(count, total)
    if level >= 4 and r.random() < 0.4 and total > 2:
        ans = Fraction(total - count, total)
        q = f"A bag contains {red} red, {blue} blue and {green} green counters. One is chosen at random. What is P(not {target})?"
        sol = f"Non-{target} outcomes = {total-count}; total outcomes = {total}. Probability = {fraction_text(ans)}."
        concept = "complementary probability"
    else:
        q = f"A bag contains {red} red, {blue} blue and {green} green counters. One is chosen at random. What is P({target})?"
        sol = f"Favourable outcomes = {count}; total outcomes = {total}. Probability = {count}/{total} = {fraction_text(ans)}."
        concept = "simple probability"
    return make_problem("Probability", q, fraction_text(ans), "Probability = favourable outcomes ÷ total outcomes.", sol, concept, diff)


def linear_problem(diff: str, r: random.Random) -> Dict[str, Any]:
    level = DIFFICULTY[diff]["level"]
    cap = DIFFICULTY[diff]["coeff"]
    x = r.randint(1 if level <= 2 else -cap, cap)
    if level <= 3:
        a = 1 if level == 1 else r.randint(1, cap)
        b = r.randint(0 if level <= 2 else -cap, cap)
        c = a * x + b
        if a == 1:
            expr = f"x + {b} = {c}" if b >= 0 else f"x − {abs(b)} = {c}"
        else:
            expr = f"{a}x + {b} = {c}" if b >= 0 else f"{a}x − {abs(b)} = {c}"
        sol = f"Subtract {b} from both sides to get {a}x = {a*x}. Divide by {a}: x = {x}." if b != 0 else f"Divide both sides by {a}: x = {x}."
    else:
        a = r.randint(2, cap)
        d = r.randint(1, cap - 1 if cap > 2 else 1)
        if a == d:
            a += 1
        b = r.randint(-cap, cap)
        e = (a - d) * x + b
        left = f"{a}x {'+' if b >= 0 else '−'} {abs(b)}"
        right = f"{d}x {'+' if e >= 0 else '−'} {abs(e)}"
        expr = f"{left} = {right}"
        sol = f"Move x-terms together: ({a}−{d})x = {e-b}. Thus {a-d}x = {(a-d)*x}, so x = {x}."
    return make_problem("Linear Equations", f"Solve for x: {expr}", str(x), "Keep the equation balanced; collect x-terms and constants on opposite sides.", sol, "linear equations", diff)


def systems_problem(diff: str, r: random.Random) -> Dict[str, Any]:
    level = DIFFICULTY[diff]["level"]
    cap = 4 + level * 2
    x, y = r.randint(-cap, cap), r.randint(-cap, cap)
    if level <= 2:
        a, b, c, d = 1, 1, 1, -1
    else:
        for _ in range(100):
            a, b, c, d = [r.randint(1, 2 + level) * r.choice([-1, 1]) for _ in range(4)]
            if a * d - b * c != 0:
                break
    e, f = a * x + b * y, c * x + d * y
    eq1 = f"{a}x {'+' if b >= 0 else '−'} {abs(b)}y = {e}"
    eq2 = f"{c}x {'+' if d >= 0 else '−'} {abs(d)}y = {f}"
    ans = f"{x}, {y}"
    sol = f"Eliminate one variable from the two equations, solve for the other, then substitute back. The solution is x = {x}, y = {y}."
    return make_problem("Systems of Equations", f"Solve the system for (x, y):\n\n{eq1}\n\n{eq2}", ans, "Use elimination or substitution.", sol, "simultaneous linear equations", diff, "pair")


def quadratic_problem(diff: str, r: random.Random) -> Dict[str, Any]:
    level = DIFFICULTY[diff]["level"]
    cap = {"Beginner": 5, "Easy": 7, "Medium": 10, "Hard": 14, "Expert": 20}[diff]
    p = r.randint(1 if level <= 2 else -cap, cap)
    q = r.randint(1 if level <= 2 else -cap, cap)
    p = p or 1
    q = q or -1
    b, c = -(p + q), p * q
    mid = f" + {b}x" if b >= 0 else f" − {abs(b)}x"
    end = f" + {c}" if c >= 0 else f" − {abs(c)}"
    roots = sorted([p, q])
    answer = str(roots[0]) if roots[0] == roots[1] else f"{roots[0]}, {roots[1]}"
    sol = f"Factor as (x − {p})(x − {q}) = 0. Therefore x = {p} or x = {q}."
    return make_problem("Quadratics", f"Solve: x²{mid}{end} = 0", answer, "Find two numbers whose product is the constant term and whose sum matches the x coefficient.", sol, "factorable quadratics", diff, "set")


def generate_one(topic: str, diff: str, r: random.Random) -> Dict[str, Any]:
    if topic == "Mixed":
        pool = SKILL_TOPICS.copy()
        if diff == "Beginner":
            pool = [t for t in pool if t not in {"Systems of Equations", "Quadratics", "Scientific Notation"}]
        topic = r.choice(pool)
    if topic in {"Addition", "Subtraction", "Multiplication", "Division"}:
        return arithmetic_problem(topic, diff, r)
    dispatch = {
        "Fractions": fraction_problem,
        "Percentages": percentage_problem,
        "Powers & Roots": power_root_problem,
        "Order of Operations": order_operations_problem,
        "Ratios & Proportions": ratio_problem,
        "Averages": averages_problem,
        "Scientific Notation": scientific_problem,
        "Sequences": sequence_problem,
        "Absolute Values": absolute_problem,
        "Number Theory": number_theory_problem,
        "Probability": probability_problem,
        "Linear Equations": linear_problem,
        "Systems of Equations": systems_problem,
        "Quadratics": quadratic_problem,
    }
    if topic not in dispatch:
        raise ValueError(f"Unsupported topic: {topic}")
    return dispatch[topic](diff, r)
