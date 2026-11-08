import sys
import json
import random
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 9,
    "title": "Анализ программ с ветвлением (Python)",
    "has_variants": False
}

# =============================================================================
# ГЕНЕРАТОР ЛОГИЧЕСКИХ УСЛОВИЙ
# =============================================================================

def build_condition(var1, var2):
    """
    Генерирует условие на языке Python и возвращает:
    (текст условия, лямбда-функцию вычисления от (v1, v2), флаг только неотрицательных чисел)
    """
    cond_type = random.choices(["simple_logic", "with_not", "arithmetic"], weights=[0.70, 0.15, 0.15], k=1)[0]

    if cond_type == "simple_logic":
        op1 = random.choice([">", "<", ">=", "<="])
        op2 = random.choice([">", "<", ">=", "<="])
        logic = random.choice(["and", "or"])
        c1 = random.randint(-3, 10)
        c2 = random.randint(-3, 10)

        cond_str = f"({var1} {op1} {c1}) {logic} ({var2} {op2} {c2})"

        def eval_fn(v1, v2):
            b1 = (v1 > c1) if op1 == ">" else (v1 < c1) if op1 == "<" else (v1 >= c1) if op1 == ">=" else (v1 <= c1)
            b2 = (v2 > c2) if op2 == ">" else (v2 < c2) if op2 == "<" else (v2 >= c2) if op2 == ">=" else (v2 <= c2)
            return (b1 and b2) if logic == "and" else (b1 or b2)

        return cond_str, eval_fn, False

    elif cond_type == "with_not":
        op1 = random.choice([">", "<"])
        op2 = random.choice([">", "<"])
        c1 = random.randint(-3, 8)
        c2 = random.randint(-3, 8)

        cond_str = f"({var1} {op1} {c1}) and not ({var2} {op2} {c2})"

        def eval_fn(v1, v2):
            b1 = (v1 > c1) if op1 == ">" else (v1 < c1)
            b2 = (v2 > c2) if op2 == ">" else (v2 < c2)
            return b1 and (not b2)

        return cond_str, eval_fn, False

    else: # arithmetic
        sub = random.choice(["div2", "mult2_ge", "mult2_le", "eq_const"])
        if sub == "div2":
            cond_str = f"{var1} // 2 == {var2}"
            # Для деления // используем строго неотрицательные числа, как в банке ФИОКО
            return cond_str, (lambda v1, v2: (v1 // 2 == v2)), True
        elif sub == "mult2_ge":
            cond_str = f"{var1} >= 2 * {var2}"
            return cond_str, (lambda v1, v2: (v1 >= 2 * v2)), False
        elif sub == "mult2_le":
            cond_str = f"{var1} <= 2 * {var2}"
            return cond_str, (lambda v1, v2: (v1 <= 2 * v2)), False
        else:
            c1 = random.randint(1, 6)
            c2 = random.randint(-3, 8)
            cond_str = f"({var1} == {c1}) or ({var2} < {c2})"
            return cond_str, (lambda v1, v2: (v1 == c1) or (v2 < c2)), False

# =============================================================================
# АРХЕТИП 1: ПОДСЧЁТ КОЛИЧЕСТВА ЗАПУСКОВ (60% — примеры 1–23)
# =============================================================================

def generate_count_runs():
    while True:
        var1, var2 = ("s", "t") if random.random() < 0.80 else ("s", "k")
        word_yes, word_no = ("YES", "NO") if random.random() < 0.70 else ("ДА", "НЕТ")

        cond_str, eval_fn, only_positive = build_condition(var1, var2)

        # Генерируем 9 уникальных тестовых пар
        pairs = []
        while len(pairs) < 9:
            if only_positive:
                v1 = random.randint(0, 20)
                v2 = random.randint(0, 12)
            else:
                v1 = random.randint(-11, 15)
                v2 = random.randint(-11, 15)

            if (v1, v2) not in pairs:
                pairs.append((v1, v2))

        results = [eval_fn(v1, v2) for v1, v2 in pairs]
        yes_count = results.count(True)
        no_count = results.count(False)

        # Отбираем невырожденные запуски (от 2 до 7 совпадений)
        if not (2 <= yes_count <= 7):
            continue

        ask_yes = random.choice([True, False])
        target_word = word_yes if ask_yes else word_no
        ans_count = yes_count if ask_yes else no_count

        pairs_str = "; ".join(f"({v1}, {v2})" for v1, v2 in pairs)

        code_text = (
            f"{var1} = int(input())\n"
            f"{var2} = int(input())\n"
            f"if {cond_str}:\n"
            f"    print(\"{word_yes}\")\n"
            f"else:\n"
            f"    print(\"{word_no}\")"
        )

        prompt = (
            f"Ниже приведена программа, записанная на языке Python:\n\n"
            f"{code_text}\n\n"
            f"Было проведено 9 запусков программы, при которых в качестве значений переменных {var1} и {var2} "
            f"вводились следующие пары чисел ({var1}, {var2}):\n"
            f"{pairs_str}.\n"
            f"Сколько было запусков, при которых программа напечатала «{target_word}»?"
        )

        return prompt, str(ans_count)

# =============================================================================
# АРХЕТИП 2: ВЫБОР ВСЕХ НОМЕРОВ ПАР ИЗ 5 (40% — примеры 24–37)
# =============================================================================

def generate_select_runs():
    while True:
        var1, var2 = ("s", "t") if random.random() < 0.85 else ("s", "k")
        word_yes, word_no = ("YES", "NO") if random.random() < 0.70 else ("ДА", "НЕТ")

        cond_str, eval_fn, only_positive = build_condition(var1, var2)

        # 5 уникальных пар чисел
        pairs = []
        while len(pairs) < 5:
            if only_positive:
                v1 = random.randint(0, 20)
                v2 = random.randint(0, 12)
            else:
                v1 = random.randint(-8, 15)
                v2 = random.randint(-8, 15)

            if (v1, v2) not in pairs:
                pairs.append((v1, v2))

        results = [eval_fn(v1, v2) for v1, v2 in pairs]
        ask_yes = random.choice([True, False])
        target_word = word_yes if ask_yes else word_no

        matching_indices = [i + 1 for i, res in enumerate(results) if (res if ask_yes else not res)]

        # Отбираем задачи, где подходит от 2 до 4 вариантов
        if len(matching_indices) not in [2, 3, 4]:
            continue

        answer_str = "".join(str(idx) for idx in sorted(matching_indices))

        pairs_formatted = "   ".join(f"{i + 1}) ({pairs[i][0]}, {pairs[i][1]})" for i in range(5))

        code_text = (
            f"{var1} = int(input())\n"
            f"{var2} = int(input())\n"
            f"if {cond_str}:\n"
            f"    print(\"{word_yes}\")\n"
            f"else:\n"
            f"    print(\"{word_no}\")"
        )

        prompt = (
            f"Ниже приведена программа, записанная на языке Python:\n\n"
            f"{code_text}\n\n"
            f"Было проведено 5 запусков программы, при которых в качестве значений переменных {var1} и {var2} "
            f"вводились следующие пары чисел ({var1}, {var2}):\n"
            f"{pairs_formatted}\n"
            f"Выберите ВСЕ пары чисел, для которых программа напечатает «{target_word}», "
            f"и запишите в ответе их номера в порядке возрастания (без пробелов)."
        )

        return prompt, answer_str

# =============================================================================
# ТОЧКА ВХОДА ГЕНЕРАТОРА
# =============================================================================

def generate():
    random.seed(os.urandom(16))

    archetype = random.choices(["count_9", "select_5"], weights=[0.60, 0.40], k=1)[0]

    if archetype == "count_9":
        prompt, answer = generate_count_runs()
    else:
        prompt, answer = generate_select_runs()

    return {
        "task": prompt,
        "variants": None,
        "variant_type": None,
        "answer": answer
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--meta":
            print(json.dumps(META, ensure_ascii=False))
        elif sys.argv[1] == "--generate":
            print(json.dumps(generate(), ensure_ascii=False))