import sys
import json
import random
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 3,
    "title": "Расширения и типы файлов (соответствие)",
    "has_variants": False
}

FILE_CATEGORIES = {
    "текстовый документ": [
        "txt", "doc", "docx", "pdf", "rtf", "odt"
    ],
    "графический файл": [
        "jpg", "jpeg", "png", "bmp", "gif", "tiff"
    ],
    "аудиофайл": [
        "mp3", "wav", "ogg", "aac", "wma", "flac"
    ],
    "видеофайл": [
        "mp4", "avi", "mkv", "mov", "webm", "wmv"
    ],
    "архивный файл": [
        "zip", "rar", "7z", "tar", "gz"
    ],
    "презентация": [
        "ppt", "pptx", "odp", "pps"
    ],
    "электронная таблица": [
        "xls", "xlsx", "ods", "csv"
    ],
    "веб-страница": [
        "html", "htm"
    ],
    "исполняемый файл": [
        "exe", "bat", "cmd"
    ]
}

def get_cleaned_categories():
    cleaned = {}
    for category_name, extensions in FILE_CATEGORIES.items():
        clean_exts = list({
            ext.strip().lower().lstrip(".")
            for ext in extensions
            if ext.strip()
        })
        if len(clean_exts) >= 3:
            cleaned[category_name.strip()] = clean_exts
    return cleaned

def generate():
    random.seed(os.urandom(16))
    categories_db = get_cleaned_categories()

    while True:
        available_category_names = list(categories_db.keys())
        if len(available_category_names) < 3:
            raise ValueError("В базе должно быть не менее 3 категорий!")

        selected_category_names = random.sample(available_category_names, 3)

        set_1 = set(categories_db[selected_category_names[0]])
        set_2 = set(categories_db[selected_category_names[1]])
        set_3 = set(categories_db[selected_category_names[2]])

        if (set_1 & set_2) or (set_1 & set_3) or (set_2 & set_3):
            continue

        distribution_patterns = [
            [2, 2, 1],
            [3, 1, 1],
            [2, 1, 2],
            [1, 2, 2],
            [1, 3, 1],
            [1, 1, 3]
        ]
        counts = random.choice(distribution_patterns)

        selected_pairs = []
        is_possible = True

        for index, count in enumerate(counts):
            category_name = selected_category_names[index]
            available_extensions = categories_db[category_name]

            if len(available_extensions) < count:
                is_possible = False
                break

            sampled_extensions = random.sample(available_extensions, count)
            for ext in sampled_extensions:
                selected_pairs.append((ext, str(index + 1)))

        if not is_possible:
            continue

        is_strictly_valid = True
        for ext, category_digit in selected_pairs:
            matches = [
                str(idx + 1)
                for idx, cat_name in enumerate(selected_category_names)
                if ext in categories_db[cat_name]
            ]
            if len(matches) != 1 or matches[0] != category_digit:
                is_strictly_valid = False
                break

        if not is_strictly_valid or len(selected_pairs) != 5:
            continue

        random.shuffle(selected_pairs)
        column_letters = ["А", "Б", "В", "Г", "Д"]

        answer_code = "".join([pair[1] for pair in selected_pairs])

        extensions_line = "   ".join([
            f"{column_letters[i]}) {selected_pairs[i][0]}"
            for i in range(5)
        ])
        categories_line = "   ".join([
            f"{i + 1}) {selected_category_names[i]}"
            for i in range(3)
        ])

        # Компактное оформление в одну строку без лишних переносов
        task_prompt = (
            "Установите соответствие между расширениями и типами файлов: для каждой позиции первого столбца, "
            "обозначенной буквой, подберите соответствующую позицию из второго столбца, обозначенную цифрой.\n"
            f"РАСШИРЕНИЯ: {extensions_line}\n"
            f"ТИПЫ ФАЙЛОВ: {categories_line}\n"
            "Запишите в таблицу выбранные цифры под соответствующими буквами:"
        )

        return {
            "task": task_prompt,
            "variants": None,
            "answer_table": column_letters,
            "answer": answer_code
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--meta":
            print(json.dumps(META, ensure_ascii=False))
        elif sys.argv[1] == "--generate":
            print(json.dumps(generate(), ensure_ascii=False))