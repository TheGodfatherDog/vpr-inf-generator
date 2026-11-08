import sys
import json
import random
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 7,
    "title": "Линейные алгоритмы для формальных исполнителей",
    "has_variants": False
}

# =============================================================================
# ПОИСК ВСЕХ РЕШЕНИЙ (ГАРАНТИЯ СТРОГО ЕДИНСТВЕННОГО ОТВЕТА)
# =============================================================================

def find_all_programs(start, target, f1, f2, max_len=5):
    """
    Находит ВСЕ программы длины <= max_len.
    Позволяет отобрать только задачи со строго единственным решением.
    """
    solutions = []
    queue = [(start, "")]

    while queue:
        curr, path = queue.pop(0)

        if curr == target and len(path) > 0:
            solutions.append(path)
            continue

        if len(path) >= max_len:
            continue

        for cmd_num, op in [("1", f1), ("2", f2)]:
            nxt = op(curr)
            if nxt is not None and isinstance(nxt, int) and 0 < nxt <= 2500:
                queue.append((nxt, path + cmd_num))

    return solutions

# =============================================================================
# АРХЕТИП 1: НАЙТИ НЕИЗВЕСТНЫЙ ПАРАМЕТР B (15% — примеры 1, 2, 3)
# =============================================================================

def generate_find_b():
    names = ["Альфа", "Гамма", "Омега"]
    name = random.choice(names)

    while True:
        d = random.randint(3, 6)
        b = random.randint(3, 14)
        prog_pattern = random.choice(["12111", "11211", "1211", "1121"])

        pre_div = b * random.randint(2, 8)
        c1_before = prog_pattern.index('2')
        start = pre_div - c1_before * d

        if start <= 0 or start == pre_div:
            continue

        curr = start
        valid = True
        for cmd in prog_pattern:
            if cmd == '1':
                curr += d
            else:
                if curr % b != 0:
                    valid = False
                    break
                curr //= b

        if not valid or curr <= 0 or curr == start:
            continue

        # Проверка строгой единственности параметра b >= 2
        solutions = []
        for test_b in range(2, 60):
            t_curr = start
            ok = True
            for cmd in prog_pattern:
                if cmd == '1':
                    t_curr += d
                else:
                    if t_curr % test_b != 0:
                        ok = False
                        break
                    t_curr //= test_b
            if ok and t_curr == curr:
                solutions.append(test_b)

        if len(solutions) == 1 and solutions[0] == b:
            prompt = (
                f"У исполнителя {name} две команды: 1. прибавь {d};  2. раздели на b (b — неизвестное натуральное число; b ≥ 2).\n"
                f"Первая из них увеличивает число на экране на {d}, вторая — делит его на b.\n"
                f"Программа {prog_pattern} переводит число {start} в число {curr}. Определите значение b."
            )
            return prompt, str(b)

# =============================================================================
# АРХЕТИП 2: УМНОЖЕНИЕ И СЛОЖЕНИЕ / ВЫЧИТАНИЕ (40% — примеры 7–16, 21–26)
# =============================================================================

def generate_mul_arithmetic():
    while True:
        m = random.choice([2, 3, 4, 5])
        is_sub = random.choice([True, False])
        a = random.choice([1, 2, 3]) if not is_sub else random.choice([1, 2])

        if m == 2:
            name = random.choice(["Удвоитель", "Калькулятор", "Вычислитель"])
        else:
            name = random.choice(["Калькулятор", "Вычислитель", "Аккорд"])

        m_word = "раза" if m in [2, 3, 4] else "раз"

        if is_sub:
            c1_text = f"умножь на {m}"
            c2_text = f"вычти {a}"
            op1 = lambda x, m=m: x * m
            op2 = lambda x, a=a: x - a
            desc1 = f"увеличивает число в {m} {m_word}"
            desc2 = f"уменьшает его на {a}"
        else:
            c1_text = f"умножь на {m}"
            c2_text = f"прибавь {a}"
            op1 = lambda x, m=m: x * m
            op2 = lambda x, a=a: x + a
            desc1 = f"увеличивает число в {m} {m_word}"
            desc2 = f"увеличивает его на {a}"

        swap = random.choice([True, False])
        if swap:
            cmd1, cmd2 = c2_text, c1_text
            f1, f2 = op2, op1
            d1, d2 = desc2, desc1
        else:
            cmd1, cmd2 = c1_text, c2_text
            f1, f2 = op1, op2
            d1, d2 = desc1, desc2

        start = random.randint(2, 7)
        curr = start
        for _ in range(random.choice([4, 5])):
            curr = f1(curr) if random.choice([True, False]) else f2(curr)

        if curr <= 0 or curr == start or curr > 350:
            continue

        target = curr
        # Гарантируем СТРОГО ЕДИНСТВЕННОЕ решение
        solutions = find_all_programs(start, target, f1, f2, max_len=5)

        if len(solutions) == 1 and len(solutions[0]) in [4, 5]:
            sol = solutions[0]
            prompt = (
                f"У исполнителя {name} две команды: 1. {cmd1};  2. {cmd2}.\n"
                f"Первая из них {d1}, вторая — {d2}.\n"
                f"Составьте алгоритм получения из числа {start} числа {target}, содержащий не более 5 команд. "
                "В ответе запишите только номера команд."
            )
            return prompt, sol

# =============================================================================
# АРХЕТИП 3: ДЕЛЕНИЕ И ВЫЧИТАНИЕ / СЛОЖЕНИЕ (30% — примеры 4, 5, 31–35)
# =============================================================================

def generate_div_arithmetic():
    while True:
        m = random.choice([2, 3])
        is_add = random.random() < 0.25
        a = random.choice([1, 2, 3, 5])

        if is_add:
            name = random.choice(["Вычислитель", "Калькулятор"])
            c1_text = f"раздели на {m}"
            c2_text = f"прибавь {a}"
            op1 = lambda x, m=m: (x // m) if (x % m == 0) else None
            op2 = lambda x, a=a: x + a
            desc1 = f"уменьшает число в {m} раза"
            desc2 = f"увеличивает его на {a}"
        else:
            name = random.choice(["Делитель", "Уменьшитель"])
            c1_text = f"раздели на {m}"
            c2_text = f"вычти {a}"
            op1 = lambda x, m=m: (x // m) if (x % m == 0) else None
            op2 = lambda x, a=a: x - a
            desc1 = f"уменьшает число в {m} раза"
            desc2 = f"уменьшает его на {a}"

        swap = random.choice([True, False])
        if swap:
            cmd1, cmd2 = c2_text, c1_text
            f1, f2 = op2, op1
            d1, d2 = desc2, desc1
        else:
            cmd1, cmd2 = c1_text, c2_text
            f1, f2 = op1, op2
            d1, d2 = desc1, desc2

        target = random.randint(2, 14)
        curr = target
        for _ in range(random.choice([4, 5])):
            curr = curr * m if random.choice([True, False]) else ((curr - a) if is_add else (curr + a))

        start = curr
        if start <= target or start > 200:
            continue

        # Гарантируем СТРОГО ЕДИНСТВЕННОЕ решение
        solutions = find_all_programs(start, target, f1, f2, max_len=5)

        if len(solutions) == 1 and len(solutions[0]) in [4, 5]:
            sol = solutions[0]
            prompt = (
                f"У исполнителя {name} две команды: 1. {cmd1};  2. {cmd2}.\n"
                f"Первая из них {d1}, вторая — {d2}. Исполнитель работает только с натуральными числами.\n"
                f"Составьте алгоритм получения из числа {start} числа {target}, содержащий не более 5 команд. "
                "В ответе запишите только номера команд."
            )
            return prompt, sol

# =============================================================================
# АРХЕТИП 4: КВАДРАТОР (15% — примеры 6, 27–30)
# =============================================================================

def generate_quadrator():
    while True:
        is_sub = random.choice([True, False])
        a = random.choice([1, 2])

        c1_text = "возведи в квадрат"
        c2_text = f"вычти {a}" if is_sub else f"прибавь {a}"

        op1 = lambda x: x * x
        op2 = lambda x, a=a, is_sub=is_sub: (x - a) if is_sub else (x + a)

        desc1 = "возводит число во вторую степень"
        desc2 = f"уменьшает его на {a}" if is_sub else f"увеличивает его на {a}"

        swap = random.choice([True, False])
        if swap:
            cmd1, cmd2 = c2_text, c1_text
            f1, f2 = op2, op1
            d1, d2 = desc2, desc1
        else:
            cmd1, cmd2 = c1_text, c2_text
            f1, f2 = op1, op2
            d1, d2 = desc1, desc2

        start = random.randint(2, 4)
        curr = start
        sq_count = 0
        for _ in range(random.choice([4, 5])):
            if sq_count < 2 and curr <= 15 and random.random() < 0.45:
                curr = curr * curr
                sq_count += 1
            else:
                curr = (curr - a) if is_sub else (curr + a)

        target = curr
        if target <= 0 or target == start or target > 300 or sq_count == 0:
            continue

        # Гарантируем СТРОГО ЕДИНСТВЕННОЕ решение
        solutions = find_all_programs(start, target, f1, f2, max_len=5)

        if len(solutions) == 1 and len(solutions[0]) in [4, 5]:
            sol = solutions[0]
            prompt = (
                f"У исполнителя Квадратор две команды: 1. {cmd1};  2. {cmd2}.\n"
                f"Первая из них {d1}, вторая — {d2}.\n"
                f"Составьте алгоритм получения из числа {start} числа {target}, содержащий не более 5 команд. "
                "В ответе запишите только номера команд."
            )
            return prompt, sol

# =============================================================================
# ТОЧКА ВХОДА ГЕНЕРАТОРА
# =============================================================================

def generate():
    random.seed(os.urandom(16))

    archetype = random.choices(
        ["mul", "div", "quad", "find_b"],
        weights=[0.40, 0.30, 0.15, 0.15],
        k=1
    )[0]

    if archetype == "mul":
        prompt, answer = generate_mul_arithmetic()
    elif archetype == "div":
        prompt, answer = generate_div_arithmetic()
    elif archetype == "quad":
        prompt, answer = generate_quadrator()
    else:
        prompt, answer = generate_find_b()

    return {
        "task": prompt,
        "variants": None,
        "answer": answer
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--meta":
            print(json.dumps(META, ensure_ascii=False))
        elif sys.argv[1] == "--generate":
            print(json.dumps(generate(), ensure_ascii=False))