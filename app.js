/**
 * =============================================================================
 * СИСТЕМА ГЕНЕРАЦИИ И ВЕРСТКИ ИНДИВИДУАЛЬНЫХ ВАРИАНТОВ (app.js)
 * =============================================================================
 * 
 * ПОЛНАЯ ЧИСТАЯ ВЕРСИЯ:
 * 1. ЧИСТЫЕ ПУСТЫЕ ЗОНЫ: убраны все окантовки и надписи "[Свободно]" / "[Черновик]".
 *    Пустые колонки и обороты остаются идеально чистыми белыми листами.
 * 2. ТАБЛИЦЫ В ЗАДАНИЯХ 3, 5, 6: идут сразу за текстом в той же строке
 *    (inline-table) и переносятся только если не помещаются по ширине.
 * 3. ВАРИАНТЫ В ЗАДАНИЯХ 10 И 11: выводятся друг за другом в одну строку
 *    с полем ответа, экономя место.
 * 4. 100% СОХРАННОСТЬ ЗАДАЧ: замер по реальному DOM предотвращает обрезку и потери.
 * 5. ВЕКТОРНЫЙ PDF И ПЕЧАТЬ: экспорт файла без сбоев кодировки (RFC 6266).
 * =============================================================================
 */

const express = require('express');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { execFile, execSync } = require('child_process');

const app = express();
const PORT = 3000;

app.use(express.json({ limit: '50mb' }));
const PYTHON_CMD = path.join(__dirname, 'venv', 'Scripts', 'python.exe');

// Поиск системного браузера Chromium (Edge / Chrome)
function getSystemBrowserPath() {
    const candidates = [
        path.join(process.env['ProgramFiles(x86)'] || 'C:\\Program Files (x86)', 'Microsoft\\Edge\\Application\\msedge.exe'),
        path.join(process.env['ProgramFiles'] || 'C:\\Program Files', 'Microsoft\\Edge\\Application\\msedge.exe'),
        path.join(process.env['ProgramFiles'] || 'C:\\Program Files', 'Google\\Chrome\\Application\\chrome.exe'),
        path.join(process.env['ProgramFiles(x86)'] || 'C:\\Program Files (x86)', 'Google\\Chrome\\Application\\chrome.exe'),
        path.join(process.env['LocalAppData'] || '', 'Microsoft\\Edge\\Application\\msedge.exe'),
        path.join(process.env['LocalAppData'] || '', 'Google\\Chrome\\Application\\chrome.exe')
    ];
    for (const p of candidates) {
        if (fs.existsSync(p)) return p;
    }
    return null;
}

function runPython(filePath, arg) {
    return execSync(`"${PYTHON_CMD}" "${filePath}" ${arg}`, {
        encoding: 'utf-8',
        env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
    }).toString().trim();
}

function runPythonAsync(filePath, arg) {
    return new Promise((resolve, reject) => {
        execFile(PYTHON_CMD, [filePath, arg], {
            encoding: 'utf-8',
            env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
        }, (error, stdout, stderr) => {
            if (error) reject(error);
            else resolve(stdout.trim());
        });
    });
}

async function mapConcurrent(items, concurrencyLimit, fn) {
    const results = new Array(items.length);
    let currentIndex = 0;

    const workers = new Array(concurrencyLimit).fill(0).map(async () => {
        while (currentIndex < items.length) {
            const index = currentIndex++;
            results[index] = await fn(items[index], index);
        }
    });

    await Promise.all(workers);
    return results;
}

function getCircledNumber(num) {
    const circled = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩", "⑪", "⑫", "⑬", "⑭", "⑮", "⑯", "⑰", "⑱", "⑲", "⑳", "㉑", "㉒", "㉓", "㉔", "㉕", "㉖", "㉗", "㉘", "㉙", "㉚"];
    return (num >= 1 && num <= circled.length) ? circled[num - 1] : `(${num})`;
}

// =============================================================================
// HTML ГЛАВНОЙ СТРАНИЦЫ
// =============================================================================
const MAIN_HTML = `
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Генератор индивидуальных вариантов</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: #121212; 
            color: #e0e0e0; 
            margin: 0; 
            padding: 30px 20px; 
        }
        .container { 
            max-width: 980px; 
            margin: 0 auto; 
            background: #1e1e1e; 
            padding: 30px; 
            border-radius: 12px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.5); 
        }
        h2 { margin-top: 0; color: #ffffff; border-bottom: 1px solid #333; padding-bottom: 15px; }
        .grid { display: flex; gap: 30px; margin-top: 20px; }
        .col { flex: 1; display: flex; flex-direction: column; }
        
        label { margin-bottom: 8px; font-weight: 500; color: #bbbbbb; display: flex; justify-content: space-between; }
        textarea, input[type="text"], select { 
            width: 100%; 
            padding: 12px; 
            margin-bottom: 18px; 
            box-sizing: border-box; 
            background: #2d2d2d; 
            border: 1px solid #444; 
            color: #ffffff; 
            border-radius: 6px; 
            font-size: 14px; 
        }
        textarea:focus, input:focus, select:focus { outline: none; border-color: #007bff; }
        textarea { height: 180px; resize: vertical; line-height: 1.5; }
        
        .btn-group { display: flex; gap: 10px; margin-bottom: 15px; }
        button { 
            background: #007bff; 
            color: white; 
            border: none; 
            padding: 10px 14px; 
            border-radius: 6px; 
            cursor: pointer; 
            font-size: 13px; 
            font-weight: 600; 
            transition: 0.2s; 
        }
        button:hover { background: #0056b3; }
        
        .btn-secondary { background: #383838; flex: 1; }
        .btn-secondary:hover { background: #4a4a4a; }
        .btn-clear { background: #661a1a; }
        .btn-clear:hover { background: #8a2222; }
        .btn-main { background: #28a745; font-size: 16px; padding: 15px; width: 100%; margin-top: auto; }
        .btn-main:hover { background: #218838; }

        .task-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
        .task-actions { display: flex; gap: 8px; }
        .task-actions button { padding: 4px 10px; font-size: 11px; background: #333; }
        .task-actions button:hover { background: #444; }

        .task-list { 
            flex-grow: 1; 
            max-height: 250px; 
            overflow-y: auto; 
            background: #252525; 
            padding: 15px; 
            border: 1px solid #444; 
            border-radius: 6px; 
            margin-bottom: 15px; 
        }
        .task-item { margin-bottom: 10px; display: flex; align-items: center; gap: 10px; cursor: pointer; }
        .task-item input { margin: 0; width: 17px; height: 17px; cursor: pointer; }
        .checkbox-label { display: flex; align-items: center; gap: 10px; cursor: pointer; width: 100%; font-size: 13.5px; }
        
        .progress-box { display: none; margin-top: 15px; }
        .progress-bar-bg { width: 100%; height: 10px; background: #333; border-radius: 5px; overflow: hidden; }
        .progress-bar-fill { width: 0%; height: 100%; background: #28a745; transition: width 0.3s; }
        .progress-text { font-size: 12px; color: #aaa; margin-top: 5px; text-align: center; }

        #toastContainer { position: fixed; top: 20px; right: 20px; z-index: 99999; display: flex; flex-direction: column; gap: 10px; }
        .toast { 
            background: #282828; 
            color: #fff; 
            padding: 14px 20px; 
            border-radius: 8px; 
            box-shadow: 0 6px 20px rgba(0,0,0,0.6); 
            border-left: 5px solid #007bff; 
            font-size: 14px; 
            min-width: 250px; 
            animation: slideIn 0.3s ease; 
        }
        .toast.success { border-left-color: #28a745; }
        .toast.error { border-left-color: #dc3545; }
        @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
    </style>
</head>
<body>
    <div id="toastContainer"></div>
    <div class="container">
        <h2>🖨️ Генератор индивидуальных вариантов</h2>
        
        <label>Выберите параллель:</label>
        <select id="classSelector" onchange="loadTasks()">
            <option value="7 класс" selected>7 класс</option>
            <option value="8 класс">8 класс</option>
        </select>
        
        <div class="grid">
            <div class="col">
                <label>Название класса:</label>
                <input type="text" id="className" value="7-67">
                
                <label>
                    <span>Список учеников:</span>
                    <span id="studentCountBadge" style="color: #007bff; font-weight: bold;">3 уч.</span>
                </label>
                <textarea id="studentsList" oninput="updateStudentCount()">Храмцов Андрей&#10;Перхурова Екатерина&#10;Елькина Милина</textarea>
                
                <div class="btn-group">
                    <button class="btn-secondary" onclick="pasteStudents()">📋 Вставить</button>
                    <button class="btn-secondary btn-clear" onclick="clearStudents()">🗑 Очистить</button>
                </div>
            </div>
            
            <div class="col">
                <div class="task-header">
                    <label style="margin: 0;">Выбор заданий:</label>
                    <div class="task-actions">
                        <button type="button" onclick="selectAllTasks(true)">Выбрать все</button>
                        <button type="button" onclick="selectAllTasks(false)">Снять все</button>
                    </div>
                </div>
                
                <div id="tasksContainer" class="task-list">
                    <em>Загрузка заданий...</em>
                </div>

                <div class="progress-box" id="progressBox">
                    <div class="progress-bar-bg">
                        <div class="progress-bar-fill" id="progressBarFill"></div>
                    </div>
                    <div class="progress-text" id="progressText">Подготовка генерации...</div>
                </div>
                
                <button class="btn-main" id="generateBtn" onclick="startGeneration()">Сгенерировать вариант</button>
            </div>
        </div>
    </div>

    <script>
        function showToast(message, type = 'info') {
            const container = document.getElementById('toastContainer');
            const toast = document.createElement('div');
            toast.className = 'toast ' + type;
            toast.innerText = message;
            container.appendChild(toast);
            setTimeout(() => {
                toast.style.opacity = '0';
                setTimeout(() => toast.remove(), 300);
            }, 3500);
        }

        function updateStudentCount() {
            const students = document.getElementById('studentsList').value.split('\\n').filter(s => s.trim() !== '');
            document.getElementById('studentCountBadge').innerText = students.length + ' уч.';
        }

        async function loadTasks() {
            const classFolder = document.getElementById('classSelector').value;
            const container = document.getElementById('tasksContainer');
            container.innerHTML = "<em>Загрузка...</em>";
            
            try {
                const response = await fetch('/api/tasks?folder=' + encodeURIComponent(classFolder));
                const tasks = await response.json();
                
                if (tasks.length === 0) {
                    container.innerHTML = "<em>Задания не найдены.</em>";
                    return;
                }
                
                container.innerHTML = "";
                tasks.forEach(task => {
                    container.innerHTML += \`
                        <div class="task-item">
                            <label class="checkbox-label">
                                <input type="checkbox" class="task-checkbox" value="\${task.file}" checked>
                                \${task.id}. \${task.title}
                            </label>
                        </div>\`;
                });
            } catch (e) {
                container.innerHTML = "<em>Ошибка загрузки заданий.</em>";
                showToast("Не удалось загрузить задания", "error");
            }
        }

        function selectAllTasks(select) {
            document.querySelectorAll('.task-checkbox').forEach(cb => cb.checked = select);
        }

        async function pasteStudents() {
            try {
                const text = await navigator.clipboard.readText();
                const textarea = document.getElementById('studentsList');
                if (textarea.value.trim() !== '') {
                    textarea.value += '\\n' + text;
                } else {
                    textarea.value = text;
                }
                updateStudentCount();
                showToast("Список учеников вставлен", "success");
            } catch (err) {
                showToast("Разрешите браузеру доступ к буферу обмена", "error");
            }
        }

        function clearStudents() {
            document.getElementById('studentsList').value = '';
            updateStudentCount();
        }

        async function startGeneration() {
            const classFolder = document.getElementById('classSelector').value;
            const className = document.getElementById('className').value.trim() || 'Без_класса';
            const students = document.getElementById('studentsList').value.split('\\n').filter(s => s.trim() !== '');
            const selectedTasks = Array.from(document.querySelectorAll('.task-checkbox:checked')).map(cb => cb.value);
            
            if (students.length === 0) return showToast("Список учеников пуст!", "error");
            if (selectedTasks.length === 0) return showToast("Выберите хотя бы одно задание!", "error");

            const editorTab = window.open('about:blank', '_blank');
            editorTab.document.write('<title>Генерация...</title><body style="background:#1e1e1e;color:#fff;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;"><div style="text-align:center;"><h2>⏳ Параллельная генерация вариантов...</h2><p style="color:#aaa;">Идёт быстрый расчёт задач в многопоточном пуле.</p></div></body>');

            const btn = document.getElementById('generateBtn');
            const progressBox = document.getElementById('progressBox');
            const progressBar = document.getElementById('progressBarFill');
            const progressText = document.getElementById('progressText');

            btn.disabled = true;
            progressBox.style.display = 'block';
            progressBar.style.width = '35%';
            progressText.innerText = "Параллельная генерация в Python...";

            try {
                const response = await fetch('/api/generate-data', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ folder: classFolder, className, students, tasks: selectedTasks })
                });

                if (response.ok) {
                    progressBar.style.width = '90%';
                    progressText.innerText = "Формирование редактора...";
                    
                    const payloadData = await response.json();
                    localStorage.setItem('editor_data', JSON.stringify(payloadData));
                    editorTab.location.href = '/editor';
                    
                    progressBar.style.width = '100%';
                    setTimeout(() => { progressBox.style.display = 'none'; }, 500);
                    showToast("Варианты успешно сгенерированы!", "success");
                } else {
                    editorTab.close();
                    showToast("Ошибка генерации на сервере", "error");
                }
            } catch (e) {
                editorTab.close();
                showToast("Ошибка связи с сервером", "error");
            } finally {
                btn.disabled = false;
                progressBar.style.width = '0%';
            }
        }

        window.onload = () => {
            loadTasks();
            updateStudentCount();
        };
    </script>
</body>
</html>
`;

// =============================================================================
// HTML РЕДАКТОРА (A4 LANDSCAPE С ВСТРОЕННЫМИ ТАБЛИЦАМИ И ВАРИАНТАМИ В СТРОКУ)
// =============================================================================
const EDITOR_HTML = `
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Редактор вариантов (A4 Альбомный • 297×210 мм)</title>
    <style id="pageStyleBlock">
        :root {
            --page-padding: 5mm;
            --font-family: 'Courier New', Courier, monospace;
            --font-size: 11pt;
            --zoom-scale: 0.82;
        }

        * { box-sizing: border-box; }
        body { 
            margin: 0; 
            background: #202020; 
            color: #222; 
            font-family: 'Segoe UI', Tahoma, sans-serif; 
        }

        .toolbar { 
            position: sticky; 
            top: 0; 
            z-index: 1000; 
            background: #141414; 
            color: #eee; 
            padding: 8px 16px; 
            display: flex; 
            flex-wrap: wrap; 
            gap: 12px; 
            align-items: center; 
            box-shadow: 0 4px 15px rgba(0,0,0,0.7); 
            border-bottom: 1px solid #333; 
        }
        .toolbar-group { display: flex; align-items: center; gap: 6px; font-size: 13px; }
        .toolbar select, .toolbar button { 
            background: #2a2a2a; 
            color: #fff; 
            border: 1px solid #444; 
            padding: 6px 10px; 
            border-radius: 5px; 
            font-size: 13px; 
            cursor: pointer; 
        }
        .toolbar select:focus { outline: none; border-color: #007bff; }
        .toolbar button:hover { background: #383838; }
        .btn-primary { background: #28a745 !important; font-weight: bold; border: none !important; }
        .btn-primary:hover { background: #218838 !important; }
        .btn-print { background: #007bff !important; font-weight: bold; border: none !important; }
        .btn-print:hover { background: #0056b3 !important; }

        .viewport { 
            padding: 30px 10px; 
            display: flex; 
            flex-direction: column; 
            align-items: center; 
            gap: 25px; 
            min-height: calc(100vh - 60px); 
        }

        .sheet-container { 
            width: calc(297mm * var(--zoom-scale)); 
            height: calc(210mm * var(--zoom-scale)); 
            position: relative; 
            margin-bottom: 20px; 
        }

        .sheet-label { 
            position: absolute; 
            top: -22px; 
            left: 0; 
            color: #888; 
            font-size: 11.5px; 
            font-weight: 600; 
        }

        /* Лист A4 Альбомный: 297 x 210 мм */
        .page { 
            background: #ffffff; 
            width: 297mm; 
            height: 210mm; 
            max-width: 297mm; 
            max-height: 210mm; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.6); 
            padding: var(--page-padding); 
            position: absolute; 
            top: 0; 
            left: 0; 
            color: #000; 
            font-family: var(--font-family); 
            font-size: var(--font-size); 
            border-radius: 2px; 
            transform-origin: top left; 
            transform: scale(var(--zoom-scale)); 
            overflow: hidden; 
        }

        /* Информативный бейдж переполнения */
        .overflow-badge { 
            display: none; 
            position: absolute; 
            bottom: 4px; 
            right: 8px; 
            background: #dc3545; 
            color: #fff; 
            padding: 3px 10px; 
            border-radius: 4px; 
            font-size: 11px; 
            font-family: sans-serif; 
            font-weight: bold; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.5);
            z-index: 500;
            user-select: none; 
        }

        .two-columns-mode { 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            column-gap: calc(var(--page-padding) * 1.5); 
            height: 100%; 
        }

        /* Колонка — блочный контейнер без flex-shrink */
        .column-block { 
            position: relative; 
            height: 100%; 
            overflow: hidden; 
            box-sizing: border-box;
            display: block; 
        }

        .cut-divider { 
            position: absolute; 
            right: calc(-1 * (var(--page-padding) * 0.75)); 
            top: 0; 
            bottom: 0; 
            width: 1px; 
            border-right: 1.5px dashed #888; 
            user-select: none; 
        }
        .cut-icon { 
            position: absolute; 
            right: -8px; 
            top: 48%; 
            background: #fff; 
            padding: 2px; 
            font-size: 12px; 
            color: #666; 
            user-select: none; 
        }

        /* Шапка варианта */
        .variant-header { 
            display: flex; 
            justify-content: space-between; 
            align-items: baseline; 
            border-bottom: 1.5px solid #000; 
            padding-bottom: 2px; 
            margin-bottom: 4px; 
            font-weight: bold; 
        }
        .variant-left { font-size: 1.02em; }
        .variant-right { font-size: 0.88em; }

        /* Задание — неделимый монолит */
        .task-block { 
            margin-bottom: 4px; 
            page-break-inside: avoid; 
            break-inside: avoid; 
            box-sizing: border-box;
        }
        .task-title { font-weight: bold; margin-bottom: 2px; display: flex; gap: 6px; align-items: baseline; }
        .task-circle { font-size: 1.15em; line-height: 1; flex-shrink: 0; user-select: none; }
        .task-title-text { flex-grow: 1; outline: none; }
        .task-body { margin-left: 18px; line-height: 1.18; }
        .task-line { margin-bottom: 1px; outline: none; word-break: break-word; }

        /* Строка текста с пристыкованной таблицей (Задания 3, 5, 6) */
        .task-line-with-table {
            margin-bottom: 2px;
            line-height: 1.2;
        }
        .task-line-text {
            display: inline;
        }

        /* Варианты в одну строку (Задания 10, 11) */
        .variants-inline-flow {
            margin-top: 2px;
            margin-bottom: 2px;
            display: flex;
            flex-wrap: wrap;
            align-items: baseline;
            gap: 3px 12px;
            line-height: 1.22;
        }
        .variant-chip {
            white-space: nowrap;
            display: inline-flex;
            gap: 4px;
        }

        .last-variant-row { 
            display: flex; 
            justify-content: space-between; 
            align-items: baseline; 
            flex-wrap: wrap;
        }
        .inline-answer { 
            font-weight: bold; 
            white-space: nowrap; 
            margin-left: 10px; 
        }

        .answer-line { margin-top: 2px; font-weight: bold; outline: none; }
        
        /* Сетка таблицы ответов и кодов */
        .answer-grid { 
            border-collapse: collapse; 
            margin: 1px 0 1px 8px; 
            display: inline-table; 
            vertical-align: middle;
        }
        .answer-grid td { 
            border: 1px solid #000; 
            min-width: 22px; 
            height: 17px; 
            padding: 0 3px; 
            text-align: center; 
            vertical-align: middle; 
            font-size: 0.82em; 
            outline: none; 
        }
        .answer-grid tr:first-child td { font-weight: bold; background: #f2f2f2; }

        .modal-debug { 
            display: none; 
            position: fixed; 
            top: 50%; 
            left: 50%; 
            transform: translate(-50%, -50%); 
            background: #1e1e1e; 
            color: #fff; 
            padding: 25px; 
            border-radius: 8px; 
            box-shadow: 0 10px 40px rgba(0,0,0,0.8); 
            z-index: 2000; 
            max-width: 600px; 
            width: 90%; 
            max-height: 80vh; 
            overflow-y: auto; 
        }
        .modal-overlay { 
            display: none; 
            position: fixed; 
            top:0; left:0; right:0; bottom:0; 
            background: rgba(0,0,0,0.7); 
            z-index: 1999; 
        }
        .debug-table { width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 13px; }
        .debug-table th, .debug-table td { border: 1px solid #444; padding: 8px; text-align: left; }
        .debug-table th { background: #333; }

        .keys-table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.9em; }
        .keys-table th, .keys-table td { border: 1px solid #000; padding: 5px; text-align: center; outline: none; }
        .keys-table th { background: #f2f2f2; }
        .keys-table td:nth-child(2) { text-align: left; }

        @media print {
            body { 
                background: #fff !important; 
                margin: 0 !important; 
                padding: 0 !important; 
            }
            .toolbar, .modal-debug, .modal-overlay, .sheet-label, .overflow-badge { 
                display: none !important; 
            }
            .viewport { 
                padding: 0 !important; 
                gap: 0 !important; 
                margin: 0 !important; 
            }
            .sheet-container { 
                width: 297mm !important; 
                height: 210mm !important; 
                margin: 0 !important; 
                padding: 0 !important; 
                page-break-after: always !important; 
                break-after: page !important; 
            }
            .page { 
                box-shadow: none !important; 
                margin: 0 !important; 
                width: 297mm !important; 
                height: 210mm !important; 
                max-width: 297mm !important; 
                max-height: 210mm !important; 
                transform: none !important; 
            }
            @page { 
                size: 297mm 210mm; 
                margin: 0; 
            }
        }
    </style>
</head>
<body>
    <div class="toolbar">
        <div class="toolbar-group">
            <label>Шрифт:</label>
            <select id="fontFamilySelect" onchange="updateVisualStyles()">
                <option value="'Courier New', Courier, monospace" selected>Courier New</option>
                <option value="'Times New Roman', Times, serif">Times New Roman</option>
                <option value="Arial, sans-serif">Arial</option>
                <option value="Calibri, sans-serif">Calibri</option>
                <option value="'Segoe UI', sans-serif">Segoe UI</option>
            </select>
        </div>

        <div class="toolbar-group">
            <label>Кегль:</label>
            <select id="fontSizeSelect" onchange="updateVisualStyles()">
                <option value="8pt">8 пт</option>
                <option value="9pt">9 пт</option>
                <option value="10pt">10 пт</option>
                <option value="11pt" selected>11 пт (рекомендуемый)</option>
                <option value="12pt">12 пт</option>
                <option value="13pt">13 пт</option>
                <option value="14pt">14 пт</option>
                <option value="16pt">16 пт</option>
            </select>
        </div>

        <div class="toolbar-group">
            <label>Поля:</label>
            <select id="marginsSelect" onchange="updateVisualStyles()">
                <option value="5mm" selected>Сверхмалые (5 мм)</option>
                <option value="10mm">Узкие (10 мм)</option>
                <option value="15mm">Стандартные (15 мм)</option>
                <option value="20mm">Умеренные (20 мм)</option>
            </select>
        </div>

        <div class="toolbar-group">
            <label style="cursor: pointer; font-weight: bold; color: #5bc0de;">
                <input type="checkbox" id="twoColumnsCheckbox" onchange="handleModeChange()"> В два столбца (2 ученика на лист A4)
            </label>
        </div>

        <div class="toolbar-group" id="duplexGroup">
            <label style="cursor: pointer; font-weight: bold; color: #f0ad4e;">
                <input type="checkbox" id="duplexCheckbox" onchange="rebuildPages()"> 🖨️ Двусторонняя печать (карточки А5 ✂)
            </label>
        </div>

        <div class="toolbar-group" style="border-left: 1px solid #444; padding-left: 8px;">
            <label>Масштаб:</label>
            <select id="zoomSelect" onchange="applyZoom()">
                <option value="fit">По ширине</option>
                <option value="0.5">50%</option>
                <option value="0.65">65%</option>
                <option value="0.75">75%</option>
                <option value="0.82" selected>82%</option>
                <option value="1.0">100%</option>
            </select>
        </div>

        <div style="margin-left: auto; display: flex; gap: 8px;">
            <button onclick="showDebug(true)">🔍 Отладка</button>
            <button class="btn-print" onclick="window.print()">🖨️ Напечатать</button>
            <button class="btn-primary" onclick="exportToPdf()">💾 Скачать PDF</button>
        </div>
    </div>

    <div class="viewport" id="viewportArea"></div>

    <div class="modal-overlay" id="modalOverlay" onclick="showDebug(false)"></div>
    <div class="modal-debug" id="debugModal">
        <h3 style="margin-top:0;">⏱️ Время генерации вариантов</h3>
        <div id="debugContent"></div>
        <button style="margin-top: 15px;" onclick="showDebug(false)">Закрыть</button>
    </div>

    <script>
        let DATA = null;

        function getCircled(n) {
            const arr = ["①", "②", "③", "④", "⑤", "⑥", "⑦", "⑧", "⑨", "⑩", "⑪", "⑫", "⑬", "⑭", "⑮", "⑯", "⑰", "⑱", "⑲", "⑳", "㉑", "㉒", "㉓", "㉔", "㉕", "㉖", "㉗", "㉘", "㉙", "㉚"];
            return (n >= 1 && n <= arr.length) ? arr[n - 1] : '(' + n + ')';
        }

        function handleModeChange() {
            const isTwoCol = document.getElementById('twoColumnsCheckbox').checked;
            const duplexCb = document.getElementById('duplexCheckbox');
            if (!isTwoCol) {
                duplexCb.checked = false;
                duplexCb.disabled = true;
            } else {
                duplexCb.disabled = false;
            }
            rebuildPages();
        }

        function renderDocument() {
            const raw = localStorage.getItem('editor_data');
            if (!raw) {
                document.getElementById('viewportArea').innerHTML = "<h2 style='color:#fff;'>Данные не найдены. Вернитесь назад и запустите генерацию.</h2>";
                return;
            }
            DATA = JSON.parse(raw);
            rebuildPages();
        }

        // =====================================================================
        // ГЕНЕРАЦИЯ HTML ЗАДАНИЯ С КОМПАКТНЫМИ ТАБЛИЦАМИ И ВАРИАНТАМИ
        // =====================================================================
        function renderTaskHtml(t, taskNumber) {
            const circled = getCircled(taskNumber);
            const lines = t.task.split('\\n').map(l => l.trim()).filter(l => l.length > 0);
            const firstLine = lines[0] || '';
            const otherLines = lines.slice(1);

            let html = \`
                <div class="task-block">
                    <div class="task-title">
                        <span class="task-circle">\${circled}</span>
                        <span class="task-title-text">\${firstLine}</span>
                    </div>
                    <div class="task-body">
            \`;

            // Проверяем наличие таблицы в задании (Задания 3, 5, 6)
            const hasCodeTable = !!(t.code_table && t.code_table.headers && t.code_table.rows);
            const hasAnswerTable = !!(t.answer_table && Array.isArray(t.answer_table));

            // Формируем HTML таблицы, если она есть
            let tableHtml = '';
            if (hasCodeTable) {
                tableHtml = '<table class="answer-grid code-table"><tr>';
                t.code_table.headers.forEach(h => { tableHtml += \`<td>\${h}</td>\`; });
                html += '</tr>';
                t.code_table.rows.forEach(row => {
                    tableHtml += '<tr>';
                    row.forEach(val => { tableHtml += \`<td>\${val}</td>\`; });
                    tableHtml += '</tr>';
                });
                tableHtml += '</table>';
            } else if (hasAnswerTable) {
                tableHtml = '<table class="answer-grid"><tr>';
                t.answer_table.forEach(letter => { tableHtml += \`<td>\${letter}</td>\`; });
                tableHtml += '</tr><tr>';
                t.answer_table.forEach(() => { tableHtml += '<td>&nbsp;</td>'; });
                tableHtml += '</tr></table>';
            }

            // Выводим строки текста. Последнюю строку склеиваем с таблицей (inline-table)!
            if (hasCodeTable || hasAnswerTable) {
                const totalLines = otherLines.length;
                if (totalLines === 0) {
                    html += \`<div class="task-line-with-table">\${tableHtml}</div>\`;
                } else {
                    for (let i = 0; i < totalLines - 1; i++) {
                        html += \`<div class="task-line">\${otherLines[i]}</div>\`;
                    }
                    const lastLine = otherLines[totalLines - 1];
                    // Таблица идет СРАЗУ за текстом! Браузер перенесет её ТОЛЬКО если она не влезет в ширину строки!
                    html += \`
                        <div class="task-line-with-table">
                            <span class="task-line-text">\${lastLine}</span>
                            \${tableHtml}
                        </div>
                    \`;
                }
                html += '<div class="answer-line">Ответ: ___________</div>';
            }
            // Выводим варианты ответов
            else if (t.variants && Array.isArray(t.variants)) {
                otherLines.forEach(l => { html += \`<div class="task-line">\${l}</div>\`; });

                // Задания 10 и 11: варианты идут ДРУГ ЗА ДРУГОМ В ОДНУ СТРОКУ!
                const isInlineVariants = (taskNumber === 10 || taskNumber === 11 || t.variant_style === 'inline' || t.variants.every(v => String(v).length < 25 && !String(v).includes('\\\\')));

                if (isInlineVariants) {
                    html += '<div class="variants-inline-flow">';
                    t.variants.forEach((v, vIdx) => {
                        const label = (vIdx + 1) + ')';
                        html += \`<span class="variant-chip"><strong>\${label}</strong> \${v}</span>\`;
                    });
                    html += '<span class="inline-answer">Ответ: ___________</span>';
                    html += '</div>';
                } else {
                    // Задание 2: длинные пути остаются вертикальным списком
                    const totalV = t.variants.length;
                    t.variants.forEach((v, vIdx) => {
                        const label = (vIdx + 1) + ')';
                        if (vIdx === totalV - 1) {
                            html += \`
                                <div class="task-line last-variant-row">
                                    <div class="last-variant-content"><strong>\${label}</strong> \${v}</div>
                                    <div class="inline-answer">Ответ: ___________</div>
                                </div>
                            \`;
                        } else {
                            html += \`<div class="task-line"><strong>\${label}</strong> \${v}</div>\`;
                        }
                    });
                }
            } else {
                otherLines.forEach(l => { html += \`<div class="task-line">\${l}</div>\`; });
                html += '<div class="answer-line">Ответ: ___________</div>';
            }

            html += '</div></div>';
            return html;
        }

        // =====================================================================
        // СБОРКА СТРАНИЦ ДОКУМЕНТА (БЕЗ НАДПИСЕЙ И ОКАЙМЛЕНИЙ ПУСТЫХ ЗОН)
        // =====================================================================
        function rebuildPages() {
            const viewport = document.getElementById('viewportArea');
            viewport.innerHTML = '';

            const isTwoCol = document.getElementById('twoColumnsCheckbox').checked;
            const isDuplex = document.getElementById('duplexCheckbox').checked && isTwoCol;

            let sheetIndex = 1;

            // 1. Одноколоночный режим
            if (!isTwoCol) {
                DATA.variants.forEach((item, idx) => {
                    const container = document.createElement('div');
                    container.className = 'sheet-container';

                    const label = document.createElement('div');
                    label.className = 'sheet-label';
                    label.innerText = \`📄 Лист \${sheetIndex++} (A4 • Вариант \${idx + 1})\`;
                    container.appendChild(label);

                    const page = document.createElement('div');
                    page.className = 'page variant-card';
                    page.contentEditable = "true";

                    let html = \`
                        <div class="variant-header">
                            <div class="variant-left">Вариант \${idx + 1}</div>
                            <div class="variant-right">\${item.student} &nbsp;&nbsp;&nbsp;&nbsp; Класс: \${DATA.className}</div>
                        </div>
                    \`;
                    item.tasks.forEach((t, tIdx) => { html += renderTaskHtml(t, tIdx + 1); });
                    html += '<div class="overflow-badge"></div>';
                    page.innerHTML = html;

                    container.appendChild(page);
                    viewport.appendChild(container);
                });
            }
            // 2. Двухколоночный режим С ДВУСТОРОННЕЙ ПЕЧАТЬЮ (КАРТОЧКИ А5)
            else if (isDuplex) {
                for (let i = 0; i < DATA.variants.length; i += 2) {
                    const v1_idx = i;
                    const v2_idx = i + 1;
                    const item1 = DATA.variants[v1_idx];
                    const item2 = (v2_idx < DATA.variants.length) ? DATA.variants[v2_idx] : null;

                    const currentSheetNum = sheetIndex++;

                    // --- ЛИЦЕВАЯ СТОРОНА ЛИСТА ---
                    const frontContainer = document.createElement('div');
                    frontContainer.className = 'sheet-container';
                    const frontLabel = document.createElement('div');
                    frontLabel.className = 'sheet-label';
                    frontLabel.innerText = \`📄 Лист \${currentSheetNum} (ЛИЦО • ВАР \${v1_idx + 1} слева, ВАР \${item2 ? v2_idx + 1 : '—'} справа)\`;
                    frontContainer.appendChild(frontLabel);

                    const frontPage = document.createElement('div');
                    frontPage.className = 'page two-columns-mode';
                    frontPage.contentEditable = "true";

                    // Колонка 1 Лицо (Ученик 1)
                    const col1Front = document.createElement('div');
                    col1Front.className = 'column-block variant-card';
                    col1Front.innerHTML = \`
                        <div class="variant-header">
                            <div class="variant-left">Вариант \${v1_idx + 1}</div>
                            <div class="variant-right">\${item1.student} &nbsp;&nbsp;&nbsp;&nbsp; Класс: \${DATA.className}</div>
                        </div>
                    \`;
                    col1Front.innerHTML += '<div class="cut-divider"><span class="cut-icon">✂</span></div>';
                    frontPage.appendChild(col1Front);

                    // Колонка 2 Лицо (Ученик 2)
                    const col2Front = document.createElement('div');
                    col2Front.className = 'column-block variant-card';
                    if (item2) {
                        col2Front.innerHTML = \`
                            <div class="variant-header">
                                <div class="variant-left">Вариант \${v2_idx + 1}</div>
                                <div class="variant-right">\${item2.student} &nbsp;&nbsp;&nbsp;&nbsp; Класс: \${DATA.className}</div>
                            </div>
                        \`;
                    }
                    frontPage.appendChild(col2Front);

                    const frontBadge = document.createElement('div');
                    frontBadge.className = 'overflow-badge';
                    frontPage.appendChild(frontBadge);
                    frontContainer.appendChild(frontPage);
                    viewport.appendChild(frontContainer);

                    // --- ПРЯМОЙ ЖИВОЙ ЗАМЕР В КОЛОНКЕ ЛИЦА ---
                    const allowedHeightPx = col1Front.clientHeight;

                    const s1_backTasks = [];
                    let s1_overflowed = false;
                    item1.tasks.forEach((t, tIdx) => {
                        if (s1_overflowed) {
                            s1_backTasks.push({ task: t, origIdx: tIdx });
                            return;
                        }
                        const tHtml = renderTaskHtml(t, tIdx + 1);
                        const tempEl = document.createElement('div');
                        tempEl.innerHTML = tHtml;
                        const taskNode = tempEl.firstElementChild;
                        col1Front.appendChild(taskNode);

                        // Если добавление задачи вызвало переполнение 200 мм — вынимаем и на оборот!
                        if (col1Front.scrollHeight > allowedHeightPx) {
                            col1Front.removeChild(taskNode);
                            s1_overflowed = true;
                            s1_backTasks.push({ task: t, origIdx: tIdx });
                        }
                    });

                    const s2_backTasks = [];
                    if (item2) {
                        let s2_overflowed = false;
                        item2.tasks.forEach((t, tIdx) => {
                            if (s2_overflowed) {
                                s2_backTasks.push({ task: t, origIdx: tIdx });
                                return;
                            }
                            const tHtml = renderTaskHtml(t, tIdx + 1);
                            const tempEl = document.createElement('div');
                            tempEl.innerHTML = tHtml;
                            const taskNode = tempEl.firstElementChild;
                            col2Front.appendChild(taskNode);

                            if (col2Front.scrollHeight > allowedHeightPx) {
                                col2Front.removeChild(taskNode);
                                s2_overflowed = true;
                                s2_backTasks.push({ task: t, origIdx: tIdx });
                            }
                        });
                    }

                    // --- ОБОРОТНАЯ СТОРОНА ЛИСТА (ЗЕРКАЛЬНАЯ ИНВЕРСИЯ!) ---
                    const backContainer = document.createElement('div');
                    backContainer.className = 'sheet-container';
                    const backLabel = document.createElement('div');
                    backLabel.className = 'sheet-label';
                    backLabel.innerText = \`📄 Лист \${currentSheetNum} (ОБОРОТ • ВАР \${item2 ? v2_idx + 1 : '—'} слева, ВАР \${v1_idx + 1} справа • РАЗРЕЗ ✂)\`;
                    backContainer.appendChild(backLabel);

                    const backPage = document.createElement('div');
                    backPage.className = 'page two-columns-mode';
                    backPage.contentEditable = "true";

                    // Оборот Колонка 1 (СЛЕВА — Ученик 2)
                    const col1Back = document.createElement('div');
                    col1Back.className = 'column-block variant-card';
                    if (item2 && s2_backTasks.length > 0) {
                        s2_backTasks.forEach(item => {
                            col1Back.innerHTML += renderTaskHtml(item.task, item.origIdx + 1);
                        });
                    }
                    col1Back.innerHTML += '<div class="cut-divider"><span class="cut-icon">✂</span></div>';
                    backPage.appendChild(col1Back);

                    // Оборот Колонка 2 (СПРАВА — Ученик 1)
                    const col2Back = document.createElement('div');
                    col2Back.className = 'column-block variant-card';
                    if (s1_backTasks.length > 0) {
                        s1_backTasks.forEach(item => {
                            col2Back.innerHTML += renderTaskHtml(item.task, item.origIdx + 1);
                        });
                    }
                    backPage.appendChild(col2Back);

                    const backBadge = document.createElement('div');
                    backBadge.className = 'overflow-badge';
                    backPage.appendChild(backBadge);

                    backContainer.appendChild(backPage);
                    viewport.appendChild(backContainer);
                }
            }
            // 3. Двухколоночный односторонний режим
            else {
                for (let i = 0; i < DATA.variants.length; i += 2) {
                    const container = document.createElement('div');
                    container.className = 'sheet-container';

                    const v1 = i + 1;
                    const v2 = (i + 1 < DATA.variants.length) ? (i + 2) : null;
                    const desc = v2 ? \`Варианты \${v1} и \${v2}\` : \`Вариант \${v1}\`;

                    const label = document.createElement('div');
                    label.className = 'sheet-label';
                    label.innerText = \`📄 Лист \${sheetIndex++} (A4 • 2 столбца • \${desc})\`;
                    container.appendChild(label);

                    const page = document.createElement('div');
                    page.className = 'page two-columns-mode';
                    page.contentEditable = "true";

                    const col1 = document.createElement('div');
                    col1.className = 'column-block variant-card';
                    col1.innerHTML = \`
                        <div class="variant-header">
                            <div class="variant-left">Вариант \${v1}</div>
                            <div class="variant-right">\${DATA.variants[i].student} &nbsp;&nbsp;&nbsp;&nbsp; Класс: \${DATA.className}</div>
                        </div>
                    \`;
                    DATA.variants[i].tasks.forEach((t, tIdx) => { col1.innerHTML += renderTaskHtml(t, tIdx + 1); });
                    col1.innerHTML += '<div class="cut-divider"><span class="cut-icon">✂</span></div>';
                    page.appendChild(col1);

                    if (i + 1 < DATA.variants.length) {
                        const col2 = document.createElement('div');
                        col2.className = 'column-block variant-card';
                        col2.innerHTML = \`
                            <div class="variant-header">
                                <div class="variant-left">Вариант \${i + 2}</div>
                                <div class="variant-right">\${DATA.variants[i + 1].student} &nbsp;&nbsp;&nbsp;&nbsp; Класс: \${DATA.className}</div>
                            </div>
                        \`;
                        DATA.variants[i + 1].tasks.forEach((t, tIdx) => { col2.innerHTML += renderTaskHtml(t, tIdx + 1); });
                        page.appendChild(col2);
                    }

                    page.innerHTML += '<div class="overflow-badge"></div>';
                    container.appendChild(page);
                    viewport.appendChild(container);
                }
            }

            // ЛИСТ С КЛЮЧАМИ (ВСЕГДА НА ОТДЕЛЬНОМ ЛИСТЕ)
            const keyContainer = document.createElement('div');
            keyContainer.className = 'sheet-container';
            keyContainer.innerHTML = \`<div class="sheet-label">📄 Лист \${sheetIndex} (КЛЮЧИ И ОТВЕТЫ • Отдельный лист)</div>\`;
            const keysPage = document.createElement('div');
            keysPage.className = 'page keys-card';
            keysPage.contentEditable = "true";
            keysPage.innerHTML = generateKeysHtml();
            keyContainer.appendChild(keysPage);
            viewport.appendChild(keyContainer);

            updateVisualStyles();
            applyZoom();
            setTimeout(checkOverflows, 100);
        }

        function generateKeysHtml() {
            let html = \`
                <h2 class="keys-title" style="margin-top:0; border-bottom: 2px solid #000; padding-bottom: 5px; font-size: 1.15em;">
                    КЛЮЧИ И ОТВЕТЫ К ВАРИАНТАМ (Класс: \${DATA.className})
                </h2>
                <table class="keys-table">
                    <tr><th style="width:50px;">Вар.</th><th>Ученик</th>
            \`;

            const maxTasks = DATA.variants[0] ? DATA.variants[0].tasks.length : 0;
            for (let i = 0; i < maxTasks; i++) html += \`<th style="width:80px;">№\${i + 1}</th>\`;
            html += '</tr>';

            DATA.variants.forEach((v, idx) => {
                html += \`<tr><td>\${idx + 1}</td><td>\${v.student}</td>\`;
                v.tasks.forEach(t => { html += \`<td style="font-weight:bold;">\${t.answer || '—'}</td>\`; });
                html += '</tr>';
            });
            html += '</table>';
            return html;
        }

        function updateVisualStyles() {
            document.documentElement.style.setProperty('--font-family', document.getElementById('fontFamilySelect').value);
            document.documentElement.style.setProperty('--font-size', document.getElementById('fontSizeSelect').value);
            document.documentElement.style.setProperty('--page-padding', document.getElementById('marginsSelect').value);
            setTimeout(checkOverflows, 150);
        }

        function applyZoom() {
            const val = document.getElementById('zoomSelect').value;
            let scale = 0.82;
            if (val === 'fit') {
                scale = Math.min(1.0, Math.max(0.4, (window.innerWidth - 60) / ((297 / 25.4) * 96)));
            } else scale = parseFloat(val);
            document.documentElement.style.setProperty('--zoom-scale', scale);
        }

        // =====================================================================
        // ТОЧНЫЙ РАСЧЕТ ПЕРЕПОЛНЕНИЯ В МИЛЛИМЕТРАХ И СТРОКАХ
        // =====================================================================
        function checkOverflows() {
            const padVal = parseInt(document.getElementById('marginsSelect').value);
            const maxAllowedHeightPx = ((210 - (padVal * 2)) / 25.4) * 96;

            document.querySelectorAll('.page:not(.keys-card)').forEach(page => {
                const badge = page.querySelector('.overflow-badge');
                if (!badge) return;

                let maxExcessPx = 0;

                if (page.classList.contains('two-columns-mode')) {
                    const cols = page.querySelectorAll('.column-block');
                    cols.forEach(col => {
                        const excess = col.scrollHeight - col.clientHeight;
                        if (excess > maxExcessPx) maxExcessPx = excess;
                    });
                } else {
                    maxExcessPx = page.scrollHeight - page.clientHeight;
                }

                // Допуск в 3 пикселя на погрешность субпиксельного рендеринга
                if (maxExcessPx > 3) {
                    const excessMm = Math.round((maxExcessPx / 96) * 25.4);
                    const approxLines = Math.max(1, Math.ceil(excessMm / 4.8));
                    badge.style.display = 'block';
                    badge.innerHTML = \`⚠️ Не влезает: +\${excessMm} мм (~\${approxLines} стр.) — уменьшите кегль!\`;
                } else {
                    badge.style.display = 'none';
                }
            });
        }

        // Автопересчет при редактировании текста в браузере
        document.addEventListener('DOMContentLoaded', () => {
            const viewport = document.getElementById('viewportArea');
            if (viewport) {
                viewport.addEventListener('input', () => { checkOverflows(); });
            }
        });

        window.onresize = () => {
            if (document.getElementById('zoomSelect').value === 'fit') applyZoom();
        };

        function showDebug(show) {
            document.getElementById('modalOverlay').style.display = show ? 'block' : 'none';
            document.getElementById('debugModal').style.display = show ? 'block' : 'none';
            if (show && DATA && DATA.debug) {
                let html = \`<p><strong>Общее время генерации:</strong> \${DATA.debug.totalMs} мс (\${(DATA.debug.totalMs / 1000).toFixed(2)} сек)</p>\`;
                html += '<p style="color:#aaa;font-size:12px;">Параллельный пул Node.js.</p>';
                document.getElementById('debugContent').innerHTML = html;
            }
        }

        // =====================================================================
        // ЧЕСТНЫЙ ЭКСПОРТ В PDF (СКАЧИВАНИЕ ГОТОВОГО ФАЙЛА)
        // =====================================================================
        async function exportToPdf() {
            const btn = document.querySelector('.btn-primary');
            const orig = btn.innerText;
            btn.innerText = "⏳ Сборка PDF...";
            btn.disabled = true;

            try {
                const styles = document.getElementById('pageStyleBlock').innerHTML;
                const viewportHtml = document.getElementById('viewportArea').innerHTML;

                const res = await fetch('/api/export-pdf', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        className: DATA.className,
                        viewportHtml,
                        styles,
                        cssVariables: {
                            padding: document.getElementById('marginsSelect').value,
                            font: document.getElementById('fontFamilySelect').value,
                            fontSize: document.getElementById('fontSizeSelect').value
                        }
                    })
                });

                if (res.ok) {
                    const blob = await res.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = \`\${DATA.className}_Варианты.pdf\`;
                    a.click();
                    window.URL.revokeObjectURL(url);
                } else {
                    const err = await res.json();
                    alert(err.error || "Ошибка экспорта в PDF");
                }
            } catch (e) {
                alert("Ошибка связи с сервером при экспорте в PDF");
            } finally {
                btn.innerText = orig;
                btn.disabled = false;
            }
        }

        window.onload = renderDocument;
    </script>
</body>
</html>
`;

// =============================================================================
// РОУТЫ EXPRESS СЕРВЕРА
// =============================================================================

app.get('/', (req, res) => res.send(MAIN_HTML));
app.get('/editor', (req, res) => res.send(EDITOR_HTML));

app.get('/api/tasks', (req, res) => {
    const classFolder = req.query.folder;
    const folderPath = path.join(__dirname, classFolder);
    if (!fs.existsSync(folderPath)) fs.mkdirSync(folderPath, { recursive: true });
    
    let tasks = [];
    const files = fs.readdirSync(folderPath).filter(f => f.startsWith('task_') && f.endsWith('.py'));
    for (const file of files) {
        try {
            const stdout = runPython(path.join(folderPath, file), '--meta');
            const meta = JSON.parse(stdout);
            tasks.push({ file: file, id: meta.id || 999, title: meta.title || "Без названия" });
        } catch (e) {}
    }
    tasks.sort((a, b) => a.id - b.id);
    res.json(tasks);
});

app.post('/api/generate-data', async (req, res) => {
    const { folder, className, students, tasks } = req.body;
    const startTimeAll = Date.now();

    const jobs = [];
    for (let sIdx = 0; sIdx < students.length; sIdx++) {
        for (let tIdx = 0; tIdx < tasks.length; tIdx++) {
            jobs.push({ studentIndex: sIdx, taskIndex: tIdx, student: students[sIdx], taskFile: tasks[tIdx] });
        }
    }

    const cpuCount = os.cpus().length || 4;
    const CONCURRENCY = Math.max(4, Math.min(16, cpuCount * 2));

    const executionResults = await mapConcurrent(jobs, CONCURRENCY, async (job) => {
        const filePath = path.join(__dirname, folder, job.taskFile);
        try {
            const stdout = await runPythonAsync(filePath, '--generate');
            return { ...job, success: true, data: JSON.parse(stdout) };
        } catch (e) {
            return { ...job, success: false, data: { task: "Ошибка генерации", variants: null, answer: "—" } };
        }
    });

    const variantsData = [];
    for (let sIdx = 0; sIdx < students.length; sIdx++) {
        const student = students[sIdx];
        const studentTasks = executionResults
            .filter(r => r.studentIndex === sIdx)
            .sort((a, b) => a.taskIndex - b.taskIndex)
            .map(r => r.data);

        variantsData.push({ variantNum: sIdx + 1, student: students[sIdx], tasks: studentTasks });
    }

    res.json({ className, variants: variantsData, debug: { totalMs: Date.now() - startTimeAll } });
});

// =============================================================================
// РОУТ ЭКСПОРТА В ВЕКТОРНЫЙ PDF (RFC 6266 ЗАЩИТА ЗАГОЛОВКА, БЕЗ КРАХА)
// =============================================================================
app.post('/api/export-pdf', async (req, res) => {
    const { className, viewportHtml, styles, cssVariables } = req.body;
    const browserPath = getSystemBrowserPath();

    if (!browserPath) {
        return res.status(500).json({ 
            error: "Системный браузер Edge/Chrome не найден. Используйте кнопку '🖨️ Напечатать' -> 'Сохранить как PDF'." 
        });
    }

    const tempId = Date.now() + '_' + Math.random().toString(36).substring(2, 7);
    const tempHtmlPath = path.join(os.tmpdir(), `print_${tempId}.html`);
    const tempPdfPath = path.join(os.tmpdir(), `print_${tempId}.pdf`);

    const fullHtml = `
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <style>
        :root {
            --page-padding: ${cssVariables.padding};
            --font-family: ${cssVariables.font};
            --font-size: ${cssVariables.fontSize};
            --zoom-scale: 1.0;
        }
        ${styles}
        body { 
            background: #fff !important; 
            margin: 0 !important; 
            padding: 0 !important; 
        }
        .toolbar, .modal-debug, .modal-overlay, .sheet-label, .overflow-badge { 
            display: none !important; 
        }
        .viewport { 
            padding: 0 !important; 
            gap: 0 !important; 
            margin: 0 !important; 
        }
        .sheet-container { 
            width: 297mm !important; 
            height: 210mm !important; 
            margin: 0 !important; 
            padding: 0 !important; 
            page-break-after: always !important; 
            break-after: page !important; 
        }
        .page { 
            box-shadow: none !important; 
            margin: 0 !important; 
            width: 297mm !important; 
            height: 210mm !important; 
            max-width: 297mm !important; 
            max-height: 210mm !important; 
            transform: none !important; 
        }
        @page { 
            size: 297mm 210mm; 
            margin: 0; 
        }
    </style>
</head>
<body>
    <div class="viewport">
        ${viewportHtml}
    </div>
</body>
</html>
`;

    try {
        fs.writeFileSync(tempHtmlPath, fullHtml, 'utf-8');

        execSync(`"${browserPath}" --headless --disable-gpu --run-all-compositor-stages-before-draw --no-pdf-header-footer --print-to-pdf="${tempPdfPath}" "${tempHtmlPath}"`, {
            windowsHide: true,
            timeout: 30000
        });

        if (fs.existsSync(tempPdfPath)) {
            const pdfBuffer = fs.readFileSync(tempPdfPath);
            const safeAsciiFilename = "variants.pdf";
            const utf8Filename = `${className}_Варианты.pdf`;

            res.setHeader('Content-Type', 'application/pdf');
            // Стандарт RFC 5987 / RFC 6266: предотвращает ошибку Invalid character in header
            res.setHeader('Content-Disposition', `attachment; filename="${safeAsciiFilename}"; filename*=UTF-8''${encodeURIComponent(utf8Filename)}`);
            res.send(pdfBuffer);
        } else {
            res.status(500).json({ error: "Файл PDF не был создан." });
        }
    } catch (e) {
        console.error("Ошибка печати в PDF:", e.message);
        res.status(500).json({ error: "Ошибка создания PDF: " + e.message });
    } finally {
        try { if (fs.existsSync(tempHtmlPath)) fs.unlinkSync(tempHtmlPath); } catch (e) {}
        try { if (fs.existsSync(tempPdfPath)) fs.unlinkSync(tempPdfPath); } catch (e) {}
    }
});

app.listen(PORT, () => {
    console.log(`Сервер запущен: http://localhost:${PORT}`);
});