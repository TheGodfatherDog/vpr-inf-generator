import sys
import json
import random
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 6,
    "title": "Таблицы истинности логических выражений",
    "has_variants": False
}

# =============================================================================
# КАТАЛОГ ШАБЛОНОВ ВЫРАЖЕНИЙ (НА ОСНОВЕ 31 ПРИМЕРА ФИОКО)
# =============================================================================

TEMPLATES = [
    # 1. Базовые с одним отрицанием (примеры 1, 2, 3, 4, 7)
    {
        "expr": "{A} ∨ ¬{B}",
        "steps": [
            lambda a, b: 1 - b,
            lambda a, b: a | (1 - b)
        ]
    },
    {
        "expr": "¬{A} ∨ {B}",
        "steps": [
            lambda a, b: 1 - a,
            lambda a, b: (1 - a) | b
        ]
    },
    {
        "expr": "¬{A} ∧ {B}",
        "steps": [
            lambda a, b: 1 - a,
            lambda a, b: (1 - a) & b
        ]
    },
    {
        "expr": "{A} ∧ ¬{B}",
        "steps": [
            lambda a, b: 1 - b,
            lambda a, b: a & (1 - b)
        ]
    },

    # 2. Два отрицания (примеры 5, 6)
    {
        "expr": "¬{A} ∧ ¬{B}",
        "steps": [
            lambda a, b: 1 - a,
            lambda a, b: 1 - b,
            lambda a, b: (1 - a) & (1 - b)
        ]
    },
    {
        "expr": "¬{A} ∨ ¬{B}",
        "steps": [
            lambda a, b: 1 - a,
            lambda a, b: 1 - b,
            lambda a, b: (1 - a) | (1 - b)
        ]
    },

    # 3. Скобки и поглощение (примеры 8, 9, 10, 11, 16, 17, 18, 19)
    {
        "expr": "{A} ∨ ({A} ∧ {B})",
        "steps": [
            lambda a, b: a & b,
            lambda a, b: a | (a & b)
        ]
    },
    {
        "expr": "{A} ∧ ({A} ∨ {B})",
        "steps": [
            lambda a, b: a | b,
            lambda a, b: a & (a | b)
        ]
    },
    {
        "expr": "{B} ∧ ({A} ∨ {B})",
        "steps": [
            lambda a, b: a | b,
            lambda a, b: b & (a | b)
        ]
    },
    {
        "expr": "{B} ∨ ({A} ∧ {B})",
        "steps": [
            lambda a, b: a & b,
            lambda a, b: b | (a & b)
        ]
    },

    # 4. Отрицание скобок (примеры 12, 13)
    {
        "expr": "¬({A} ∨ {B})",
        "steps": [
            lambda a, b: a | b,
            lambda a, b: 1 - (a | b)
        ]
    },
    {
        "expr": "¬({A} ∧ {B})",
        "steps": [
            lambda a, b: a & b,
            lambda a, b: 1 - (a & b)
        ]
    },

    # 5. Составные выражения (примеры 14, 15, 20, 21, 22, 23)
    {
        "expr": "{B} ∨ (¬{A} ∧ {B})",
        "steps": [
            lambda a, b: 1 - a,
            lambda a, b: (1 - a) & b,
            lambda a, b: b | ((1 - a) & b)
        ]
    },
    {
        "expr": "¬{B} ∧ ({A} ∨ {B})",
        "steps": [
            lambda a, b: a | b,
            lambda a, b: 1 - b,
            lambda a, b: (1 - b) & (a | b)
        ]
    },
    {
        "expr": "¬{A} ∨ ¬({A} ∧ {B})",
        "steps": [
            lambda a, b: a & b,
            lambda a, b: 1 - a,
            lambda a, b: 1 - (a & b),
            lambda a, b: (1 - a) | (1 - (a & b))
        ]
    },
    {
        "expr": "{B} ∧ ¬({A} ∨ {B})",
        "steps": [
            lambda a, b: a | b,
            lambda a, b: 1 - (a | b),
            lambda a, b: b & (1 - (a | b))
        ]
    },
    {
        "expr": "({A} ∨ {B}) ∧ ({A} ∧ {B})",
        "steps": [
            lambda a, b: a | b,
            lambda a, b: a & b,
            lambda a, b: (a | b) & (a & b)
        ]
    },
    {
        "expr": "¬({A} ∨ {B}) ∨ ({A} ∧ {B})",
        "steps": [
            lambda a, b: a | b,
            lambda a, b: 1 - (a | b),
            lambda a, b: a & b,
            lambda a, b: (1 - (a | b)) | (a & b)
        ]
    },

    # 6. Расширенные выражения (примеры 26, 27, 30, 31)
    {
        "expr": "(¬{A} ∧ ¬{B}) ∨ ¬{A}",
        "steps": [
            lambda a, b: 1 - a,
            lambda a, b: 1 - b,
            lambda a, b: (1 - a) & (1 - b),
            lambda a, b: ((1 - a) & (1 - b)) | (1 - a)
        ]
    },
    {
        "expr": "(¬{A} ∨ ¬{B}) ∧ ¬{B}",
        "steps": [
            lambda a, b: 1 - a,
            lambda a, b: 1 - b,
            lambda a, b: (1 - a) | (1 - b),
            lambda a, b: ((1 - a) | (1 - b)) & (1 - b)
        ]
    },
    {
        "expr": "¬{A} ∧ ¬{B} ∨ {B}",
        "steps": [
            lambda a, b: 1 - a,
            lambda a, b: 1 - b,
            lambda a, b: (1 - a) & (1 - b),
            lambda a, b: ((1 - a) & (1 - b)) | b
        ]
    },
    {
        "expr": "¬{A} ∧ ¬{B} ∧ {A}",
        "steps": [
            lambda a, b: 1 - a,
            lambda a, b: 1 - b,
            lambda a, b: (1 - a) & (1 - b),
            lambda a, b: ((1 - a) & (1 - b)) & a
        ]
    }
]

# =============================================================================
# ГЕНЕРАЦИЯ ЗАДАНИЯ
# =============================================================================

def generate():
    random.seed(os.urandom(16))

    # Выбираем переменные: A и B (85%) или X и Y (15%)
    if random.random() < 0.85:
        var_a, var_b = "A", "B"
    else:
        var_a, var_b = "X", "Y"

    tmpl = random.choice(TEMPLATES)
    expr_str = tmpl["expr"].format(A=var_a, B=var_b)
    step_count = len(tmpl["steps"])

    # В шапке таблицы НЕ показываем действия:
    # Подписаны только входные переменные, остальные колонки — пустые графы для ученика
    headers = [var_a, var_b] + ["&nbsp;" for _ in range(step_count)]

    # Стандартные наборы строк для таблицы истинности двух переменных
    input_rows = [(0, 0), (0, 1), (1, 0), (1, 1)]

    # Вычисляем истинные значения для формирования ответа учителя
    calc_results = []
    for a, b in input_rows:
        row_vals = [step_fn(a, b) for step_fn in tmpl["steps"]]
        calc_results.append(row_vals)

    # Ответ для учителя — значения последней колонки
    final_col_values = "".join(str(r[-1]) for r in calc_results)

    # Строки для бланка ученика (все расчетные ячейки пустые)
    student_rows = []
    for a, b in input_rows:
        student_rows.append([str(a), str(b)] + ["&nbsp;" for _ in range(step_count)])

    prompt = f"Заполните таблицу истинности выражения: {expr_str}."

    return {
        "task": prompt,
        "table": {
            "headers": headers,
            "rows": student_rows
        },
        "variants": None,
        "variant_type": None,
        "answer": final_col_values
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--meta":
            print(json.dumps(META, ensure_ascii=False))
        elif sys.argv[1] == "--generate":
            print(json.dumps(generate(), ensure_ascii=False))