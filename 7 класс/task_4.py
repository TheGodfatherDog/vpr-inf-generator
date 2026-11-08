import sys
import json
import random
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 4,
    "title": "Адресация в сети Интернет (составление URL)",
    "has_variants": False
}

PROTOCOLS = ["http", "https", "ftp"]

DOMAINS = [
    "school", "obr", "biblio", "teach", "home", "book", "weather",
    "music", "sport", "test", "olympiada", "flowers", "box", "travel",
    "nature", "science", "library", "autumn", "spring", "planet"
]

ZONES = ["ru", "com", "org", "net", "edu", "info", "kz"]

FILENAMES = [
    "books", "table", "rus", "math", "hello", "tests", "karl", "page",
    "summer", "winter", "may", "rose", "tulip", "dog", "timer", "work",
    "report", "notes", "music", "photo", "document", "spb", "water"
]

EXTENSIONS = [
    "txt", "doc", "docx", "xls", "xlsx", "pdf", "jpg", "jpeg",
    "gif", "png", "rar", "htm", "html", "pptx", "rtf", "cpp"
]

DIRECTORIES = [
    "red", "work", "foto", "2024", "months", "docs", "files",
    "archive", "class7", "tasks", "materials"
]

def generate_standard_url():
    protocol = random.choice(PROTOCOLS)
    domain = random.choice(DOMAINS)
    zone = random.choice(ZONES)
    filename = random.choice(FILENAMES)
    ext = random.choice(EXTENSIONS)

    if len({domain, zone, filename, ext}) != 4:
        return None

    if random.choice([True, False]):
        server_part1, server_part2 = f"{domain}.", zone
    else:
        server_part1, server_part2 = domain, f".{zone}"

    if random.choice([True, False]):
        file_part1, file_part2 = f"{filename}.", ext
    else:
        file_part1, file_part2 = filename, f".{ext}"

    target_tokens = [
        protocol,
        "://",
        server_part1,
        server_part2,
        "/",
        file_part1,
        file_part2
    ]

    if len(set(target_tokens)) != 7:
        return None

    shuffled_tokens = target_tokens.copy()
    random.shuffle(shuffled_tokens)

    answer_digits = "".join([str(shuffled_tokens.index(token) + 1) for token in target_tokens])

    # Все 7 фрагментов идут единой компактной строкой через пробелы
    tokens_str = "   ".join([f"{i + 1}) {shuffled_tokens[i]}" for i in range(7)])

    task_prompt = (
        f"Доступ к файлу {filename}.{ext}, находящемуся на сервере {domain}.{zone}, "
        f"осуществляется по протоколу {protocol}. "
        "Фрагменты адреса файла закодированы цифрами от 1 до 7. "
        "Запишите последовательность этих цифр, кодирующую адрес указанного файла в сети Интернет:\n"
        f"{tokens_str}"
    )

    return task_prompt, answer_digits

def generate_relocated_url():
    old_protocol, new_protocol = random.sample(PROTOCOLS, 2)
    old_domain, new_domain = random.sample(DOMAINS, 2)
    old_zone, new_zone = random.sample(ZONES, 2)
    directory = random.choice(DIRECTORIES)
    filename = random.choice(FILENAMES)
    ext = random.choice(EXTENSIONS)

    if len({old_domain, new_domain, directory, filename}) != 4:
        return None

    old_url = f"{old_protocol}://{old_domain}.{old_zone}/{filename}.{ext}"

    target_sequence = [
        f"{new_protocol}:/",
        "/",
        new_domain,
        f".{new_zone}",
        "/",
        directory,
        "/",
        filename,
        f".{ext}"
    ]

    available_tokens = [
        f"{old_protocol}:/",
        old_domain,
        f"{new_protocol}:/",
        new_domain,
        f".{new_zone}",
        directory,
        filename,
        f".{ext}",
        "/"
    ]

    available_tokens = list(dict.fromkeys(available_tokens))
    if len(available_tokens) != 9:
        return None

    random.shuffle(available_tokens)
    answer_digits = "".join([str(available_tokens.index(token) + 1) for token in target_sequence])

    # Все 9 фрагментов выводятся единым сплошным потоком без принудительного разрыва
    tokens_str = "   ".join([f"{i + 1}) {available_tokens[i]}" for i in range(9)])

    task_prompt = (
        f"Файл {filename}.{ext} был выложен в сети Интернет по адресу {old_url}.\n"
        f"Позже его переместили в каталог {directory} на сайте {new_domain}.{new_zone}, "
        f"доступ к которому осуществляется по протоколу {new_protocol}. Имя файла не изменилось.\n"
        f"Фрагменты адреса закодированы цифрами от 1 до 9. "
        "Запишите последовательность цифр, кодирующую адрес файла после перемещения:\n"
        f"{tokens_str}"
    )

    return task_prompt, answer_digits

def generate():
    random.seed(os.urandom(16))

    while True:
        chosen_generator = random.choice([generate_standard_url, generate_relocated_url])
        result = chosen_generator()

        if result is None:
            continue

        task_prompt, answer_code = result

        return {
            "task": task_prompt,
            "variants": None,
            "answer": answer_code
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--meta":
            print(json.dumps(META, ensure_ascii=False))
        elif sys.argv[1] == "--generate":
            print(json.dumps(generate(), ensure_ascii=False))