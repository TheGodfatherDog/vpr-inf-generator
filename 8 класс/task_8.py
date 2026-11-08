import sys
import json
import random
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 8,
    "title": "Исполнитель Чертёжник (циклы и перемещения на плоскости)",
    "has_variants": True
}

# =============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================================================

INSTRUCTION = (
    "Исполнитель Чертёжник перемещается на координатной плоскости, выполняя команду "
    "Сместиться на (a, b), которая перемещает его из точки (x, y) в точку (x + a, y + b). "
    "Запись «Повтори k раз Команда1 Команда2 Конец» означает повторение команд k раз."
)

def format_cmd(x, y):
    return f"Сместиться на ({x}, {y})"

def generate_distractors_cmd(correct_x, correct_y):
    """Генерирует 3 уникальных правдоподобных дистрактора для команды смещения."""
    candidates = [
        (-correct_x, -correct_y),
        (-correct_x, correct_y),
        (correct_x, -correct_y),
        (correct_y, correct_x),
        (-correct_y, -correct_x),
        (correct_x * 2, correct_y * 2),
        (-correct_y, correct_x)
    ]
    unique = []
    for cx, cy in candidates:
        if (cx, cy) != (correct_x, correct_y) and (cx, cy) not in unique:
            unique.append((cx, cy))
        if len(unique) == 3:
            break

    offset = 1
    while len(unique) < 3:
        cand = (correct_x + offset, correct_y - offset)
        if cand != (correct_x, correct_y) and cand not in unique:
            unique.append(cand)
        offset += 1

    return [format_cmd(cx, cy) for cx, cy in unique]

def generate_distractors_point(correct_x, correct_y):
    """Генерирует 3 уникальных правдоподобных дистрактора для координат точки (включая (0,0))."""
    candidates = [
        (-correct_x, -correct_y),
        (-correct_x, correct_y),
        (correct_x, -correct_y),
        (correct_y, correct_x),
        (-correct_y, -correct_x),
        (correct_x + 1, correct_y - 1),
        (correct_x - 1, correct_y + 1),
        (correct_x + 2, correct_y + 2),
        (-correct_x + 1, -correct_y - 1)
    ]
    unique = []
    for cx, cy in candidates:
        if (cx, cy) != (correct_x, correct_y) and (cx, cy) not in unique:
            unique.append((cx, cy))
        if len(unique) == 3:
            break

    offset = 1
    while len(unique) < 3:
        cand = (correct_x + offset, correct_y - offset)
        if cand != (correct_x, correct_y) and cand not in unique:
            unique.append(cand)
        offset += 1

    return [f"({cx}, {cy})" for cx, cy in unique]

# =============================================================================
# АРХЕТИП 1: ВОССТАНОВЛЕНИЕ КОМАНДЫ1 ВНУТРИ ЦИКЛА (15% — примеры 1–4, 21, 22)
# =============================================================================

def generate_missing_command():
    while True:
        k = random.choice([2, 3, 4, 5])
        cmd1_x = random.choice([-3, -2, -1, 1, 2, 3])
        cmd1_y = random.choice([-3, -2, -1, 1, 2, 3])

        c2_x, c2_y = random.randint(-4, 4), random.randint(-4, 4)
        c3_x, c3_y = random.randint(-4, 4), random.randint(-4, 4)

        loop_dx = cmd1_x + c2_x + c3_x
        loop_dy = cmd1_y + c2_y + c3_y

        out_x = -k * loop_dx
        out_y = -k * loop_dy

        if out_x == 0 and out_y == 0:
            continue

        is_after = random.choice([True, False])
        if is_after:
            algo_text = f"Повтори {k} раз Команда1 {format_cmd(c2_x, c2_y)} {format_cmd(c3_x, c3_y)} Конец {format_cmd(out_x, out_y)}"
        else:
            algo_text = f"{format_cmd(out_x, out_y)} Повтори {k} раз Команда1 {format_cmd(c2_x, c2_y)} {format_cmd(c3_x, c3_y)} Конец"

        correct_cmd = format_cmd(cmd1_x, cmd1_y)
        distractors = generate_distractors_cmd(cmd1_x, cmd1_y)
        variants = distractors + [correct_cmd]
        random.shuffle(variants)
        correct_idx = variants.index(correct_cmd) + 1

        prompt = (
            f"{INSTRUCTION}\n\n"
            f"Чертёжнику был дан следующий алгоритм: {algo_text}.\n"
            f"После выполнения этого алгоритма Чертёжник вернулся в исходную точку. "
            f"Какую команду надо поставить вместо команды Команда1?\n"
            f"В ответе укажите номер правильного варианта."
        )

        return prompt, variants, str(correct_idx)

# =============================================================================
# АРХЕТИП 2: ЭКВИВАЛЕНТНАЯ КОМАНДА ДЛЯ ЗАМЕНЫ (35% — примеры 5, 16–20, 26, 27)
# =============================================================================

def generate_replace_algorithm():
    while True:
        k = random.choice([2, 3, 4, 5, 6])
        cmd_count = random.choice([2, 3])

        loop_cmds = []
        loop_dx, loop_dy = 0, 0
        for _ in range(cmd_count):
            cx, cy = random.randint(-4, 4), random.randint(-4, 4)
            loop_cmds.append((cx, cy))
            loop_dx += cx
            loop_dy += cy

        if loop_dx == 0 and loop_dy == 0:
            continue

        has_extra = random.choice(["before", "after", "none"])
        extra_x, extra_y = 0, 0
        if has_extra != "none":
            extra_x, extra_y = random.randint(-8, 8), random.randint(-8, 8)

        total_x = k * loop_dx + extra_x
        total_y = k * loop_dy + extra_y

        if total_x == 0 and total_y == 0:
            continue

        loop_str = " ".join(format_cmd(cx, cy) for cx, cy in loop_cmds)
        if has_extra == "before":
            algo_text = f"{format_cmd(extra_x, extra_y)} Повтори {k} раз {loop_str} Конец"
        elif has_extra == "after":
            algo_text = f"Повтори {k} раз {loop_str} Конец {format_cmd(extra_x, extra_y)}"
        else:
            algo_text = f"Повтори {k} раз {loop_str} Конец"

        correct_cmd = format_cmd(total_x, total_y)
        distractors = generate_distractors_cmd(total_x, total_y)
        variants = distractors + [correct_cmd]
        random.shuffle(variants)
        correct_idx = variants.index(correct_cmd) + 1

        prompt = (
            f"{INSTRUCTION}\n\n"
            f"Чертёжнику был дан следующий алгоритм: {algo_text}.\n"
            f"На какую одну команду можно заменить этот алгоритм, чтобы Чертёжник оказался в той же точке, "
            f"что и после выполнения алгоритма?\n"
            f"В ответе укажите номер правильного варианта."
        )

        return prompt, variants, str(correct_idx)

# =============================================================================
# АРХЕТИП 3: КОМАНДА ВОЗВРАТА В ИСХОДНУЮ ТОЧКУ (35% — примеры 6–10, 23–25, 28)
# =============================================================================

def generate_return_command():
    while True:
        k = random.choice([2, 3, 4, 5, 7])
        cmd_count = random.choice([2, 3])

        loop_cmds = []
        loop_dx, loop_dy = 0, 0
        for _ in range(cmd_count):
            cx, cy = random.randint(-4, 4), random.randint(-4, 4)
            loop_cmds.append((cx, cy))
            loop_dx += cx
            loop_dy += cy

        has_extra = random.choice(["before", "after", "none"])
        extra_x, extra_y = 0, 0
        if has_extra != "none":
            extra_x, extra_y = random.randint(-5, 5), random.randint(-5, 5)

        total_x = k * loop_dx + extra_x
        total_y = k * loop_dy + extra_y

        if total_x == 0 and total_y == 0:
            continue

        loop_str = " ".join(format_cmd(cx, cy) for cx, cy in loop_cmds)
        if has_extra == "before":
            algo_text = f"{format_cmd(extra_x, extra_y)} Повтори {k} раз {loop_str} Конец"
        elif has_extra == "after":
            algo_text = f"Повтори {k} раз {loop_str} Конец {format_cmd(extra_x, extra_y)}"
        else:
            algo_text = f"Повтори {k} раз {loop_str} Конец"

        ret_x = -total_x
        ret_y = -total_y

        correct_cmd = format_cmd(ret_x, ret_y)
        distractors = generate_distractors_cmd(ret_x, ret_y)
        variants = distractors + [correct_cmd]
        random.shuffle(variants)
        correct_idx = variants.index(correct_cmd) + 1

        prompt = (
            f"{INSTRUCTION}\n\n"
            f"Чертёжнику был дан следующий алгоритм: {algo_text}.\n"
            f"Какую команду надо выполнить Чертёжнику, чтобы вернуться в исходную точку, "
            f"из которой он начал движение?\n"
            f"В ответе укажите номер правильного варианта."
        )

        return prompt, variants, str(correct_idx)

# =============================================================================
# АРХЕТИП 4: КООРДИНАТЫ НАЧАЛА ИЛИ КОНЦА (15% — примеры 11–15)
# =============================================================================

def generate_find_coordinates():
    while True:
        k = random.choice([3, 4, 5, 7])
        c1 = (random.randint(-3, 3), random.randint(-3, 3))
        c2 = (random.randint(-3, 3), random.randint(-3, 3))
        c3 = (random.randint(-4, 4), random.randint(-4, 4))

        shift_x = k * (c1[0] + c2[0] + c3[0])
        shift_y = k * (c1[1] + c2[1] + c3[1])

        if shift_x == 0 and shift_y == 0:
            continue

        start_x, start_y = random.randint(-5, 5), random.randint(-5, 5)
        end_x = start_x + shift_x
        end_y = start_y + shift_y

        algo_text = f"Повтори {k} раз {format_cmd(c1[0], c1[1])} {format_cmd(c2[0], c2[1])} {format_cmd(c3[0], c3[1])} Конец"

        find_start = random.choice([True, False])

        if find_start:
            correct_val = f"({start_x}, {start_y})"
            distractors = generate_distractors_point(start_x, start_y)
            question_text = (
                f"Каковы координаты точки, с которой Чертёжник начинал движение, "
                f"если в конце он оказался в точке с координатами ({end_x}, {end_y})?"
            )
        else:
            correct_val = f"({end_x}, {end_y})"
            distractors = generate_distractors_point(end_x, end_y)
            question_text = (
                f"Координаты точки, с которой Чертёжник начинал движение: ({start_x}, {start_y}). "
                f"Каковы координаты точки, в которой он оказался после выполнения алгоритма?"
            )

        variants = distractors + [correct_val]
        random.shuffle(variants)
        correct_idx = variants.index(correct_val) + 1

        prompt = (
            f"{INSTRUCTION}\n\n"
            f"Чертёжнику был дан следующий алгоритм: {algo_text}.\n"
            f"{question_text}\n"
            f"В ответе укажите номер правильного варианта."
        )

        return prompt, variants, str(correct_idx)

# =============================================================================
# ТОЧКА ВХОДА ГЕНЕРАТОРА
# =============================================================================

def generate():
    random.seed(os.urandom(16))

    archetype = random.choices(
        ["replace", "return", "missing", "coords"],
        weights=[0.35, 0.35, 0.15, 0.15],
        k=1
    )[0]

    if archetype == "replace":
        prompt, variants, answer = generate_replace_algorithm()
    elif archetype == "return":
        prompt, variants, answer = generate_return_command()
    elif archetype == "missing":
        prompt, variants, answer = generate_missing_command()
    else:
        prompt, variants, answer = generate_find_coordinates()

    return {
        "task": prompt,
        "variants": variants,
        "variant_type": "numbers",
        "answer": answer
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--meta":
            print(json.dumps(META, ensure_ascii=False))
        elif sys.argv[1] == "--generate":
            print(json.dumps(generate(), ensure_ascii=False))