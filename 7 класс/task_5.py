import sys
import json
import random
import os
import itertools

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 5,
    "title": "Логические задачи на соответствие",
    "has_variants": False
}

MALE_PEOPLE = [
    ("А", "Артём", "Артёмом", "Антонов", "Антоновым"),
    ("Б", "Борис", "Борисом", "Белов", "Беловым"),
    ("В", "Виктор", "Виктором", "Воронов", "Вороновым"),
    ("Г", "Георгий", "Георгием", "Громов", "Громовым"),
    ("Д", "Дмитрий", "Дмитрием", "Дмитриев", "Дмитриевым"),
    ("И", "Иван", "Иваном", "Иванов", "Ивановым"),
    ("К", "Кирилл", "Кириллом", "Ковалёв", "Ковалёвым"),
    ("М", "Михаил", "Михаилом", "Михайлов", "Михайловым"),
    ("Н", "Николай", "Николаем", "Никифоров", "Никифоровым"),
    ("О", "Олег", "Олегом", "Орлов", "Орловым"),
    ("П", "Пётр", "Петром", "Петров", "Петровым"),
    ("Р", "Роман", "Романом", "Романов", "Романовым"),
    ("С", "Сергей", "Сергеем", "Сидоров", "Сидоровым"),
    ("Т", "Тимур", "Тимуром", "Тимофеев", "Тимофеевым"),
    ("Ф", "Фёдор", "Фёдором", "Фёдоров", "Фёдоровым")
]

FEMALE_PEOPLE = [
    ("А", "Анна", "Анной", "Андреева", "Андреевой"),
    ("В", "Вера", "Верой", "Васильева", "Васильевой"),
    ("Д", "Дарья", "Дарьей", "Дмитриева", "Дмитриевой"),
    ("Е", "Екатерина", "Екатериной", "Егорова", "Егоровой"),
    ("З", "Зоя", "Зоей", "Зайцева", "Зайцевой"),
    ("И", "Ирина", "Ириной", "Иванова", "Ивановой"),
    ("К", "Ксения", "Ксенией", "Крылова", "Крыловой"),
    ("Л", "Лидия", "Лидией", "Лебедева", "Лебедевой"),
    ("М", "Марина", "Мариной", "Миронова", "Мироновой"),
    ("Н", "Наталья", "Натальей", "Николаева", "Николаевой"),
    ("О", "Ольга", "Ольгой", "Орлова", "Орловой"),
    ("С", "Светлана", "Светланой", "Сергеева", "Сергеевой"),
    ("Т", "Татьяна", "Татьяной", "Тихонова", "Тихоновой"),
    ("Ю", "Юлия", "Юлией", "Юдина", "Юдиной")
]

def generate_three_persons():
    is_male = random.choice([True, False])
    source_pool = MALE_PEOPLE if is_male else FEMALE_PEOPLE
    role_word = "мальчика" if is_male else "девушки"
    roles_title = "мальчиков" if is_male else "девушек"

    selected_triplet = random.sample(source_pool, 3)
    letters = ["А", "Б", "В"]

    names_nom = [p[1] for p in selected_triplet]
    names_ins = [p[2] for p in selected_triplet]
    name_initials = [p[0] for p in selected_triplet]

    surname_indices = list(range(3))
    random.shuffle(surname_indices)

    surnames_nom = [selected_triplet[idx][3] for idx in surname_indices]
    surnames_ins = [selected_triplet[idx][4] for idx in surname_indices]
    surname_initials = [selected_triplet[idx][0] for idx in surname_indices]

    valid_pairs = [
        (i, j)
        for i in range(3)
        for j in range(3)
        if name_initials[i] != surname_initials[j]
    ]
    random.shuffle(valid_pairs)

    for person_idx, surname_idx in valid_pairs:
        valid_solutions = []
        for perm in itertools.permutations(range(3)):
            if any(name_initials[k] == surname_initials[perm[k]] for k in range(3)):
                continue
            if perm[person_idx] == surname_idx:
                continue
            valid_solutions.append(perm)

        if len(valid_solutions) == 1:
            single_solution = valid_solutions[0]
            answer_code = "".join([str(single_solution[k] + 1) for k in range(3)])

            verb = "заметил" if is_male else "заметила"
            pronoun = "ни у одного из них" if is_male else "ни у одной из них"

            if random.choice([True, False]):
                clue_phrase = (
                    f"В разговоре с {names_ins[person_idx]} {surnames_nom[surname_idx]} {verb}, "
                    f"что {pronoun} первая буква своего имени и первая буква своей фамилии не совпадают."
                )
            else:
                clue_phrase = (
                    f"{names_nom[person_idx]} во время беседы с {surnames_ins[surname_idx]} {verb}, "
                    f"что {pronoun} первая буква своего имени и первая буква своей фамилии не совпадают."
                )

            names_line = "   ".join([f"{letters[k]}) {names_nom[k]}" for k in range(3)])
            surnames_line = "   ".join([f"{k + 1}) {surnames_nom[k]}" for k in range(3)])

            # Объединено в одну строку для экономии высоты
            prompt_text = (
                f"На встречу пришли три {role_word}: {', '.join(names_nom)}. "
                f"Фамилии {roles_title} — {', '.join(surnames_nom)}. {clue_phrase} "
                "Соотнесите имена и фамилии.\n"
                f"ИМЕНА: {names_line}\n"
                f"ФАМИЛИИ: {surnames_line}\n"
                "Запишите в таблицу выбранные цифры под соответствующими буквами:"
            )

            return prompt_text, letters, answer_code

    return None

def generate_four_persons():
    is_male = random.choice([True, False])
    source_pool = MALE_PEOPLE if is_male else FEMALE_PEOPLE
    role_word = "мальчика" if is_male else "девочки"
    roles_title = "мальчиков" if is_male else "девочек"

    selected_quad = random.sample(source_pool, 4)
    letters = ["А", "Б", "В", "Г"]

    names_nom = [p[1] for p in selected_quad]
    name_initials = [p[0] for p in selected_quad]

    surname_indices = list(range(4))
    random.shuffle(surname_indices)

    surnames_nom = [selected_quad[idx][3] for idx in surname_indices]
    surname_initials = [selected_quad[idx][0] for idx in surname_indices]

    contexts = [
        ("живут в комнате №1", "в комнате №2"),
        ("сидят за первым столом", "за вторым столом"),
        ("поехали на первом автобусе", "на втором автобусе")
    ]
    clue_context = random.choice(contexts)

    index_permutations = list(itertools.permutations(range(4)))
    random.shuffle(index_permutations)

    for a, b, c, d in index_permutations:
        if name_initials[a] == surname_initials[b] or name_initials[c] == surname_initials[d]:
            continue

        valid_solutions = []
        for perm in itertools.permutations(range(4)):
            if any(name_initials[k] == surname_initials[perm[k]] for k in range(4)):
                continue

            holder_b = perm.index(b)
            holder_d = perm.index(d)

            pair1 = {a, holder_b}
            pair2 = {c, holder_d}

            if len(pair1) == 2 and len(pair2) == 2 and pair1.isdisjoint(pair2):
                valid_solutions.append(perm)

        if len(valid_solutions) == 1:
            single_solution = valid_solutions[0]
            answer_code = "".join([str(single_solution[k] + 1) for k in range(4)])

            names_line = "   ".join([f"{letters[k]}) {names_nom[k]}" for k in range(4)])
            surnames_line = "   ".join([f"{k + 1}) {surnames_nom[k]}" for k in range(4)])

            clue_phrase = (
                f"{names_nom[a]} и {surnames_nom[b]} {clue_context[0]}, "
                f"а {names_nom[c]} и {surnames_nom[d]} — {clue_context[1]}."
            )

            prompt_text = (
                f"На встрече собрались четыре {role_word}: {', '.join(names_nom)}. "
                f"Фамилии {roles_title} — {', '.join(surnames_nom)}. "
                f"Известно, что ни у кого имя и фамилия не начинаются на одну букву. "
                f"{clue_phrase} Соотнесите имена и фамилии.\n"
                f"ИМЕНА: {names_line}\n"
                f"ФАМИЛИИ: {surnames_line}\n"
                "Запишите в таблицу выбранные цифры под соответствующими буквами:"
            )

            return prompt_text, letters, answer_code

    return None

def generate():
    random.seed(os.urandom(16))

    while True:
        generator_func = random.choice([generate_three_persons, generate_four_persons])
        result = generator_func()

        if result is None:
            continue

        task_prompt, table_letters, answer_code = result

        return {
            "task": task_prompt,
            "variants": None,
            "answer_table": table_letters,
            "answer": answer_code
        }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--meta":
            print(json.dumps(META, ensure_ascii=False))
        elif sys.argv[1] == "--generate":
            print(json.dumps(generate(), ensure_ascii=False))