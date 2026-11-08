import sys
import json
import random
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 7,
    "title": "Информационный объём носителей и количество файлов",
    "has_variants": False
}

# =============================================================================
# СПРАВОЧНИКИ И ПУЛЫ ДАННЫХ
# =============================================================================

FILE_TYPES = [
    "видеофайлов",
    "аудиофайлов",
    "изображений",
    "фотографий",
    "документов",
    "презентаций",
    "электронных книг",
    "аудиокниг"
]

MEDIA_TYPES = [
    "флеш-карте",
    "карте памяти",
    "USB-накопителе"
]

# Объёмы накопителей в Гбайтах
CARDS_GB = [1, 2, 4, 8, 10, 16, 20, 32, 64, 128, 256]

# Размеры файлов в Мбайтах: степени двойки + круглые практические размеры
FILES_MB_POW2 = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048]
FILES_MB_ARBITRARY = [3, 5, 10, 15, 20, 25, 40, 50, 100, 200, 300, 400, 500, 700]

# Размеры файлов в Гбайтах
FILES_GB = [1, 2, 3, 4, 5]

# Грамматически согласованные формулировки
PHRASINGS = [
    "Сколько {file_type} размером {file_size_str} может уместиться на {media} объёмом {card_size_str}?",
    "Определите максимальное количество {file_type} размером {file_size_str}, которые можно сохранить на {media} объёмом {card_size_str}.",
    "Какое наибольшее число {file_type} размером {file_size_str} удастся записать на {media} объёмом {card_size_str}?"
]

# =============================================================================
# ГЕНЕРАЦИЯ ЗАДАЧИ
# =============================================================================

def generate():
    random.seed(os.urandom(16))

    while True:
        file_type = random.choice(FILE_TYPES)
        media = random.choice(MEDIA_TYPES)
        template = random.choice(PHRASINGS)
        card_gb = random.choice(CARDS_GB)

        # Категории размеров:
        # 1. Мбайты (степени двойки, деление нацело) ~ 50%
        # 2. Мбайты (деление с остатком) ~ 35%
        # 3. Гбайты ~ 15%
        size_category = random.choices(
            ["pow2_mb", "arbitrary_mb", "gb"],
            weights=[0.50, 0.35, 0.15],
            k=1
        )[0]

        if size_category == "gb":
            file_gb = random.choice(FILES_GB)
            if file_gb > card_gb:
                continue
            count = card_gb // file_gb
            file_size_str = f"{file_gb} Гбайт"

        elif size_category == "pow2_mb":
            file_mb = random.choice(FILES_MB_POW2)
            total_mb = card_gb * 1024
            if file_mb > total_mb:
                continue
            count = total_mb // file_mb
            file_size_str = f"{file_mb} Мбайт"

        else: # arbitrary_mb
            file_mb = random.choice(FILES_MB_ARBITRARY)
            total_mb = card_gb * 1024
            if file_mb > total_mb:
                continue
            count = total_mb // file_mb
            file_size_str = f"{file_mb} Мбайт"

        card_size_str = f"{card_gb} Гбайт"

        prompt = template.format(
            file_type=file_type,
            file_size_str=file_size_str,
            media=media,
            card_size_str=card_size_str
        )

        return {
            "task": prompt,
            "variants": None,
            "answer": str(count)
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--meta":
            print(json.dumps(META, ensure_ascii=False))
        elif sys.argv[1] == "--generate":
            print(json.dumps(generate(), ensure_ascii=False))