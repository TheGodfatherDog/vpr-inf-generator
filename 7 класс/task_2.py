import sys
import json
import random
import os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 2,
    "title": "Файловая система (пути к файлам и каталогам)",
    "has_variants": True
}

ТЕМАТИЧЕСКИЕ_ПАПКИ = {
    "учеба": [
        "Учеба", "Математика", "Информатика", "Физика", "Химия", "Биология",
        "География", "Литература", "История", "7_класс", "ГИА", "ОГЭ",
        "Задания", "Оценки", "Контрольные", "Рефераты", "Таблицы", "Презентации"
    ],
    "фото": [
        "Фотографии", "2023", "2024", "Лето", "Зима", "Весна", "Осень",
        "Байкал", "Путешествия", "Семья", "Природа", "Пейзажи", "Праздники", "Экскурсии"
    ],
    "документы": [
        "Документы", "Проекты", "Отчеты", "Договоры", "Срочные", "Архив",
        "Черновики", "Сданные", "Работа", "Готово", "Материалы"
    ],
    "музыка": [
        "Музыка", "Хиты", "Рок", "Классика", "Ретро", "Любимое",
        "Сборники", "Популярное", "Альбомы", "Песни"
    ]
}

ФАЙЛЫ = [
    "Реферат.docx", "Доклад.doc", "Презентация.pptx", "Таблица.xlsx",
    "Сочинение.docx", "Лабораторная.pdf", "Фото.jpg", "Рисунок.png",
    "Песня.mp3", "Программа.pas", "Код.py", "Заметки.txt", "График.xls"
]

ДИСКИ = ["C:", "D:"]

def generate_navigation_forward():
    theme = random.choice(list(ТЕМАТИЧЕСКИЕ_ПАПКИ.keys()))
    folders = random.sample(ТЕМАТИЧЕСКИЕ_ПАПКИ[theme], 6)
    disk = random.choice(ДИСКИ)

    initial_stack = [disk, folders[0], folders[1], folders[2]]
    initial_path = "\\".join(initial_stack)

    up_steps = random.choice([1, 2])
    current_stack = initial_stack[:-up_steps]

    down_folder1 = folders[3]
    current_stack.append(down_folder1)

    down_folder2 = folders[4]
    current_stack.append(down_folder2)

    correct_path = "\\".join(current_stack)
    up_text = "на один уровень вверх" if up_steps == 1 else "на два уровня вверх"
    task_text = (
        f"Пользователь работал с каталогом {initial_path}.\n"
        f"Сначала он поднялся {up_text}, затем спустился в каталог {down_folder1}, "
        f"после чего спустился в каталог {down_folder2}.\n"
        f"Укажите полный путь каталога, в котором оказался пользователь:"
    )

    distractors = [
        "\\".join(initial_stack + [down_folder1, down_folder2]),
        f"{disk}\\{down_folder1}\\{down_folder2}",
        "\\".join(initial_stack[:-up_steps] + [down_folder2, down_folder1])
    ]

    return task_text, correct_path, distractors

def generate_navigation_backward():
    theme = random.choice(list(ТЕМАТИЧЕСКИЕ_ПАПКИ.keys()))
    folders = random.sample(ТЕМАТИЧЕСКИЕ_ПАПКИ[theme], 6)
    disk = random.choice(ДИСКИ)

    start_folder = folders[0]
    common_folder = folders[1]
    end_sub1 = folders[2]
    end_sub2 = folders[3]

    final_path = f"{disk}\\{common_folder}\\{end_sub1}\\{end_sub2}"
    correct_start_path = f"{disk}\\{common_folder}\\{start_folder}"

    task_text = (
        f"Пользователь находился в каталоге {start_folder}.\n"
        f"Сначала он поднялся на один уровень вверх, затем спустился на один уровень вниз, "
        f"потом еще раз спустился на один уровень вниз.\n"
        f"В результате он оказался в каталоге {final_path}.\n"
        f"Укажите полный путь каталога, с которым пользователь начинал работу:"
    )

    distractors = [
        f"{disk}\\{start_folder}",
        f"{disk}\\{common_folder}\\{end_sub1}\\{start_folder}",
        f"{final_path}\\{start_folder}"
    ]

    return task_text, correct_start_path, distractors

def generate_file_move():
    theme = random.choice(list(ТЕМАТИЧЕСКИЕ_ПАПКИ.keys()))
    folders = random.sample(ТЕМАТИЧЕСКИЕ_ПАПКИ[theme], 4)
    file_name = random.choice(ФАЙЛЫ)
    disk = random.choice(ДИСКИ)

    parent_path = f"{disk}\\{folders[0]}\\{folders[1]}"
    old_file_path = f"{parent_path}\\{file_name}"
    new_subfolder = folders[2]
    new_file_path = f"{parent_path}\\{new_subfolder}\\{file_name}"

    is_after = random.choice([True, False])

    if is_after:
        task_text = (
            f"В некотором каталоге хранился файл {file_name}, имевший полное имя {old_file_path}.\n"
            f"В этом каталоге создали подкаталог {new_subfolder} и файл {file_name} переместили в созданный подкаталог.\n"
            f"Укажите полное имя этого файла после перемещения:"
        )
        correct_answer = new_file_path
        distractors = [
            f"{disk}\\{new_subfolder}\\{file_name}",
            f"{disk}\\{folders[0]}\\{new_subfolder}\\{file_name}",
            old_file_path
        ]
    else:
        task_text = (
            f"В некотором каталоге хранился файл {file_name}.\n"
            f"В этом каталоге создали подкаталог {new_subfolder} и файл {file_name} переместили в созданный подкаталог.\n"
            f"Полное имя файла стало {new_file_path}.\n"
            f"Укажите полное имя этого файла до перемещения:"
        )
        correct_answer = old_file_path
        distractors = [
            f"{disk}\\{folders[0]}\\{file_name}",
            f"{disk}\\{new_subfolder}\\{file_name}",
            new_file_path
        ]

    return task_text, correct_answer, distractors

def generate_folder_relocation():
    theme = random.choice(list(ТЕМАТИЧЕСКИЕ_ПАПКИ.keys()))
    folders = random.sample(ТЕМАТИЧЕСКИЕ_ПАПКИ[theme], 5)
    file_name = random.choice(ФАЙЛЫ)

    source_disk = "D:"
    target_disk = "C:"

    moved_folder = folders[2]
    old_full_path = f"{source_disk}\\{folders[0]}\\{folders[1]}\\{moved_folder}"
    destination_root_folder = folders[3]

    new_full_file_path = f"{target_disk}\\{destination_root_folder}\\{moved_folder}\\{file_name}"

    task_text = (
        f"Папку, полный путь до которой был {old_full_path}, "
        f"перенесли в папку {destination_root_folder}, расположенную в корне диска {target_disk}.\n"
        f"Укажите полный путь к файлу {file_name}, находившемуся в перемещённой папке {moved_folder}:"
    )

    correct_answer = new_full_file_path
    distractors = [
        f"{target_disk}\\{destination_root_folder}\\{file_name}",
        f"{target_disk}\\{moved_folder}\\{destination_root_folder}\\{file_name}",
        f"{source_disk}\\{destination_root_folder}\\{moved_folder}\\{file_name}"
    ]

    return task_text, correct_answer, distractors

def generate():
    random.seed(os.urandom(16))

    while True:
        generator_func = random.choice([
            generate_navigation_forward,
            generate_navigation_backward,
            generate_file_move,
            generate_folder_relocation
        ])

        task_text, correct_answer, raw_distractors = generator_func()

        unique_distractors = list({d.strip() for d in raw_distractors if d.strip() != correct_answer})

        if len(unique_distractors) < 3:
            continue

        selected_distractors = unique_distractors[:3]
        variants = selected_distractors + [correct_answer]

        if len(set(variants)) != 4:
            continue

        random.shuffle(variants)
        correct_number = str(variants.index(correct_answer) + 1)

        return {
            "task": task_text,
            "variants": variants,
            "variant_type": "numbers",
            "answer": correct_number
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--meta":
            print(json.dumps(META, ensure_ascii=False))
        elif sys.argv[1] == "--generate":
            print(json.dumps(generate(), ensure_ascii=False))