import sys
import json
import random
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 6,
    "title": "Декодирование сообщений (азбука Морзе и шифры)",
    "has_variants": False
}

# =============================================================================
# 1. БАНК СЛОВ (Используются строго целиком, без обрезки)
# =============================================================================

# Слова со строго уникальными буквами (длина 4–6 букв)
WORDS_UNIQUE = [
    "ЛИМОН", "ПОЛЕТ", "ОЛИМП", "ПРАВО", "ОКЕАН",
    "ТУМАН", "ПАРОМ", "СПОРТ", "МЕТРО", "АДРЕС",
    "КАТЕР", "ПИЛОТ", "ФАКЕЛ", "ГРАНИТ", "КОМЕТА",
    "СТРЕЛА", "МОЛНИЯ", "АРБУЗ", "ПОЕЗД", "ЗОНТИК",
    "МИНУТА", "ФЛАГ", "ВЕТКА", "ПЕСОК"
]

# Слова с повторяющимися буквами
WORDS_REPEATS = [
    "ВОПРОС", "ОПРАВА", "ВАССАЛ", "ВАРВАР", "ПОЛОСА",
    "КОЛОС", "РАКЕТА", "ПЛАНЕТА", "КУБИК", "ЗВОНОК",
    "РАССВЕТ", "БАРАБАН"
]

# Азбука Морзе
MORSE_TABLE = {
    "А": "•−",   "Б": "−•••", "В": "•−−",  "Г": "−−•",
    "Д": "−••",  "Е": "•",    "Ж": "•••−", "З": "−−••",
    "И": "••",   "Й": "•−−−", "К": "−•−",  "Л": "•−••",
    "М": "−−",   "Н": "−•",   "О": "−−−",  "П": "•−−•",
    "Р": "•−•",  "С": "•••",  "Т": "−",    "У": "••−",
    "Ф": "••−•", "Х": "••••", "Ц": "−•−•", "Ч": "−−−•",
    "Ш": "−−−−", "Щ": "−−•−", "Ы": "−•−−", "Ь": "−••−",
    "Э": "••−••","Ю": "••−−", "Я": "•−•−"
}

# =============================================================================
# 2. ДЕКОДЕР ДЛЯ ПРОВЕРКИ ОДНОЗНАЧНОСТИ РЕШЕНИЯ
# =============================================================================

def find_all_decodings(encoded_str, code_to_char, max_limit=25):
    """Находит все возможные варианты разбиения строки по кодовой таблице."""
    memo = {}

    def backtrack(idx):
        if idx == len(encoded_str):
            return [""]
        if idx in memo:
            return memo[idx]

        results = []
        for code, ch in code_to_char.items():
            if encoded_str.startswith(code, idx):
                sub_res = backtrack(idx + len(code))
                for s in sub_res:
                    results.append(ch + s)
                    if len(results) >= max_limit:
                        break
            if len(results) >= max_limit:
                break

        memo[idx] = results
        return results

    return backtrack(0)

# =============================================================================
# 3. ГЕНЕРАЦИЯ АРХЕТИПОВ
# =============================================================================

def generate_repeats_archetype():
    """Архетип 3 (25%): Какие буквы в сообщении повторяются?"""
    for _ in range(60):
        word = random.choice(WORDS_REPEATS)
        word_letters = list(set(word))

        # Добавляем 1-2 буквы-дистрактора
        other_letters = [ch for ch in MORSE_TABLE.keys() if ch not in word_letters]
        distractors = random.sample(other_letters, min(2, len(other_letters)))
        alphabet = sorted(word_letters + distractors)

        char_to_code = {ch: MORSE_TABLE[ch] for ch in alphabet}
        code_to_char = {v: k for k, v in char_to_code.items()}

        encoded_str = "".join([char_to_code[ch] for ch in word])
        decodings = find_all_decodings(encoded_str, code_to_char)

        if len(decodings) == 1 and decodings[0] == word:
            repeated = sorted(list({ch for ch in word if word.count(ch) > 1}))
            answer = "".join(repeated)

            task_prompt = (
                "Сообщение было зашифровано кодом. Использовались только буквы, приведенные в таблице.\n"
                "Определите, какие буквы в сообщении повторяются, и запишите их в ответе "
                f"(в алфавитном порядке, без пробелов):\n{encoded_str}"
            )

            return {
                "task": task_prompt,
                "code_table": {
                    "headers": alphabet,
                    "rows": [[char_to_code[ch] for ch in alphabet]]
                },
                "variants": None,
                "answer": answer
            }
    return None

def generate_unique_letters_archetype():
    """Архетип 2 (35%): Буквы в сообщении не повторяются (с дистракторами!)"""
    symbols = ['*', '+', '~', '#', '@', '^']
    rus_alphabet = list("АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЭЮЯ")

    for _ in range(60):
        word = random.choice(WORDS_UNIQUE)
        word_letters = list(word)

        # ОБЯЗАТЕЛЬНО добавляем 1–2 буквы-дистрактора, чтобы таблица была длиннее слова
        other_letters = [ch for ch in rus_alphabet if ch not in word_letters]
        distractors = random.sample(other_letters, random.choice([1, 2]))
        all_table_letters = sorted(word_letters + distractors)

        # Генерируем шаблоны кодов для всех букв таблицы
        s1, s2, s3 = random.sample(symbols, 3)
        patterns = [s1, s2, s1 + s2, s2 + s1, s3 + s1, s2 + s3, s1 + s3, s3 + s2, s1 + s2 + s3]
        random.shuffle(patterns)

        char_to_code = {all_table_letters[i]: patterns[i] for i in range(len(all_table_letters))}
        code_to_char = {v: k for k, v in char_to_code.items()}

        encoded_str = "".join([char_to_code[ch] for ch in word])
        all_decodings = find_all_decodings(encoded_str, code_to_char)

        # Без условия — несколько решений, с условием "буквы не повторяются" — СТРОГО 1
        unique_decodings = [d for d in all_decodings if len(d) == len(set(d))]

        if len(all_decodings) > 1 and len(unique_decodings) == 1 and unique_decodings[0] == word:
            ask_count = random.choice([True, False])

            if ask_count:
                task_prompt = (
                    "Вася и Петя играли в шпионов и кодировали сообщение собственным шифром. "
                    "Фрагмент кодовой таблицы приведен ниже.\n"
                    "Определите, из скольких букв состоит сообщение, если известно, "
                    f"что буквы в нем не повторяются:\n{encoded_str}"
                )
                answer = str(len(word))
            else:
                task_prompt = (
                    "Вася и Петя играли в шпионов и кодировали сообщение собственным шифром. "
                    "Фрагмент кодовой таблицы приведен ниже.\n"
                    "Расшифруйте сообщение, если известно, что буквы в нем не повторяются:\n"
                    f"{encoded_str}"
                )
                answer = word

            return {
                "task": task_prompt,
                "code_table": {
                    "headers": all_table_letters,
                    "rows": [[char_to_code[ch] for ch in all_table_letters]]
                },
                "variants": None,
                "answer": answer
            }
    return None

def generate_standard_morse_archetype():
    """Архетип 1 (40%): Однозначное декодирование радиограммы Морзе"""
    for _ in range(60):
        word = random.choice(WORDS_UNIQUE + WORDS_REPEATS)
        word_letters = list(set(word))

        # Добавляем 1–2 дистрактора
        other_letters = [ch for ch in MORSE_TABLE.keys() if ch not in word_letters]
        distractors = random.sample(other_letters, min(2, len(other_letters)))
        alphabet = sorted(word_letters + distractors)

        char_to_code = {ch: MORSE_TABLE[ch] for ch in alphabet}
        code_to_char = {v: k for k, v in char_to_code.items()}

        encoded_str = "".join([char_to_code[ch] for ch in word])
        decodings = find_all_decodings(encoded_str, code_to_char)

        if len(decodings) == 1 and decodings[0] == word:
            ask_count = random.choice([True, False])

            if ask_count:
                task_prompt = (
                    "От разведчика была получена шифрованная радиограмма, переданная азбукой Морзе:\n"
                    f"{encoded_str}\n"
                    "При передаче было потеряно разбиение на буквы, но использовались только буквы из таблицы.\n"
                    "Определите текст радиограммы. В ответе укажите, сколько букв было в исходной радиограмме:"
                )
                answer = str(len(word))
            else:
                task_prompt = (
                    "От разведчика была получена шифрованная радиограмма, переданная азбукой Морзе:\n"
                    f"{encoded_str}\n"
                    "При передаче было потеряно разбиение на буквы, но использовались только буквы из таблицы.\n"
                    "Расшифруйте радиограмму и запишите в ответе расшифрованное слово:"
                )
                answer = word

            return {
                "task": task_prompt,
                "code_table": {
                    "headers": alphabet,
                    "rows": [[char_to_code[ch] for ch in alphabet]]
                },
                "variants": None,
                "answer": answer
            }
    return None

# =============================================================================
# 4. ТОЧКА ВХОДА
# =============================================================================

def generate():
    random.seed(os.urandom(16))

    while True:
        choice = random.choices(
            ["repeats", "unique_letters", "standard_morse"],
            weights=[0.25, 0.35, 0.40],
            k=1
        )[0]

        if choice == "repeats":
            res = generate_repeats_archetype()
        elif choice == "unique_letters":
            res = generate_unique_letters_archetype()
        else:
            res = generate_standard_morse_archetype()

        if res is not None:
            return res

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--meta":
            print(json.dumps(META, ensure_ascii=False))
        elif sys.argv[1] == "--generate":
            print(json.dumps(generate(), ensure_ascii=False))