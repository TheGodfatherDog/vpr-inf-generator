import sys
import json
import random
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 3,
    "title": "Арифметика в позиционных системах счисления",
    "has_variants": False
}

# =============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================================================

def to_repr(val, base):
    """Форматирует число с нижним индексом СС."""
    if base == 2:
        return f"{bin(val)[2:]}₂"
    elif base == 8:
        return f"{oct(val)[2:]}₈"
    elif base == 16:
        return f"{hex(val)[2:].upper()}₁₆"
    elif base == 10:
        return f"{val}₁₀"
    return str(val)

def to_clean(val, base):
    """Возвращает чистое число без префиксов в нужной СС."""
    if base == 2:
        return bin(val)[2:]
    elif base == 8:
        return oct(val)[2:]
    elif base == 16:
        return hex(val)[2:].upper()
    return str(val)

# =============================================================================
# АРХЕТИП 1: ВОСЬМЕРИЧНАЯ АРИФМЕТИКА -> ОТВЕТ В 8-Й СС (45%)
# =============================================================================

def generate_octal_arithmetic():
    is_subtraction = random.choice([True, False])

    while True:
        # 50% двузначные числа, 50% трехзначные
        is_large = random.choice([True, False])
        if is_large:
            v2 = random.randint(30, 220)
            diff = random.randint(15, 200)
        else:
            v2 = random.randint(7, 45)
            diff = random.randint(5, 45)

        v1 = v2 + diff

        # Проверяем наличие заёма/переноса в младшем разряде
        if is_subtraction:
            if (v1 % 8 < v2 % 8) or random.random() < 0.30:
                ans_val = v1 - v2
                str_v1 = to_repr(v1, 8)
                str_v2 = to_repr(v2, 8)
                prompt = (
                    f"Выполните вычитание: {str_v1} − {str_v2}. "
                    "Ответ запишите в восьмеричной системе счисления. Основание системы писать не нужно."
                )
                return prompt, to_clean(ans_val, 8)
        else:
            if ((v2 % 8) + (diff % 8) >= 8) or random.random() < 0.30:
                ans_val = v1
                str_v2 = to_repr(v2, 8)
                str_diff = to_repr(diff, 8)
                prompt = (
                    f"Выполните сложение: {str_v2} + {str_diff}. "
                    "Ответ запишите в восьмеричной системе счисления. Основание системы писать не нужно."
                )
                return prompt, to_clean(ans_val, 8)

# =============================================================================
# АРХЕТИП 2: ШЕСТНАДЦАТЕРИЧНАЯ АРИФМЕТИКА -> ОТВЕТ В 16-Й СС (25%)
# =============================================================================

def generate_hex_arithmetic():
    is_subtraction = random.choice([True, False])

    while True:
        is_large = random.random() < 0.35
        if is_large:
            v2 = random.randint(100, 2500)
            diff = random.randint(50, 1500)
        else:
            v2 = random.randint(20, 220)
            diff = random.randint(15, 180)

        v1 = v2 + diff

        # Гарантируем наличие шестнадцатеричных цифр (A-F) в записи
        if is_subtraction:
            ans_val = v1 - v2
            raw_v1 = hex(v1)[2:].upper()
            raw_v2 = hex(v2)[2:].upper()
            if any(ch in "ABCDEF" for ch in raw_v1 + raw_v2):
                str_v1 = to_repr(v1, 16)
                str_v2 = to_repr(v2, 16)
                prompt = (
                    f"Выполните вычитание: {str_v1} − {str_v2}. "
                    "Ответ запишите в шестнадцатеричной системе счисления. Основание системы писать не нужно."
                )
                return prompt, to_clean(ans_val, 16)
        else:
            ans_val = v1
            raw_v2 = hex(v2)[2:].upper()
            raw_diff = hex(diff)[2:].upper()
            if any(ch in "ABCDEF" for ch in raw_v2 + raw_diff):
                str_v2 = to_repr(v2, 16)
                str_diff = to_repr(diff, 16)
                prompt = (
                    f"Выполните сложение: {str_v2} + {str_diff}. "
                    "Ответ запишите в шестнадцатеричной системе счисления. Основание системы писать не нужно."
                )
                return prompt, to_clean(ans_val, 16)

# =============================================================================
# АРХЕТИП 3: ВЫЧИСЛЕНИЕ ВЫРАЖЕНИЙ -> ОТВЕТ В ДЕСЯТИЧНОЙ СС (30%)
# =============================================================================

def generate_to_decimal_arithmetic():
    subtype = random.choices(["hex_diff", "hex_sum", "mixed_diff", "oct_sum_diff"], weights=[0.40, 0.25, 0.20, 0.15], k=1)[0]

    while True:
        if subtype == "hex_diff":
            # Разность двух 16-ричных чисел (примеры 1-6, 11)
            is_close = random.random() < 0.65
            if is_close:
                # Старшие разряды совпадают строго (без переполнения ниббла)
                prefix = random.randint(5, 25) * 16
                b_off = random.randint(0, 11)
                a_off = b_off + random.randint(2, 15 - b_off)
                v1 = prefix + a_off
                v2 = prefix + b_off
            else:
                v2 = random.randint(40, 300)
                v1 = v2 + random.randint(15, 80)

            ans = v1 - v2
            str_v1 = to_repr(v1, 16)
            str_v2 = to_repr(v2, 16)
            prompt = (
                f"Вычислите значение выражения {str_v1} − {str_v2}. "
                "Ответ запишите в десятичной системе счисления."
            )
            return prompt, str(ans)

        elif subtype == "hex_sum":
            # Сложение двух 16-ричных чисел -> 10-я СС (примеры 7, 8, 25)
            v1 = random.randint(40, 220)
            v2 = random.randint(15, 120)
            ans = v1 + v2
            str_v1 = to_repr(v1, 16)
            str_v2 = to_repr(v2, 16)
            prompt = (
                f"Вычислите значение выражения {str_v1} + {str_v2}. "
                "Ответ запишите в десятичной системе счисления."
            )
            return prompt, str(ans)

        elif subtype == "mixed_diff":
            # Смешанные СС: 16-ричное минус 8-ричное (примеры 9, 10)
            v2 = random.randint(60, 260)
            diff = random.randint(3, 15)
            v1 = v2 + diff
            ans = v1 - v2
            str_v1 = to_repr(v1, 16)
            str_v2 = to_repr(v2, 8)
            prompt = (
                f"Вычислите значение выражения {str_v1} − {str_v2}. "
                "Ответ запишите в десятичной системе счисления."
            )
            return prompt, str(ans)

        else: # oct_sum_diff
            # Действия в 8-й СС -> 10-я СС (примеры 23, 24)
            is_sub = random.choice([True, False])
            v2 = random.randint(30, 250)
            diff = random.randint(15, 150)
            if is_sub:
                v1 = v2 + diff
                ans = v1 - v2
                str_v1 = to_repr(v1, 8)
                str_v2 = to_repr(v2, 8)
                prompt = (
                    f"Вычислите значение выражения {str_v1} − {str_v2}. "
                    "Ответ запишите в десятичной системе счисления."
                )
            else:
                ans = v2 + diff
                str_v2 = to_repr(v2, 8)
                str_diff = to_repr(diff, 8)
                prompt = (
                    f"Вычислите значение выражения {str_v2} + {str_diff}. "
                    "Ответ запишите в десятичной системе счисления."
                )
            return prompt, str(ans)

# =============================================================================
# ТОЧКА ВХОДА ГЕНЕРАТОРА
# =============================================================================

def generate():
    random.seed(os.urandom(16))

    archetype = random.choices(
        ["octal", "hex", "to_decimal"],
        weights=[0.45, 0.25, 0.30],
        k=1
    )[0]

    if archetype == "octal":
        prompt, answer = generate_octal_arithmetic()
    elif archetype == "hex":
        prompt, answer = generate_hex_arithmetic()
    else:
        prompt, answer = generate_to_decimal_arithmetic()

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