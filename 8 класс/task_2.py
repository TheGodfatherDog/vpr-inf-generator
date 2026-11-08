import sys
import json
import random
import os
import itertools

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 2,
    "title": "Сравнение чисел в различных системах счисления",
    "has_variants": True
}

# =============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================================================

def to_repr(val, base):
    """Возвращает число с нижним индексом основания системы счисления."""
    if base == 2:
        return f"{bin(val)[2:]}₂"
    elif base == 8:
        return f"{oct(val)[2:]}₈"
    elif base == 16:
        return f"{hex(val)[2:].upper()}₁₆"
    elif base == 10:
        return f"{val}₁₀"
    return str(val)

def to_raw(val, base):
    """Возвращает строковое представление числа без индексов для вариантов."""
    if base == 2:
        return bin(val)[2:]
    elif base == 8:
        return oct(val)[2:]
    elif base == 16:
        return hex(val)[2:].upper()
    return str(val)

def base_name_dative(base):
    return {
        2: "двоичной",
        8: "восьмеричной",
        16: "шестнадцатеричной",
        10: "десятичной"
    }[base]

# =============================================================================
# АРХЕТИП 1: ПОИСК ЧИСЛА В ИНТЕРВАЛЕ НЕРАВЕНСТВА (55% — примеры 1, 2, 4, 14–31)
# =============================================================================

def generate_interval_choice():
    while True:
        v_min = random.randint(25, 260)
        gap = random.randint(2, 5)
        v_max = v_min + gap

        candidates_inside = list(range(v_min + 1, v_max))
        correct_val = random.choice(candidates_inside)

        base_left, base_right = random.sample([2, 8, 16, 10], 2)
        base_target = random.choices([2, 8, 16], weights=[0.75, 0.15, 0.10], k=1)[0]

        distractor_pool = [
            v_min,
            v_max,
            v_min - 1,
            v_max + 1,
            v_min - 2,
            v_max + 2
        ]
        distractor_pool = [d for d in distractor_pool if d > 0 and (d <= v_min or d >= v_max)]
        random.shuffle(distractor_pool)

        unique_distractors = []
        for d in distractor_pool:
            if d not in unique_distractors:
                unique_distractors.append(d)
            if len(unique_distractors) == 3:
                break

        if len(unique_distractors) < 3:
            continue

        raw_options = unique_distractors + [correct_val]
        options_strs = [to_raw(x, base_target) for x in raw_options]
        if len(set(options_strs)) != 4:
            continue

        random.shuffle(raw_options)
        correct_idx = raw_options.index(correct_val) + 1

        variants = [to_raw(x, base_target) for x in raw_options]

        left_str = to_repr(v_min, base_left)
        right_str = to_repr(v_max, base_right)
        target_name = base_name_dative(base_target)

        prompt = (
            f"Какое из чисел, записанных в {target_name} системе счисления, "
            f"удовлетворяет условию {left_str} < x < {right_str}?"
        )

        return prompt, variants, str(correct_idx)

# =============================================================================
# АРХЕТИП 2: УПОРЯДОЧИВАНИЕ ТРЁХ ЧИСЕЛ ПО ВОЗРАСТАНИЮ (20% — примеры 32–36)
# =============================================================================

def generate_sort_three():
    while True:
        base_val = random.randint(80, 300)
        offsets = random.sample([-18, -12, -7, -3, 3, 7, 12, 18], 3)
        vals = [base_val + offsets[0], base_val + offsets[1], base_val + offsets[2]]

        if len(set(vals)) != 3 or any(v <= 0 for v in vals):
            continue

        val_A, val_B, val_C = vals
        bases = [2, 8, 16]
        random.shuffle(bases)

        named = [('A', val_A), ('B', val_B), ('C', val_C)]
        named.sort(key=lambda item: item[1])
        correct_order = "".join([item[0] for item in named])

        all_perms = ["".join(p) for p in itertools.permutations(['A', 'B', 'C'])]
        distractors = [p for p in all_perms if p != correct_order]
        random.shuffle(distractors)

        chosen_options = distractors[:3] + [correct_order]
        random.shuffle(chosen_options)

        correct_idx = chosen_options.index(correct_order) + 1

        str_A = to_repr(val_A, bases[0])
        str_B = to_repr(val_B, bases[1])
        str_C = to_repr(val_C, bases[2])

        prompt = (
            f"Расположите числа в порядке возрастания:\n"
            f"A = {str_A},  B = {str_B},  C = {str_C}."
        )

        return prompt, chosen_options, str(correct_idx)

# =============================================================================
# АРХЕТИП 3: ВЫБОР НАИБОЛЬШЕГО ИЛИ НАИМЕНЬШЕГО ЧИСЛА (13% — примеры 10, 11)
# =============================================================================

def generate_min_max():
    while True:
        center = random.randint(70, 260)
        diffs = random.sample([-15, -9, -4, 4, 9, 15], 3)
        vals = [center + diffs[0], center + diffs[1], center + diffs[2]]

        if len(set(vals)) != 3 or any(v <= 0 for v in vals):
            continue

        bases = [2, 8, 16]
        random.shuffle(bases)

        nums_repr = [to_repr(vals[i], bases[i]) for i in range(3)]
        random.shuffle(nums_repr)

        is_max = random.choice([True, False])
        target_val = max(vals) if is_max else min(vals)
        kind_str = "наибольшее" if is_max else "наименьшее"

        # Формируем 4 варианта ответа в десятичной системе (3 числа + 1 правдоподобный дистрактор)
        distractor = center + random.choice([-20, -2, 2, 20])
        while distractor in vals or distractor <= 0:
            distractor += 1

        options_vals = vals + [distractor]
        options_vals = list(dict.fromkeys(options_vals))
        if len(options_vals) != 4:
            continue

        random.shuffle(options_vals)
        correct_idx = options_vals.index(target_val) + 1
        variants = [str(v) for v in options_vals]

        prompt = (
            f"Какое десятичное число является {kind_str} среди чисел: {nums_repr[0]}, {nums_repr[1]}, {nums_repr[2]}?\n"
            f"В ответе укажите номер правильного варианта."
        )

        return prompt, variants, str(correct_idx)

# =============================================================================
# АРХЕТИП 4: КОЛИЧЕСТВО ЦЕЛЫХ ЧИСЕЛ В ИНТЕРВАЛЕ (12% — примеры 7, 8, 9, 12, 13)
# =============================================================================

def generate_count_between():
    while True:
        v_min = random.randint(30, 260)
        if random.random() < 0.70:
            count = random.randint(1, 5)
        else:
            count = random.randint(10, 99)

        v_max = v_min + count + 1

        base_left, base_right = random.sample([2, 8, 16], 2)

        str_left = to_repr(v_min, base_left)
        str_right = to_repr(v_max, base_right)

        prompt = (
            f"Сколько существует целых чисел x, для которых выполняется неравенство "
            f"{str_left} < x < {str_right}?"
        )

        return prompt, None, str(count)

# =============================================================================
# ТОЧКА ВХОДА ГЕНЕРАТОРА
# =============================================================================

def generate():
    random.seed(os.urandom(16))

    archetype = random.choices(
        ["interval_choice", "sort_three", "min_max", "count_between"],
        weights=[0.55, 0.20, 0.13, 0.12],
        k=1
    )[0]

    if archetype == "interval_choice":
        prompt, variants, answer = generate_interval_choice()
    elif archetype == "sort_three":
        prompt, variants, answer = generate_sort_three()
    elif archetype == "min_max":
        prompt, variants, answer = generate_min_max()
    else:
        prompt, variants, answer = generate_count_between()

    return {
        "task": prompt,
        "variants": variants,
        "variant_type": "numbers" if variants else None,
        "answer": answer
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--meta":
            print(json.dumps(META, ensure_ascii=False))
        elif sys.argv[1] == "--generate":
            print(json.dumps(generate(), ensure_ascii=False))