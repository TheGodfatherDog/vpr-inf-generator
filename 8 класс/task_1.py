import sys
import json
import random
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 1,
    "title": "Системы счисления (перевод чисел и подсчёт единиц)",
    "has_variants": False
}

# =============================================================================
# АРХЕТИП 1: ДВОИЧНАЯ <-> ДЕСЯТИЧНАЯ (45%)
# =============================================================================

def generate_bin_dec():
    # 6-8 бит (от 35 до 250)
    val = random.randint(35, 250)
    bin_str = bin(val)[2:]

    if random.choice([True, False]):
        # Из 2 в 10
        phrasings = [
            f"Переведите двоичное число {bin_str} в десятичную систему счисления.",
            f"Переведите число {bin_str} из двоичной системы счисления в десятичную."
        ]
        prompt = random.choice(phrasings)
        answer = str(val)
    else:
        # Из 10 в 2
        phrasings = [
            f"Переведите число {val} из десятичной системы счисления в двоичную систему счисления. В ответе укажите двоичное число. Основание системы счисления указывать не нужно.",
            f"Переведите десятичное число {val} в двоичную систему счисления. Основание системы писать не нужно."
        ]
        prompt = random.choice(phrasings)
        answer = bin_str

    return prompt, answer

# =============================================================================
# АРХЕТИП 2: ВОСЬМЕРИЧНАЯ <-> ДЕСЯТИЧНАЯ (25%)
# =============================================================================

def generate_oct_dec():
    # Числа от 45 до 280 (в восьмеричной системе от 55 до 430)
    val = random.randint(45, 280)
    oct_str = oct(val)[2:]

    if random.choice([True, False]):
        # Из 8 в 10
        phrasings = [
            f"Переведите число {oct_str} из восьмеричной системы счисления в десятичную. Основание системы писать не нужно.",
            f"Переведите восьмеричное число {oct_str} в десятичную систему счисления."
        ]
        prompt = random.choice(phrasings)
        answer = str(val)
    else:
        # Из 10 в 8
        phrasings = [
            f"Переведите десятичное число {val} в восьмеричную систему счисления. Основание системы писать не нужно.",
            f"Переведите число {val} из десятичной системы счисления в восьмеричную систему счисления. Основание системы счисления указывать не нужно."
        ]
        prompt = random.choice(phrasings)
        answer = oct_str

    return prompt, answer

# =============================================================================
# АРХЕТИП 3: ШЕСТНАДЦАТЕРИЧНАЯ <-> ДЕСЯТИЧНАЯ (23%)
# =============================================================================

def generate_hex_dec():
    # Числа от 75 до 350
    val = random.randint(75, 350)
    hex_str = hex(val)[2:].upper()

    if random.choice([True, False]):
        # Из 16 в 10
        phrasings = [
            f"Переведите число {hex_str} из шестнадцатеричной системы счисления в десятичную. Основание системы писать не нужно.",
            f"Переведите шестнадцатеричное число {hex_str} в десятичную систему счисления."
        ]
        prompt = random.choice(phrasings)
        answer = str(val)
    else:
        # Из 10 в 16
        phrasings = [
            f"Переведите десятичное число {val} в шестнадцатеричную систему счисления. Основание системы писать не нужно.",
            f"Переведите число {val} из десятичной системы счисления в шестнадцатеричную систему счисления. Основание системы счисления указывать не нужно."
        ]
        prompt = random.choice(phrasings)
        answer = hex_str

    return prompt, answer

# =============================================================================
# АРХЕТИП 4: ПОДСЧЁТ ЕДИНИЦ В ДВОИЧНОЙ ЗАПИСИ (7% — шаблон №40)
# =============================================================================

def generate_count_ones():
    while True:
        val = random.randint(45, 250)
        bin_str = bin(val)[2:]
        ones_count = bin_str.count("1")
        # Исключаем крайние тривиальные случаи (1 единица или одни единицы)
        if 2 <= ones_count <= len(bin_str) - 2:
            prompt = f"Сколько единиц содержит двоичная запись десятичного числа {val}?"
            return prompt, str(ones_count)

# =============================================================================
# ТОЧКА ВХОДА ГЕНЕРАТОРА
# =============================================================================

def generate():
    random.seed(os.urandom(16))

    archetype = random.choices(
        ["bin_dec", "oct_dec", "hex_dec", "count_ones"],
        weights=[0.45, 0.25, 0.23, 0.07],
        k=1
    )[0]

    if archetype == "bin_dec":
        prompt, answer = generate_bin_dec()
    elif archetype == "oct_dec":
        prompt, answer = generate_oct_dec()
    elif archetype == "hex_dec":
        prompt, answer = generate_hex_dec()
    else:
        prompt, answer = generate_count_ones()

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