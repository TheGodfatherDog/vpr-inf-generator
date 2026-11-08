import sys
import json
import random
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 10,
    "title": "Таблицы истинности сложных выражений (3 переменные)",
    "has_variants": False
}

# =============================================================================
# КАТАЛОГ ШАБЛОНОВ ДЛЯ 3 ПЕРЕМЕННЫХ
# Каждое действие хранит имя (для расчета ширины) и функцию вычисления
# =============================================================================

TEMPLATES_3_VARS = [
    # 1. (¬A ∨ B ∧ ¬C) ∧ C (примеры 1, 18)
    {
        "expr": "(¬{A} ∨ {B} ∧ ¬{C}) ∧ {C}",
        "steps": [
            ("¬{A}", lambda a, b, c: 1 - a),
            ("¬{C}", lambda a, b, c: 1 - c),
            ("{B} ∧ ¬{C}", lambda a, b, c: b & (1 - c)),
            ("¬{A} ∨ {B} ∧ ¬{C}", lambda a, b, c: (1 - a) | (b & (1 - c))),
            ("(¬{A} ∨ {B} ∧ ¬{C}) ∧ {C}", lambda a, b, c: ((1 - a) | (b & (1 - c))) & c)
        ]
    },
    # 2. ¬A ∧ (¬B ∨ ¬C) (пример 2)
    {
        "expr": "¬{A} ∧ (¬{B} ∨ ¬{C})",
        "steps": [
            ("¬{A}", lambda a, b, c: 1 - a),
            ("¬{B}", lambda a, b, c: 1 - b),
            ("¬{C}", lambda a, b, c: 1 - c),
            ("¬{B} ∨ ¬{C}", lambda a, b, c: (1 - b) | (1 - c)),
            ("¬{A} ∧ (¬{B} ∨ ¬{C})", lambda a, b, c: (1 - a) & ((1 - b) | (1 - c)))
        ]
    },
    # 3. ¬A ∧ B ∨ ¬C (пример 3)
    {
        "expr": "¬{A} ∧ {B} ∨ ¬{C}",
        "steps": [
            ("¬{A}", lambda a, b, c: 1 - a),
            ("¬{C}", lambda a, b, c: 1 - c),
            ("¬{A} ∧ {B}", lambda a, b, c: (1 - a) & b),
            ("¬{A} ∧ {B} ∨ ¬{C}", lambda a, b, c: ((1 - a) & b) | (1 - c))
        ]
    },
    # 4. A ∨ ¬B ∧ ¬C (пример 5)
    {
        "expr": "{A} ∨ ¬{B} ∧ ¬{C}",
        "steps": [
            ("¬{B}", lambda a, b, c: 1 - b),
            ("¬{C}", lambda a, b, c: 1 - c),
            ("¬{B} ∧ ¬{C}", lambda a, b, c: (1 - b) & (1 - c)),
            ("{A} ∨ ¬{B} ∧ ¬{C}", lambda a, b, c: a | ((1 - b) & (1 - c)))
        ]
    },
    # 5. X ∧ (Y ∨ ¬Z) (пример 6)
    {
        "expr": "{A} ∧ ({B} ∨ ¬{C})",
        "steps": [
            ("¬{C}", lambda a, b, c: 1 - c),
            ("{B} ∨ ¬{C}", lambda a, b, c: b | (1 - c)),
            ("{A} ∧ ({B} ∨ ¬{C})", lambda a, b, c: a & (b | (1 - c)))
        ]
    },
    # 6. ¬(A ∨ B ∧ ¬C) (пример 22)
    {
        "expr": "¬({A} ∨ {B} ∧ ¬{C})",
        "steps": [
            ("¬{C}", lambda a, b, c: 1 - c),
            ("{B} ∧ ¬{C}", lambda a, b, c: b & (1 - c)),
            ("{A} ∨ {B} ∧ ¬{C}", lambda a, b, c: a | (b & (1 - c))),
            ("¬({A} ∨ {B} ∧ ¬{C})", lambda a, b, c: 1 - (a | (b & (1 - c))))
        ]
    },
    # 7. ¬(¬A ∧ B ∨ C) (пример 23)
    {
        "expr": "¬(¬{A} ∧ {B} ∨ {C})",
        "steps": [
            ("¬{A}", lambda a, b, c: 1 - a),
            ("¬{A} ∧ {B}", lambda a, b, c: (1 - a) & b),
            ("¬{A} ∧ {B} ∨ {C}", lambda a, b, c: ((1 - a) & b) | c),
            ("¬(¬{A} ∧ {B} ∨ {C})", lambda a, b, c: 1 - (((1 - a) & b) | c))
        ]
    },
    # 8. (A ∨ B) ∨ (B ∧ ¬C) (пример 24)
    {
        "expr": "({A} ∨ {B}) ∨ ({B} ∧ ¬{C})",
        "steps": [
            ("¬{C}", lambda a, b, c: 1 - c),
            ("{A} ∨ {B}", lambda a, b, c: a | b),
            ("{B} ∧ ¬{C}", lambda a, b, c: b & (1 - c)),
            ("({A} ∨ {B}) ∨ ({B} ∧ ¬{C})", lambda a, b, c: (a | b) | (b & (1 - c)))
        ]
    },
    # 9. (¬A ∧ B) ∧ (B ∨ C) (пример 25)
    {
        "expr": "(¬{A} ∧ {B}) ∧ ({B} ∨ {C})",
        "steps": [
            ("¬{A}", lambda a, b, c: 1 - a),
            ("¬{A} ∧ {B}", lambda a, b, c: (1 - a) & b),
            ("{B} ∨ {C}", lambda a, b, c: b | c),
            ("(¬{A} ∧ {B}) ∧ ({B} ∨ {C})", lambda a, b, c: ((1 - a) & b) & (b | c))
        ]
    },
    # 10. ¬(A ∧ C) ∨ (B ∧ C) (пример 26)
    {
        "expr": "¬({A} ∧ {C}) ∨ ({B} ∧ {C})",
        "steps": [
            ("{A} ∧ {C}", lambda a, b, c: a & c),
            ("{B} ∧ {C}", lambda a, b, c: b & c),
            ("¬({A} ∧ {C})", lambda a, b, c: 1 - (a & c)),
            ("¬({A} ∧ {C}) ∨ ({B} ∧ {C})", lambda a, b, c: (1 - (a & c)) | (b & c))
        ]
    },
    # 11. (A ∨ C) ∧ ¬(B ∨ C) (пример 27)
    {
        "expr": "({A} ∨ {C}) ∧ ¬({B} ∨ {C})",
        "steps": [
            ("{A} ∨ {C}", lambda a, b, c: a | c),
            ("{B} ∨ {C}", lambda a, b, c: b | c),
            ("¬({B} ∨ {C})", lambda a, b, c: 1 - (b | c)),
            ("({A} ∨ {C}) ∧ ¬({B} ∨ {C})", lambda a, b, c: (a | c) & (1 - (b | c)))
        ]
    },
    # 12. A ∧ B ∨ C ∧ (A ∨ B) (пример 28)
    {
        "expr": "{A} ∧ {B} ∨ {C} ∧ ({A} ∨ {B})",
        "steps": [
            ("{A} ∨ {B}", lambda a, b, c: a | b),
            ("{A} ∧ {B}", lambda a, b, c: a & b),
            ("{C} ∧ ({A} ∨ {B})", lambda a, b, c: c & (a | b)),
            ("{A} ∧ {B} ∨ {C} ∧ ({A} ∨ {B})", lambda a, b, c: (a & b) | (c & (a | b)))
        ]
    },
    # 13. ¬(A ∨ B ∧ C) ∨ B (пример 30)
    {
        "expr": "¬({A} ∨ {B} ∧ {C}) ∨ {B}",
        "steps": [
            ("{B} ∧ {C}", lambda a, b, c: b & c),
            ("{A} ∨ {B} ∧ {C}", lambda a, b, c: a | (b & c)),
            ("¬({A} ∨ {B} ∧ {C})", lambda a, b, c: 1 - (a | (b & c))),
            ("¬({A} ∨ {B} ∧ {C}) ∨ {B}", lambda a, b, c: (1 - (a | (b & c))) | b)
        ]
    },
    # 14. ¬(A ∧ B ∨ C) ∧ A (пример 31)
    {
        "expr": "¬({A} ∧ {B} ∨ {C}) ∧ {A}",
        "steps": [
            ("{A} ∧ {B}", lambda a, b, c: a & b),
            ("{A} ∧ {B} ∨ {C}", lambda a, b, c: (a & b) | c),
            ("¬({A} ∧ {B} ∨ {C})", lambda a, b, c: 1 - ((a & b) | c)),
            ("¬({A} ∧ {B} ∨ {C}) ∧ {A}", lambda a, b, c: (1 - ((a & b) | c)) & a)
        ]
    },
    # 15. ¬(A ∨ B) ∨ A ∧ ¬C (пример 33)
    {
        "expr": "¬({A} ∨ {B}) ∨ {A} ∧ ¬{C}",
        "steps": [
            ("{A} ∨ {B}", lambda a, b, c: a | b),
            ("¬({A} ∨ {B})", lambda a, b, c: 1 - (a | b)),
            ("¬{C}", lambda a, b, c: 1 - c),
            ("{A} ∧ ¬{C}", lambda a, b, c: a & (1 - c)),
            ("¬({A} ∨ {B}) ∨ {A} ∧ ¬{C}", lambda a, b, c: (1 - (a | b)) | (a & (1 - c)))
        ]
    },
    # 16. (A ∧ ¬B ∨ ¬C) ∨ A (пример 35)
    {
        "expr": "({A} ∧ ¬{B} ∨ ¬{C}) ∨ {A}",
        "steps": [
            ("¬{B}", lambda a, b, c: 1 - b),
            ("¬{C}", lambda a, b, c: 1 - c),
            ("{A} ∧ ¬{B}", lambda a, b, c: a & (1 - b)),
            ("{A} ∧ ¬{B} ∨ ¬{C}", lambda a, b, c: (a & (1 - b)) | (1 - c)),
            ("({A} ∧ ¬{B} ∨ ¬{C}) ∨ {A}", lambda a, b, c: ((a & (1 - b)) | (1 - c)) | a)
        ]
    },
    # 17. A ∧ B ∨ ¬(¬A ∧ C) (пример 37)
    {
        "expr": "{A} ∧ {B} ∨ ¬(¬{A} ∧ {C})",
        "steps": [
            ("¬{A}", lambda a, b, c: 1 - a),
            ("¬{A} ∧ {C}", lambda a, b, c: (1 - a) & c),
            ("¬(¬{A} ∧ {C})", lambda a, b, c: 1 - ((1 - a) & c)),
            ("{A} ∧ {B}", lambda a, b, c: a & b),
            ("{A} ∧ {B} ∨ ¬(¬{A} ∧ {C})", lambda a, b, c: (a & b) | (1 - ((1 - a) & c)))
        ]
    },
    # 18. (¬A ∧ B ∨ C) ∨ ¬B (пример 39)
    {
        "expr": "(¬{A} ∧ {B} ∨ {C}) ∨ ¬{B}",
        "steps": [
            ("¬{A}", lambda a, b, c: 1 - a),
            ("¬{B}", lambda a, b, c: 1 - b),
            ("¬{A} ∧ {B}", lambda a, b, c: (1 - a) & b),
            ("¬{A} ∧ {B} ∨ {C}", lambda a, b, c: ((1 - a) & b) | c),
            ("(¬{A} ∧ {B} ∨ {C}) ∨ ¬{B}", lambda a, b, c: (((1 - a) & b) | c) | (1 - b))
        ]
    }
]

# =============================================================================
# ГЕНЕРАЦИЯ ЗАДАНИЯ
# =============================================================================

def generate():
    random.seed(os.urandom(16))

    if random.random() < 0.85:
        va, vb, vc = "A", "B", "C"
    else:
        va, vb, vc = "X", "Y", "Z"

    tmpl = random.choice(TEMPLATES_3_VARS)
    expr_str = tmpl["expr"].format(A=va, B=vb, C=vc)
    step_count = len(tmpl["steps"])

    # Рассчитываем комфортную ширину для каждой пустой ячейки по длине формулы:
    # от 5ch до 14ch, чтобы ученику было удобно писать от руки
    blank_headers = []
    for step in tmpl["steps"]:
        txt = step[0].format(A=va, B=vb, C=vc)
        w_ch = max(5, min(14, len(txt)))
        blank_headers.append(f'<span style="display:inline-block;min-width:{w_ch}ch;">&nbsp;</span>')

    headers = [va, vb, vc] + blank_headers

    # 8 стандартных входных наборов
    input_rows = [
        (0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1),
        (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)
    ]

    calc_results = []
    for a, b, c in input_rows:
        row_vals = [step[1](a, b, c) for step in tmpl["steps"]]
        calc_results.append(row_vals)

    # Строки бланка ученика (все расчетные ячейки пустые)
    student_rows = []
    for a, b, c in input_rows:
        student_rows.append([str(a), str(b), str(c)] + ["&nbsp;" for _ in range(step_count)])

    final_answer = "".join(str(r[-1]) for r in calc_results)

    # Компактный стиль: убираем лишние вертикальные отступы у ячеек
    compact_css = "<style>.answer-grid td { height: 13px !important; line-height: 1 !important; padding: 0 2px !important; font-size: 0.78em !important; }</style>"
    prompt = f"{compact_css}Заполните таблицу истинности выражения: {expr_str}."

    return {
        "task": prompt,
        "table": {
            "headers": headers,
            "rows": student_rows
        },
        "variants": None,
        "variant_type": None,
        "answer": final_answer
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--meta":
            print(json.dumps(META, ensure_ascii=False))
        elif sys.argv[1] == "--generate":
            print(json.dumps(generate(), ensure_ascii=False))