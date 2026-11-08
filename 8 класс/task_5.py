import sys
import json
import random
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 5,
    "title": "Логические высказывания (И, ИЛИ, НЕ)",
    "has_variants": True
}

# =============================================================================
# БАЗЫ ДАННЫХ И СЛОВАРИ
# =============================================================================

VOWELS = set("аеёиоуыэюя")
CONSONANTS = set("бвгджзйклмнпрстфхцчшщ")

NAMES_POOL = [
    "Анна", "Елена", "Егор", "Иван", "Игорь", "Илья", "Олег", "Ольга", "Алиса",
    "Алексей", "Артем", "Максим", "Татьяна", "Никита", "Михаил", "Полина",
    "Кристина", "Семен", "Николай", "Павел", "Марина", "Сергей", "Глафира",
    "Вадим", "Галина", "Федор", "Юрий", "Тит", "Емеля", "Денис", "Роман",
    "София", "Дарья", "Виктор", "Наталья", "Аида", "Александр", "Илларион"
]

WORDS_POOL = [
    ("растения", ["Орхидея", "Ромашка", "Тюльпан", "Ирис", "Астра", "Нарцисс", "Роза", "Пион", "Клевер"]),
    ("овоща", ["Огурец", "Помидор", "Авокадо", "Редька", "Тыква", "Кабачок", "Морковь", "Свекла"]),
    ("фрукта", ["Яблоко", "Груша", "Банан", "Апельсин", "Персик", "Абрикос", "Ананас", "Лимон", "Манго"]),
    ("слова", ["слива", "яблоко", "банан", "ананас", "апельсин", "груша", "персик", "лимон"])
]

# =============================================================================
# ПРЕДИКАТЫ ДЛЯ СЛОВ (С КОРРЕКТНОЙ ОБРАБОТКОЙ Ь / Ъ)
# =============================================================================

def get_word_predicates(word):
    w = word.lower()
    preds = {}

    # Первая буква
    if w[0] in VOWELS:
        preds[("Первая буква гласная", "Первая")] = True
        preds[("Первая буква согласная", "Первая")] = False
    elif w[0] in CONSONANTS:
        preds[("Первая буква гласная", "Первая")] = False
        preds[("Первая буква согласная", "Первая")] = True

    # Последняя буква (если ь/ъ — предикат гласности/согласности не создается)
    if w[-1] in VOWELS:
        preds[("Последняя буква гласная", "Последняя")] = True
        preds[("Последняя буква согласная", "Последняя")] = False
    elif w[-1] in CONSONANTS:
        preds[("Последняя буква гласная", "Последняя")] = False
        preds[("Последняя буква согласная", "Последняя")] = True

    # Вторая буква
    if len(w) >= 2:
        if w[1] in VOWELS:
            preds[("Вторая буква гласная", "Вторая")] = True
            preds[("Вторая буква согласная", "Вторая")] = False
        elif w[1] in CONSONANTS:
            preds[("Вторая буква гласная", "Вторая")] = False
            preds[("Вторая буква согласная", "Вторая")] = True

    # Третья буква
    if len(w) >= 3:
        if w[2] in VOWELS:
            preds[("Третья буква гласная", "Третья")] = True
            preds[("Третья буква согласная", "Третья")] = False
        elif w[2] in CONSONANTS:
            preds[("Третья буква гласная", "Третья")] = False
            preds[("Третья буква согласная", "Третья")] = True

    # Длина слова
    preds[("Количество букв > 4", "Длина")] = len(w) > 4
    preds[("Количество букв < 5", "Длина")] = len(w) < 5
    preds[("Количество букв > 5", "Длина")] = len(w) > 5
    preds[("Количество букв < 6", "Длина")] = len(w) < 6

    return preds

# =============================================================================
# АРХЕТИП 1 И 2: ИМЕНА И СЛОВА (90%)
# =============================================================================

def generate_word_logic():
    is_name = random.random() < 0.75
    target_kind = random.choices(["ИСТИННО", "ЛОЖНО"], weights=[0.75, 0.25], k=1)[0]

    while True:
        if is_name:
            candidates = random.sample(NAMES_POOL, 4)
            obj_kind = "name"
        else:
            category_title, pool = random.choice(WORDS_POOL)
            candidates = random.sample(pool, 4)
            obj_kind = category_title  # "растения", "овоща", "фрукта" или "слова"

        # Собираем предикаты для всех 4 кандидатов
        cand_preds = [get_word_predicates(c) for c in candidates]
        common_keys = list(set.intersection(*(set(cp.keys()) for cp in cand_preds)))

        if len(common_keys) < 2:
            continue

        # Выбираем два независимых предиката (проверяющих разные свойства)
        pred_key1, pred_key2 = random.sample(common_keys, 2)
        if pred_key1[1] == pred_key2[1]:
            continue

        text_p1, text_p2 = pred_key1[0], pred_key2[0]

        structure_type = random.choice([
            "A_AND_B",
            "NOT_A_AND_B",
            "A_AND_NOT_B",
            "NOT_A_AND_NOT_B",
            "NOT_A_OR_B",
            "A_OR_NOT_B",
            "NOT_A_OR_NOT_B",
            "NOT_BRACKET_AND",
            "NOT_BRACKET_OR"
        ])

        def evaluate_expr(preds_dict):
            val1 = preds_dict[pred_key1]
            val2 = preds_dict[pred_key2]

            if structure_type == "A_AND_B":
                return val1 and val2
            elif structure_type == "NOT_A_AND_B":
                return (not val1) and val2
            elif structure_type == "A_AND_NOT_B":
                return val1 and (not val2)
            elif structure_type == "NOT_A_AND_NOT_B":
                return (not val1) and (not val2)
            elif structure_type == "NOT_A_OR_B":
                return (not val1) or val2
            elif structure_type == "A_OR_NOT_B":
                return val1 or (not val2)
            elif structure_type == "NOT_A_OR_NOT_B":
                return (not val1) or (not val2)
            elif structure_type == "NOT_BRACKET_AND":
                return not (val1 and val2)
            elif structure_type == "NOT_BRACKET_OR":
                return not (val1 or val2)

        # Текстовое представление выражения
        if structure_type == "A_AND_B":
            expr_text = f"({text_p1}) И ({text_p2})"
        elif structure_type == "NOT_A_AND_B":
            expr_text = f"НЕ ({text_p1}) И ({text_p2})"
        elif structure_type == "A_AND_NOT_B":
            expr_text = f"({text_p1}) И НЕ ({text_p2})"
        elif structure_type == "NOT_A_AND_NOT_B":
            expr_text = f"НЕ ({text_p1}) И НЕ ({text_p2})"
        elif structure_type == "NOT_A_OR_B":
            expr_text = f"НЕ ({text_p1}) ИЛИ ({text_p2})"
        elif structure_type == "A_OR_NOT_B":
            expr_text = f"({text_p1}) ИЛИ НЕ ({text_p2})"
        elif structure_type == "NOT_A_OR_NOT_B":
            expr_text = f"НЕ ({text_p1}) ИЛИ НЕ ({text_p2})"
        elif structure_type == "NOT_BRACKET_AND":
            expr_text = f"НЕ (({text_p1}) И ({text_p2}))"
        elif structure_type == "NOT_BRACKET_OR":
            expr_text = f"НЕ (({text_p1}) ИЛИ ({text_p2}))"

        eval_results = [evaluate_expr(cp) for cp in cand_preds]

        # Строгая проверка на единственность решения
        if target_kind == "ИСТИННО":
            if eval_results.count(True) == 1:
                ans_idx = eval_results.index(True) + 1
                break
        else:
            if eval_results.count(False) == 1:
                ans_idx = eval_results.index(False) + 1
                break

    # Идеально согласованные русские формулировки
    if obj_kind == "name":
        prompt = (
            f"Для какого из приведенных имен {target_kind} высказывание:\n"
            f"{expr_text}?"
        )
    elif obj_kind == "слова":
        prompt = (
            f"Для какого из приведенных слов {target_kind} высказывание:\n"
            f"{expr_text}?"
        )
    else:
        prompt = (
            f"Укажите название {obj_kind}, для которого {target_kind} высказывание:\n"
            f"{expr_text}?"
        )

    return prompt, candidates, str(ans_idx)

# =============================================================================
# АРХЕТИП 3: ЧИСЛА И ЦИФРЫ (10% — примеры 3, 7, 35)
# =============================================================================

def generate_number_logic():
    target_kind = random.choices(["ИСТИННО", "ЛОЖНО"], weights=[0.70, 0.30], k=1)[0]

    while True:
        candidates = []
        while len(candidates) < 4:
            n = random.randint(1000, 9999)
            if n not in candidates:
                candidates.append(n)

        cand_str = [str(c) for c in candidates]
        preds = [
            (int(s[0]) % 2 == 0, int(s[-1]) % 2 == 0)
            for s in cand_str
        ]

        stmt_type = random.choice(["E_AND_O", "NOT_E_OR_NOT_E", "E_AND_NOT_O"])

        if stmt_type == "E_AND_O":
            expr_text = "(Первая цифра четная) И (Последняя цифра нечетная)"
            eval_results = [p[0] and (not p[1]) for p in preds]
        elif stmt_type == "NOT_E_OR_NOT_E":
            expr_text = "НЕ (Первая цифра четная) ИЛИ НЕ (Последняя цифра четная)"
            eval_results = [(not p[0]) or (not p[1]) for p in preds]
        else:
            expr_text = "(Первая цифра четная) И НЕ (Последняя цифра нечетная)"
            eval_results = [p[0] and (not (not p[1])) for p in preds]

        if target_kind == "ИСТИННО":
            if eval_results.count(True) == 1:
                ans_idx = eval_results.index(True) + 1
                variants = [str(c) for c in candidates]
                break
        else:
            if eval_results.count(False) == 1:
                ans_idx = eval_results.index(False) + 1
                variants = [str(c) for c in candidates]
                break

    prompt = (
        f"Для какого из приведенных чисел {target_kind} высказывание:\n"
        f"{expr_text}?"
    )

    return prompt, variants, str(ans_idx)

# =============================================================================
# ТОЧКА ВХОДА ГЕНЕРАТОРА
# =============================================================================

def generate():
    random.seed(os.urandom(16))

    if random.random() < 0.90:
        prompt, variants, answer = generate_word_logic()
    else:
        prompt, variants, answer = generate_number_logic()

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