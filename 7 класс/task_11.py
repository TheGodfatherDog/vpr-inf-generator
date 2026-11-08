import sys
import json
import random
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 11,
    "title": "Цветовая модель RGB и кодирование цвета",
    "has_variants": True
}

# =============================================================================
# БАЗА ЦВЕТОВ RGB
# =============================================================================

# 8 базовых вершин куба RGB (85% задач)
BASE_COLORS = [
    ("Чёрный", (0, 0, 0)),
    ("Белый", (255, 255, 255)),
    ("Красный", (255, 0, 0)),
    ("Зелёный", (0, 255, 0)),
    ("Синий", (0, 0, 255)),
    ("Жёлтый", (255, 255, 0)),
    ("Голубой", (0, 255, 255)),
    ("Пурпурный", (255, 0, 255))
]

# Оттенки (15% задач, взяты из экзаменационных примеров)
SHADE_COLORS = [
    ("Серый", (127, 127, 127)),
    ("Тёмно-красный", (127, 0, 0)),
    ("Тёмно-зелёный", (0, 127, 0)),
    ("Тёмно-синий", (0, 0, 127)),
    ("Тёмно-фиолетовый", (64, 0, 64)),
    ("Фиолетовый", (127, 0, 255)),
    ("Оранжево-красный", (255, 69, 0))
]

def format_code(rgb_tuple):
    """Единый строгий формат кортежа: (255, 255, 0)."""
    r, g, b = rgb_tuple
    return f"({r}, {g}, {b})"

# =============================================================================
# НАПРАВЛЕНИЕ 1: КОД -> НАЗВАНИЕ ЦВЕТА (50%)
# =============================================================================

def generate_code_to_name():
    is_base = random.random() < 0.85

    if is_base:
        target_name, target_code = random.choice(BASE_COLORS)
        # Для базового цвета дистракторы берем ТОЛЬКО из базовых (никакой путаницы с оттенками!)
        other_names = [name for name, _ in BASE_COLORS if name != target_name]
    else:
        target_name, target_code = random.choice(SHADE_COLORS)
        other_names = [name for name, _ in (BASE_COLORS + SHADE_COLORS) if name != target_name]

    distractors = random.sample(other_names, 3)
    options = distractors + [target_name]
    random.shuffle(options)

    correct_idx = options.index(target_name) + 1
    code_str = format_code(target_code)

    prompt = f"Какой цвет в цветовой модели RGB кодируется как {code_str}?"

    return prompt, options, str(correct_idx)

# =============================================================================
# НАПРАВЛЕНИЕ 2: НАЗВАНИЕ ЦВЕТА -> КОД (50%)
# =============================================================================

def generate_name_to_code():
    is_base = random.random() < 0.85

    if is_base:
        target_name, target_code = random.choice(BASE_COLORS)
        # Дистракторы строго из базовых цветов
        other_codes = [format_code(code) for _, code in BASE_COLORS if code != target_code]
    else:
        target_name, target_code = random.choice(SHADE_COLORS)
        other_codes = [format_code(code) for _, code in (BASE_COLORS + SHADE_COLORS) if code != target_code]

    target_code_str = format_code(target_code)

    other_codes = list(dict.fromkeys(other_codes))
    distractors = random.sample(other_codes, 3)

    options = distractors + [target_code_str]
    random.shuffle(options)

    correct_idx = options.index(target_code_str) + 1

    prompt = f"Как в цветовой модели RGB кодируется {target_name.lower()} цвет?"

    return prompt, options, str(correct_idx)

# =============================================================================
# ТОЧКА ВХОДА ГЕНЕРАТОРА
# =============================================================================

def generate():
    random.seed(os.urandom(16))

    if random.random() < 0.50:
        prompt, variants, answer = generate_code_to_name()
    else:
        prompt, variants, answer = generate_name_to_code()

    return {
        "task": prompt,
        "variants": variants,
        "variant_type": "numbers",  # Обязательно "numbers" для нумерации вариантов 1), 2), 3), 4) в app.js!
        "answer": answer
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--meta":
            print(json.dumps(META, ensure_ascii=False))
        elif sys.argv[1] == "--generate":
            print(json.dumps(generate(), ensure_ascii=False))