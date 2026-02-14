import random

def generate_problem(difficulty="easy", mode="classic"):
    """
    Generates a math problem based on difficulty and variety.
    Returns: (problem_text, answer)
    """
    # Randomly choose problem type for innovation
    p_type = random.choices(["standard", "missing_op", "true_false"], weights=[0.7, 0.15, 0.15])[0]
    
    if p_type == "missing_op" and difficulty != "easy":
        return _generate_missing_op(difficulty)
    elif p_type == "true_false":
        return _generate_true_false(difficulty)
    
    return _generate_standard(difficulty)

def _generate_standard(difficulty):
    if difficulty == "easy":
        ops = ['+', '-']
        op = random.choice(ops)
        if op == '+':
            a, b = random.randint(1, 15), random.randint(1, 15)
            return f"{a} + {b}", a + b
        else:
            a = random.randint(5, 20)
            b = random.randint(1, a)
            return f"{a} - {b}", a - b

    elif difficulty == "medium":
        ops = ['*', '+', '-']
        op = random.choice(ops)
        if op == '*':
            a, b = random.randint(2, 12), random.randint(2, 12)
            return f"{a} * {b}", a * b
        elif op == '+':
            a, b = random.randint(15, 60), random.randint(15, 60)
            return f"{a} + {b}", a + b
        else:
            a = random.randint(40, 100)
            b = random.randint(10, a)
            return f"{a} - {b}", a - b

    else: # hard
        ops = ['/', '*', '+', '-']
        op = random.choice(ops)
        if op == '/':
            b = random.randint(2, 15)
            a = b * random.randint(2, 15)
            return f"{a} / {b}", a // b
        elif op == '*':
            a, b = random.randint(10, 25), random.randint(2, 20)
            return f"{a} * {b}", a * b
        else:
            a, b = random.randint(100, 500), random.randint(50, 400)
            if random.random() > 0.5: return f"{a} + {b}", a + b
            return f"{max(a,b)} - {min(a,b)}", abs(a - b)

def _generate_missing_op(difficulty):
    a, b = random.randint(2, 10), random.randint(2, 10)
    op = random.choice(['+', '-', '*'])
    if op == '+': res = a + b
    elif op == '-': res = a - b
    else: res = a * b
    
    # User needs to identify the operator? No, the original game expects int answer.
    # Let's make missing_op return a standard format but with a twist or just keep it for variety.
    # Actually, let's stick to numerical answers but maybe "solve for x": "5 + ? = 12"
    a, b = random.randint(1, 20), random.randint(1, 20)
    res = a + b
    return f"{a} + ? = {res}", b

def _generate_true_false(difficulty):
    # Answer 1 for True, 0 for False
    prob, ans = _generate_standard(difficulty)
    is_true = random.random() > 0.5
    if is_true:
        return f"{prob} = {ans} (1=T, 0=F)", 1
    else:
        fake_ans = ans + random.choice([-2, -1, 1, 2, 5, 10])
        return f"{prob} = {fake_ans} (1=T, 0=F)", 0
