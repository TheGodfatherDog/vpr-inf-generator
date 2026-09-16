@echo off
title Генератор заданий по Информатике
chcp 65001 > nul

echo [INFO] Проверка наличия Node.js...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js не установлен! Пожалуйста, скачайте его с https://nodejs.org/ и установите.
    pause
    exit /b
)

set VENV_DIR=venv

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [INFO] Создаю виртуальное окружение Python %VENV_DIR%...
    python -m venv %VENV_DIR%
)

if not exist "package.json" (
    echo [INFO] Инициализация Node.js проекта...
    echo {"name": "task-generator", "version": "1.0.0", "private": true} > package.json
)

echo [INFO] Установка зависимостей (express, docx)...
call npm install express docx --no-fund --silent

echo [INFO] Запуск приложения...
start http://localhost:3000
node app.js

pause