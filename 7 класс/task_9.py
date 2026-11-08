import sys
import json
import random
import os
import math

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

META = {
    "id": 9,
    "title": "Скорость передачи данных и пропускная способность канала",
    "has_variants": False
}

# =============================================================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ГРАММАТИКИ
# =============================================================================

def format_accusative_time(seconds):
    """
    Возвращает время в винительном падеже (без предлога).
    Идеально согласуется с:
    - 'заняла {time}' ('заняла 1 минуту', 'заняла 24 секунды', 'заняла 50 секунд')
    - 'составило {time}'
    - 'за {time}' ('за 1 минуту', 'за 24 секунды', 'за 50 секунд')
    """
    if seconds == 60:
        return "1 минуту"
    if seconds == 120:
        return "2 минуты"

    s_abs = abs(seconds) % 100
    s_last = s_abs % 10
    if 11 <= s_abs <= 19:
        return f"{seconds} секунд"
    if s_last == 1:
        return f"{seconds} секунду"
    if 2 <= s_last <= 4:
        return f"{seconds} секунды"
    return f"{seconds} секунд"

def get_connection_name():
    return random.choice([
        "ADSL-соединение",
        "WAP-соединение",
        "выделенный канал",
        "некоторое соединение",
        "высокоскоростное соединение"
    ])

# =============================================================================
# АРХЕТИП 1: БАЗОВЫЙ РАСЧЕТ (I = v * t) — 40%
# =============================================================================

TELECOM_SPEEDS = [
    64000, 128000, 256000, 512000,
    1024000, 2048000, 4096000, 5120000
]

def generate_archetype_basic():
    subtype = random.choice(["find_I", "find_v", "find_t"])
    v = random.choice(TELECOM_SPEEDS)

    # Шаг времени, при котором (v * t) делится на 8192 нацело
    gcd_val = math.gcd(v, 8192)
    t_step = 8192 // gcd_val
    t = t_step * random.randint(1, 8)

    # 1 минута (60 с) или 2 минуты (120 с), если кратны t_step
    if 60 % t_step == 0 and random.random() < 0.15:
        t = 60
    elif 120 % t_step == 0 and random.random() < 0.15:
        t = 120

    I_kb = (v * t) // 8192
    conn = get_connection_name()
    t_acc = format_accusative_time(t)

    if subtype == "find_I":
        phrasings = [
            f"Скорость передачи данных через {conn} равна {v} бит/c. Передача файла заняла {t_acc}. "
            "Определите размер файла в Кбайт. В ответе укажите одно число — размер файла в Кбайт.",

            f"Через {conn} со скоростью {v} бит/c за {t_acc} был передан файл. "
            "Определите размер файла в килобайтах."
        ]
        return random.choice(phrasings), str(I_kb)

    elif subtype == "find_v":
        phrasings = [
            f"Передача файла размером {I_kb} Кбайт через {conn} продолжалась {t_acc}. "
            "Определите скорость передачи данных в бит/c. В ответе укажите только число.",

            f"Файл объёмом {I_kb} Кбайт передавался ровно {t_acc}. "
            "Какова скорость передачи данных через это соединение в битах в секунду?"
        ]
        return random.choice(phrasings), str(v)

    else: # find_t
        phrasings = [
            f"Скорость передачи данных через {conn} равна {v} бит/c. Через данное соединение передают файл "
            f"размером {I_kb} Кбайт. Сколько секунд займёт передача файла?",

            f"Через соединение со скоростью {v} бит/c было передано {I_kb} Кбайт. "
            "Сколько секунд потребовалось для передачи файла?"
        ]
        return random.choice(phrasings), str(t)

# =============================================================================
# АРХЕТИП 2: РАЗНОСТЬ ВРЕМЕНИ (Δt = |t1 - t2|) — 25%
# =============================================================================

POWER2_SPEED_PAIRS = [
    (1024, 1536),
    (1024, 2048),
    (1024, 4096),
    (1536, 2048),
    (2048, 4096),
    (4096, 8192),
    (1024, 8192)
]

def generate_archetype_delta_time():
    v1, v2 = random.choice(POWER2_SPEED_PAIRS)
    if random.choice([True, False]):
        v1, v2 = v2, v1

    step1 = v1 // math.gcd(v1, 8192)
    step2 = v2 // math.gcd(v2, 8192)
    lcm_step = (step1 * step2) // math.gcd(step1, step2)

    I_kb = lcm_step * random.randint(1, 8)

    t1 = (I_kb * 8192) // v1
    t2 = (I_kb * 8192) // v2
    diff_t = abs(t1 - t2)

    if v2 > v1:
        prompt = (
            f"Файл размером {I_kb} Кбайт передается через некоторое соединение со скоростью {v1} бит в секунду. "
            f"Определите, на сколько секунд быстрее можно передать этот же файл через другое соединение со скоростью {v2} бит в секунду. "
            "В ответе укажите одно число — количество секунд."
        )
    else:
        prompt = (
            f"Файл размером {I_kb} Кбайт передается через некоторое соединение со скоростью {v1} бит в секунду. "
            f"Определите, на сколько секунд дольше будет передаваться этот же файл через другое соединение со скоростью {v2} бит в секунду. "
            "В ответе укажите одно число — количество секунд."
        )

    return prompt, str(diff_t)

# =============================================================================
# АРХЕТИП 3: ОДИНАКОВОЕ ВРЕМЯ (t = const) — 12%
# =============================================================================

def generate_archetype_same_time():
    v1, v2 = random.sample([512, 768, 1024, 1536, 2048, 3072, 4096], 2)
    t = random.choice([16, 24, 32, 48, 64])

    bits_file1 = t * v1
    bits_file2 = t * v2

    if bits_file1 % 8192 == 0:
        I1_val = bits_file1 // 8192
        I1_str = f"{I1_val} Кбайт"
    else:
        I1_val = bits_file1 // 8
        I1_str = f"{I1_val} байт"

    if bits_file2 % 8192 == 0 and random.choice([True, False]):
        ans = bits_file2 // 8192
        unit_target = "Кбайт"
    else:
        ans = bits_file2 // 8
        unit_target = "байтах"

    prompt = (
        f"Файл размером {I1_str} передается через некоторое соединение со скоростью {v1} бит в секунду. "
        f"Определите размер файла (в {unit_target}), который можно передать за то же время через другое соединение со скоростью {v2} бит в секунду. "
        "В ответе укажите одно число."
    )

    return prompt, str(ans)

# =============================================================================
# АРХЕТИП 4: ОДНО СОЕДИНЕНИЕ, РАЗНЫЕ ФАЙЛЫ (v = const) — 12%
# =============================================================================

def generate_archetype_proportions():
    subtype = random.choice(["find_I2", "find_t2"])

    if subtype == "find_I2":
        ratio = random.choice([2, 3, 4, 5])
        I2 = random.randint(2, 20) * 4
        I1 = I2 * ratio
        t2 = random.randint(10, 60)
        t1 = t2 * ratio

        t2_acc = format_accusative_time(t2)
        t1_acc = format_accusative_time(t1)

        prompt = (
            f"Передача файла размером {I1} Кбайт через некоторое соединение заняла {t1_acc}. "
            f"Определите размер файла (в Кбайт), передаваемого через это же соединение, если время его передачи составило {t2_acc}. "
            "В ответе укажите одно число — размер файла в Кбайт."
        )
        return prompt, str(I2)

    else: # find_t2
        # Дробные килобайты согласованы: "1,5 Кбайта", "1,25 Кбайта"
        preset = random.choice([
            (1536, "1,5 Кбайта", 512, "512 байт", 3),
            (1280, "1,25 Кбайта", 256, "256 байт", 5),
            (2048, "2 Кбайта", 512, "512 байт", 4),
            (3072, "3 Кбайта", 1024, "1024 байта", 3)
        ])
        bytes1, str1, bytes2, str2, ratio = preset
        t2 = random.randint(15, 80)
        t1 = t2 * ratio

        prompt = (
            f"Файл размером {str1} передается через некоторое соединение за {format_accusative_time(t1)}. "
            f"Сколько секунд будет передаваться файл размером {str2} через это же соединение? "
            "В ответе укажите одно число — длительность передачи в секундах."
        )
        return prompt, str(t2)

# =============================================================================
# АРХЕТИП 5: ОДИН ФАЙЛ, РАЗНЫЕ СОЕДИНЕНИЯ (I = const) — 11%
# =============================================================================

def generate_archetype_same_file():
    presets = [
        (5120, 24, 8192, 15),
        (4096, 30, 6144, 20),
        (2048, 45, 3072, 30),
        (3072, 20, 2048, 30),
        (10240, 18, 6144, 30),
        (1536, 40, 2048, 30)
    ]
    v1, t1, v2, t2 = random.choice(presets)

    t1_acc = format_accusative_time(t1)
    t2_acc = format_accusative_time(t2)

    ask_speed = random.choice([True, False])

    if ask_speed:
        prompt = (
            f"Через некоторое соединение со скоростью {v1} бит в секунду за {t1_acc} передается файл. "
            f"Определите скорость соединения (в битах в секунду), через которое этот же файл будет передаваться за {t2_acc}. "
            "В ответе укажите только число."
        )
        return prompt, str(v2)
    else:
        prompt = (
            f"Файл передается через соединение со скоростью {v1} бит в секунду за {t1_acc}. "
            f"Сколько секунд потребуется для передачи этого же файла через другое соединение со скоростью {v2} бит в секунду? "
            "В ответе укажите только число."
        )
        return prompt, str(t2)

# =============================================================================
# ТОЧКА ВХОДА ГЕНЕРАТОРА
# =============================================================================

def generate():
    random.seed(os.urandom(16))

    archetype = random.choices(
        ["basic", "delta_time", "same_time", "proportions", "same_file"],
        weights=[0.40, 0.25, 0.12, 0.12, 0.11],
        k=1
    )[0]

    if archetype == "basic":
        prompt, answer = generate_archetype_basic()
    elif archetype == "delta_time":
        prompt, answer = generate_archetype_delta_time()
    elif archetype == "same_time":
        prompt, answer = generate_archetype_same_time()
    elif archetype == "proportions":
        prompt, answer = generate_archetype_proportions()
    else:
        prompt, answer = generate_archetype_same_file()

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