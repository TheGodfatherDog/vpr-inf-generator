import sys
import json
import random
import os
import math

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 8,
    "title": "Алфавитный подход к измерению информации (мощность алфавита)",
    "has_variants": False
}

# Допустимые мощности алфавитов N = 2^i
ALPHABET_POWERS = [
    (4, 2),
    (8, 3),
    (16, 4),
    (32, 5),
    (64, 6),
    (128, 7),
    (256, 8),
    (512, 9),
    (1024, 10)
]

def plural_symbols(n):
    """Корректное грамматическое склонение слова 'символ'."""
    n_abs = abs(n) % 100
    n_last = n_abs % 10
    if 11 <= n_abs <= 19:
        return f"{n} символов"
    if n_last == 1:
        return f"{n} символ"
    if 2 <= n_last <= 4:
        return f"{n} символа"
    return f"{n} символов"

def format_decimal(val):
    """Форматирует число в школьный стандарт (через запятую, без лишних нулей)."""
    if val == int(val):
        return str(int(val))
    formatted = f"{val:.2f}".rstrip('0').rstrip('.')
    return formatted.replace('.', ',')

def generate_direct():
    """Прямая задача: найти объем в байтах по мощности N и длине K."""
    want_integer = random.random() < 0.70

    if want_integer:
        # Для целого ответа подходит любая степень, включая i = 8
        N, i = random.choice(ALPHABET_POWERS)
        step = 8 // math.gcd(i, 8)
        k_multiplier = random.randint(2, 60)
        K = k_multiplier * step
        bytes_val = (K * i) // 8
    else:
        # Для дробного ответа исключаем i = 8 (N = 256 дает только целые байты!)
        valid_powers = [p for p in ALPHABET_POWERS if p[1] != 8]
        N, i = random.choice(valid_powers)

        # Выбираем K так, чтобы (K * i) % 8 было равно 2, 4 или 6 (дроби .25, .5, .75)
        candidates = []
        for test_k in range(6, 120):
            rem = (test_k * i) % 8
            if rem in [2, 4, 6]:
                candidates.append(test_k)

        K = random.choice(candidates)
        bytes_val = (K * i) / 8

    symbols_str = plural_symbols(K)

    phrasings = [
        f"Сообщение, записанное буквами {N}-символьного алфавита, содержит {symbols_str}. "
        "Чему равен информационный объём этого сообщения в байтах?",

        f"Сообщение, записанное символами {N}-символьного алфавита, содержит {symbols_str}. "
        "Определите информационный объём этого сообщения в байтах.",

        f"Текст составлен с помощью {N}-символьного алфавита и содержит {symbols_str}. "
        "Чему равен информационный объём этого сообщения в байтах? Единицы измерения писать не нужно."
    ]

    prompt = random.choice(phrasings)
    return prompt, format_decimal(bytes_val)

def generate_inverse():
    """Обратная задача: найти количество символов K по объёму в байтах."""
    N, i = random.choice(ALPHABET_POWERS)

    # Шаг для K, чтобы объем в байтах (K * i / 8) был строго целым числом
    step = 8 // math.gcd(i, 8)

    # Красивые школьные длины текстов
    base_k = random.choice([12, 16, 20, 24, 30, 32, 40, 48, 50, 60, 64, 70, 80, 96, 100, 120, 150, 160, 200])
    K = ((base_k + step - 1) // step) * step

    bytes_val = (K * i) // 8

    phrasings = [
        f"Сколько символов содержит сообщение, записанное с помощью {N}-символьного алфавита, если его объём равен {bytes_val} байт?",
        f"Информационный объём сообщения, записанного символами {N}-символьного алфавита, составляет {bytes_val} байт. Сколько символов в этом сообщении?",
        f"Определите количество символов в тексте, составленном из букв {N}-символьного алфавита, если объём текста равен {bytes_val} байт."
    ]

    prompt = random.choice(phrasings)
    return prompt, str(K)

def generate():
    random.seed(os.urandom(16))

    # 85% прямых задач, 15% обратных
    if random.random() < 0.85:
        prompt, answer = generate_direct()
    else:
        prompt, answer = generate_inverse()

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