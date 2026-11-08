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

WORDS_UNIQUE = [
    "ЛИМОН", "ПОЛЕТ", "ОЛИМП", "ПРАВО", "ОКЕАН",
    "ТУМАН", "ПАРОМ", "СПОРТ", "МЕТРО", "АДРЕС",
    "КАТЕР", "ПИЛОТ", "ФАКЕЛ", "ГРАНИТ", "КОМЕТА",
    "СТРЕЛА", "МОЛНИЯ", "АРБУЗ", "ПОЕЗД", "ЗОНТИК",
    "МИНУТА", "ФЛАГ", "ВЕТКА", "ПЕСОК"
]

WORDS_REPEATS = [
    "ВОПРОС", "ОПРАВА", "ВАССАЛ", "ВАРВАР", "ПОЛОСА",
    "КОЛОС", "РАКЕТА", "ПЛАНЕТА", "КУБИК", "ЗВОНОК",
    "РАССВЕТ", "БАРАБАН"
]

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

def find_all_decodings(encoded_str, code_to_char, max_limit=500):
    memo = {}
    def backtrack(idx):
        if idx == len(encoded_str):
            return [""]
        if idx in memo:
            return memo[idx]
        results = []
        for code, ch in code_to_char.items():
            if encoded_str.startswith(code, idx):
                for s in backtrack(idx + len(code)):
                    results.append(ch + s)
                    if len(results) >= max_limit:
                        break
            if len(results) >= max_limit:
                break
        memo[idx] = results
        return results
    return backtrack(0)

def generate_repeats_archetype():
    for _ in range(60):
        word = random.choice(WORDS_REPEATS)
        word_letters = list(set(word))
        other_letters = [ch for ch in MORSE_TABLE.keys() if ch not in word_letters]
        alphabet = sorted(word_letters + random.sample(other_letters, min(2, len(other_letters))))

        char_to_code = {ch: MORSE_TABLE[ch] for ch in alphabet}
        code_to_char = {v: k for k, v in char_to_code.items()}
        encoded_str = "".join([char_to_code[ch] for ch in word])
        decodings = find_all_decodings(encoded_str, code_to_char)

        if len(decodings) == 1 and decodings[0] == word:
            answer = "".join(sorted({ch for ch in word if word.count(ch) > 1}))
            task_prompt = (
                "Сообщение было зашифровано кодом с использованием букв из таблицы. "
                "Определите, какие буквы в сообщении повторяются, и запишите их в ответе (в алфавитном порядке, без пробелов):\n"
                f"{encoded_str}"
            )
            return {
                "task": task_prompt,
                "code_table": {"headers": alphabet, "rows": [[char_to_code[ch] for ch in alphabet]]},
                "variants": None,
                "answer": answer
            }
    return None

def generate_unique_letters_archetype():
    symbols = ['*', '+', '~', '#', '@', '^']
    rus_alphabet = list("АБВГДЕЖЗИКЛМНОПРСТУФХЦЧШЭЮЯ")

    for _ in range(60):
        word = random.choice(WORDS_UNIQUE)
        word_letters = list(word)
        other_letters = [ch for ch in rus_alphabet if ch not in word_letters]
        all_table_letters = sorted(word_letters + random.sample(other_letters, random.choice([1, 2])))

        s1, s2, s3 = random.sample(symbols, 3)
        patterns = [s1, s2, s1 + s2, s2 + s1, s3 + s1, s2 + s3, s1 + s3, s3 + s2, s1 + s2 + s3]
        random.shuffle(patterns)

        char_to_code = {all_table_letters[i]: patterns[i] for i in range(len(all_table_letters))}
        code_to_char = {v: k for k, v in char_to_code.items()}
        encoded_str = "".join([char_to_code[ch] for ch in word])
        all_decodings = find_all_decodings(encoded_str, code_to_char)
        unique_decodings = [d for d in all_decodings if len(d) == len(set(d))]

        if len(all_decodings) > 1 and len(unique_decodings) == 1 and unique_decodings[0] == word:
            if random.choice([True, False]):
                task_prompt = (
                    "Вася и Петя кодировали сообщение собственным шифром. "
                    "Определите, из скольких букв состоит сообщение, если известно, что буквы в нем не повторяются:\n"
                    f"{encoded_str}"
                )
                answer = str(len(word))
            else:
                task_prompt = (
                    "Вася и Петя кодировали сообщение собственным шифром. "
                    "Расшифруйте сообщение, если известно, что буквы в нем не повторяются:\n"
                    f"{encoded_str}"
                )
                answer = word

            return {
                "task": task_prompt,
                "code_table": {"headers": all_table_letters, "rows": [[char_to_code[ch] for ch in all_table_letters]]},
                "variants": None,
                "answer": answer
            }
    return None

def generate_standard_morse_archetype():
    for _ in range(60):
        word = random.choice(WORDS_UNIQUE + WORDS_REPEATS)
        word_letters = list(set(word))
        other_letters = [ch for ch in MORSE_TABLE.keys() if ch not in word_letters]
        alphabet = sorted(word_letters + random.sample(other_letters, min(2, len(other_letters))))

        char_to_code = {ch: MORSE_TABLE[ch] for ch in alphabet}
        code_to_char = {v: k for k, v in char_to_code.items()}
        encoded_str = "".join([char_to_code[ch] for ch in word])
        decodings = find_all_decodings(encoded_str, code_to_char)

        if len(decodings) == 1 and decodings[0] == word:
            if random.choice([True, False]):
                task_prompt = (
                    "Получена шифрованная радиограмма, переданная азбукой Морзе (разбиение на буквы потеряно). "
                    "Определите, сколько букв было в исходной радиограмме:\n"
                    f"{encoded_str}"
                )
                answer = str(len(word))
            else:
                task_prompt = (
                    "Получена шифрованная радиограмма, переданная азбукой Морзе (разбиение на буквы потеряно). "
                    "Расшифруйте радиограмму и запишите полученное слово:\n"
                    f"{encoded_str}"
                )
                answer = word

            return {
                "task": task_prompt,
                "code_table": {"headers": alphabet, "rows": [[char_to_code[ch] for ch in alphabet]]},
                "variants": None,
                "answer": answer
            }
    return None

def generate():
    random.seed(os.urandom(16))
    while True:
        choice = random.choices(["repeats", "unique_letters", "standard_morse"], weights=[0.25, 0.35, 0.40], k=1)[0]
        res = (generate_repeats_archetype() if choice == "repeats"
               else generate_unique_letters_archetype() if choice == "unique_letters"
               else generate_standard_morse_archetype())
        if res is not None:
            return res

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--meta":
            print(json.dumps(META, ensure_ascii=False))
        elif sys.argv[1] == "--generate":
            print(json.dumps(generate(), ensure_ascii=False))