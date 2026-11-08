import sys
import json
import random
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 10,
    "title": "Информационный объём текста и кодировки символов",
    "has_variants": True
}

# =============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================================================

def plural_bits(n):
    """Склонение слова 'бит' (8 бит, 16 бит, 32 бита, 4 бита)."""
    n_abs = abs(n) % 100
    n_last = n_abs % 10
    if 11 <= n_abs <= 19:
        return f"{n} бит"
    if 2 <= n_last <= 4:
        return f"{n} бита"
    return f"{n} бит"

# =============================================================================
# БАНК ИЗ 40 ВЫВЕРЕННЫХ ПОСЛОВИЦ И ЛИТЕРАТУРНЫХ СТРОК
# =============================================================================

PHRASES_BANK = [
    "Мама мыла раму.",
    "Красота спасёт мир.",
    "Один в поле не воин.",
    "Дело мастера боится.",
    "Язык мой — враг мой.",
    "Век живи, век учись.",
    "Своя ноша не тянет.",
    "Не всё коту Масленица.",
    "Друг познается в беде.",
    "Мал золотник, да дорог.",
    "Цыплят по осени считают.",
    "Где тонко, там и рвётся.",
    "У лукоморья дуб зелёный.",
    "Повторенье — мать ученья.",
    "Что посеешь, то и пожнёшь.",
    "Не то золото, что блестит.",
    "Любви все возрасты покорны.",
    "Ты жива ещё, моя старушка?",
    "Тише едешь — дальше будешь.",
    "На вкус и цвет товарища нет.",
    "Плоды лета — сокровища зимы.",
    "Близок локоть, да не укусишь.",
    "Старый друг лучше новых двух.",
    "Роняет лес багряный свой убор.",
    "Мороз и солнце; день чудесный!",
    "В гостях хорошо, а дома лучше.",
    "Терпенье и труд — всё перетрут.",
    "Последняя туча рассеянной бури!",
    "Унылая пора! Очей очарованье!",
    "На чужой каравай рот не разевай.",
    "Кто рано встаёт, тому Бог подаёт.",
    "Ученье — свет, а неученье — тьма.",
    "Не откладывай дела в долгий ящик.",
    "Семь раз отмерь — один раз отрежь.",
    "Учиться — одно, научиться — другое.",
    "Слово — серебро, молчание — золото.",
    "Полюбишь работу — и она тебя полюбит.",
    "Без труда не выловишь и рыбку из пруда.",
    "Слух обо мне пройдет по всей Руси великой.",
    "Свет мой, зеркальце! скажи да всю правду доложи."
]

# =============================================================================
# АРХЕТИП 1: ПРЯМАЯ ЗАДАЧА (75%)
# =============================================================================

ENCODINGS = [
    ("Unicode", 16, "В одной из кодировок Unicode каждый символ кодируется 16 битами. Определите информационный объём в байтах следующего предложения в данной кодировке:"),
    ("Win-1251", 8, "В кодировке Win-1251 каждый символ кодируется 8 битами. Определите информационный объём в байтах следующего предложения в данной кодировке:"),
    ("КОИ-8", 8, "В кодировке КОИ-8 каждый символ кодируется 8 битами. Определите информационный объём в байтах следующего предложения в данной кодировке:")
]

def generate_direct():
    enc_name, bits_per_char, prompt_template = random.choice(ENCODINGS)
    phrase = random.choice(PHRASES_BANK)
    K = len(phrase)

    bytes_per_char = bits_per_char // 8
    correct_bytes = K * bytes_per_char

    raw_distractors = []

    if bits_per_char == 16:
        # Для Unicode (2 байта на символ):
        # 1. Забыл умножить на 2
        raw_distractors.append(K)
        # 2. Ошибки подсчета длины (+-1, +-2, +-4 символа)
        raw_distractors.extend([
            (K - 1) * 2,
            (K + 1) * 2,
            (K - 2) * 2,
            (K + 2) * 2,
            (K + 4) * 2
        ])
        # 3. Перевел в биты (классическая ошибка ученика)
        raw_distractors.append(K * 16)
    else:
        # Для 8-битных кодировок (1 байт на символ):
        # 1. Ошибочно умножил на 2
        raw_distractors.append(K * 2)
        # 2. Ошибки подсчета знаков (+-1, +-2, +-3, +-4)
        raw_distractors.extend([
            K - 1, K + 1,
            K - 2, K + 2,
            K - 3, K + 3,
            K - 4, K + 4
        ])
        # 3. Перевел в биты
        raw_distractors.append(K * 8)

    unique_distractors = []
    for d in raw_distractors:
        if d > 0 and d != correct_bytes and d not in unique_distractors:
            unique_distractors.append(d)

    random.shuffle(unique_distractors)
    if len(unique_distractors) < 3:
        return None

    chosen_distractors = unique_distractors[:3]
    options_vals = chosen_distractors + [correct_bytes]
    random.shuffle(options_vals)

    variants = [f"{val} байт" for val in options_vals]
    correct_idx = options_vals.index(correct_bytes) + 1

    task_prompt = f"{prompt_template}\n\n{phrase}"

    return task_prompt, variants, str(correct_idx)

# =============================================================================
# АРХЕТИП 2: ОБРАТНАЯ ЗАДАЧА (25%)
# =============================================================================

def generate_inverse():
    phrase = random.choice(PHRASES_BANK)
    K = len(phrase)

    # Правильный вес символа: 8 или 16 бит
    bits_per_char = random.choice([8, 16])
    bytes_per_char = bits_per_char // 8
    total_bytes = K * bytes_per_char

    correct_option = plural_bits(bits_per_char)

    # Пул дистракторов СТРОГО в битах (с корректными грамматическими окончаниями)
    distractor_numbers = [4, 8, 16, 24, 32, 64, K, total_bytes]
    unique_distractors = []

    for num in distractor_numbers:
        opt_str = plural_bits(num)
        if opt_str != correct_option and opt_str not in unique_distractors:
            unique_distractors.append(opt_str)

    random.shuffle(unique_distractors)
    if len(unique_distractors) < 3:
        return None

    chosen_distractors = unique_distractors[:3]
    options = chosen_distractors + [correct_option]
    random.shuffle(options)

    correct_idx = options.index(correct_option) + 1

    task_prompt = (
        f"Информационный объём данного предложения составляет {total_bytes} байт:\n\n"
        f"{phrase}\n\n"
        "Определите, сколькими битами кодируется один символ."
    )

    return task_prompt, options, str(correct_idx)

# =============================================================================
# ТОЧКА ВХОДА ГЕНЕРАТОРА
# =============================================================================

def generate():
    random.seed(os.urandom(16))

    while True:
        is_inverse = random.random() < 0.25

        if is_inverse:
            result = generate_inverse()
        else:
            result = generate_direct()

        if result is not None:
            task_text, variants, answer_digit = result
            return {
                "task": task_text,
                "variants": variants,
                "variant_type": "numbers",
                "answer": answer_digit
            }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--meta":
            print(json.dumps(META, ensure_ascii=False))
        elif sys.argv[1] == "--generate":
            print(json.dumps(generate(), ensure_ascii=False))