import sys
import json
import random
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 4,
    "title": "Двоичная арифметика (сложение, вычитание, умножение, деление)",
    "has_variants": False
}

# =============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================================================

def format_prompt(op_name, symbol, val1, val2):
    """Формирует условие в одном из двух официальных стилей ФИОКО."""
    bin1 = bin(val1)[2:]
    bin2 = bin(val2)[2:]

    if random.choice([True, False]):
        # Формат с индексами (образцы 26-37)
        prompt = (
            f"Выполните {op_name}: {bin1}₂ {symbol} {bin2}₂. "
            "Ответ запишите в двоичной системе счисления. Основание системы писать не нужно."
        )
    else:
        # Развернутый текстовый формат (образцы 1-25)
        prompt = (
            f"Выполните {op_name} чисел, представленных в двоичной системе счисления: {bin1} {symbol} {bin2}. "
            "Ответ запишите в двоичной системе счисления."
        )

    return prompt

# =============================================================================
# АРХЕТИП 1: СЛОЖЕНИЕ В ДВОИЧНОЙ СС (40%)
# =============================================================================

def generate_addition():
    while True:
        # Длина 3-6 бит
        v1 = random.randint(9, 55)
        v2 = random.randint(5, 45)

        # Проверяем, что сложение нетривиальное (есть перенос разряда)
        if (v1 & v2) != 0:
            ans = bin(v1 + v2)[2:]
            prompt = format_prompt("сложение", "+", v1, v2)
            return prompt, ans

# =============================================================================
# АРХЕТИП 2: ВЫЧИТАНИЕ В ДВОИЧНОЙ СС (30%)
# =============================================================================

def generate_subtraction():
    while True:
        v1 = random.randint(16, 60)
        v2 = random.randint(5, 45)

        if v1 <= v2:
            continue

        # Гарантируем заём разряда (в битовой записи v2 есть 1 там, где у v1 стоит 0)
        if (~v1 & v2) != 0:
            ans = bin(v1 - v2)[2:]
            prompt = format_prompt("вычитание", "−", v1, v2)
            return prompt, ans

# =============================================================================
# АРХЕТИП 3: УМНОЖЕНИЕ В ДВОИЧНОЙ СС (15%)
# =============================================================================

def generate_multiplication():
    while True:
        # Множители длиной 2-4 бита (исключая 0 и 1)
        v1 = random.randint(4, 15)
        v2 = random.randint(2, 7)

        # Ограничиваем результат для комфортного счета в столбик
        if v1 * v2 <= 75:
            ans = bin(v1 * v2)[2:]
            prompt = format_prompt("умножение", "×", v1, v2)
            return prompt, ans

# =============================================================================
# АРХЕТИП 4: ДЕЛЕНИЕ В ДВОИЧНОЙ СС (15%)
# =============================================================================

def generate_division():
    while True:
        # Делитель от 2 до 7 (10₂, 11₂, 100₂, 101₂, 110₂, 111₂)
        divisor = random.randint(2, 7)
        # Частное от 3 до 15
        quotient = random.randint(3, 15)
        # Делимое гарантированно делится нацело
        dividend = divisor * quotient

        if dividend <= 75:
            ans = bin(quotient)[2:]
            prompt = format_prompt("деление", "÷", dividend, divisor)
            return prompt, ans

# =============================================================================
# ТОЧКА ВХОДА ГЕНЕРАТОРА
# =============================================================================

def generate():
    random.seed(os.urandom(16))

    archetype = random.choices(
        ["add", "sub", "mul", "div"],
        weights=[0.40, 0.30, 0.15, 0.15],
        k=1
    )[0]

    if archetype == "add":
        prompt, answer = generate_addition()
    elif archetype == "sub":
        prompt, answer = generate_subtraction()
    elif archetype == "mul":
        prompt, answer = generate_multiplication()
    else:
        prompt, answer = generate_division()

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