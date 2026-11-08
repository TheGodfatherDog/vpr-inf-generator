@echo off
chcp 65001 >nul
cd /d "%~dp0"
title Генератор заданий по Информатике

echo [INFO] Проверка наличия Node.js и Python...

where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js не установлен! Скачайте его с https://nodejs.org/
    pause
    exit /b 1
)

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python не установлен! Скачайте его с https://www.python.org/
    pause
    exit /b 1
)

set "VENV_DIR=venv"
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [INFO] Создаю виртуальное окружение Python: %VENV_DIR% ...
    python -m venv "%VENV_DIR%"
)

if not exist "package.json" (
    echo [INFO] Инициализация Node.js проекта...
    echo {"name": "task-generator", "version": "1.0.0", "private": true}> package.json
)

if not exist "node_modules\express" (
    echo [INFO] Установка зависимости express...
    call npm install express --no-fund --no-audit --silent
)

echo [INFO] Запуск сервера на http://localhost:3000 ...
start "" "http://localhost:3000"
node app.js

pause