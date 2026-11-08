#!/bin/bash
cd "$(dirname "$0")"

echo "=== Генератор заданий по Информатике ==="

if ! command -v node >/dev/null 2>&1; then
    echo "[ERROR] Node.js не установлен! Скачайте его с https://nodejs.org/"
    read -p "Нажмите Enter для выхода..."
    exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
    echo "[ERROR] Python 3 не установлен! Скачайте его с https://www.python.org/"
    read -p "Нажмите Enter для выхода..."
    exit 1
fi

VENV_DIR="venv"
if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "[INFO] Создаю виртуальное окружение Python ($VENV_DIR)..."
    python3 -m venv "$VENV_DIR"
fi

if [ ! -f "package.json" ]; then
    echo "[INFO] Инициализация Node.js проекта..."
    echo '{"name": "task-generator", "version": "1.0.0", "private": true}' > package.json
fi

if [ ! -d "node_modules/express" ]; then
    echo "[INFO] Установка зависимости express..."
    npm install express --no-fund --no-audit --silent
fi

echo "[INFO] Запуск сервера на http://localhost:3000 ..."
(sleep 1 && open "http://localhost:3000") &
node app.js