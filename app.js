const express = require('express');
const fs = require('fs');
const path = require('path');
const os = require('os');
const { execFile } = require('child_process');
const { renderEditorPage, exportPdfHandler } = require('./generatorPDF');

const app = express();
const PORT = 3000;
app.use(express.json({ limit: '50mb' }));

const PYTHON_CMD = [
    path.join(__dirname, 'venv', 'Scripts', 'python.exe'),
    path.join(__dirname, 'venv', 'bin', 'python'),
    path.join(__dirname, '.venv', 'Scripts', 'python.exe'),
    path.join(__dirname, '.venv', 'bin', 'python')
].find(p => fs.existsSync(p)) || (process.platform === 'win32' ? 'python' : 'python3');

const IGNORED_DIRS = new Set(['node_modules', 'venv', '.venv', '.git', '.idea', '.vscode', '__pycache__']);
const metaCache = new Map();

function runPython(filePath, args = []) {
    return new Promise((resolve, reject) => {
        execFile(PYTHON_CMD, [filePath, ...args], {
            encoding: 'utf-8',
            env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
        }, (err, stdout, stderr) => {
            if (err) return reject(new Error(stderr || err.message));
            resolve(stdout.trim());
        });
    });
}

async function mapConcurrent(items, limit, fn) {
    const results = new Array(items.length);
    let idx = 0;
    await Promise.all(Array.from({ length: Math.min(limit, items.length) }, async () => {
        while (idx < items.length) {
            const cur = idx++;
            results[cur] = await fn(items[cur], cur);
        }
    }));
    return results;
}

function getSafeFolderPath(folderName) {
    if (!folderName) return null;
    const clean = String(folderName).trim();
    if (!clean || clean.startsWith('.') || IGNORED_DIRS.has(clean)) return null;
    const resolved = path.resolve(__dirname, clean);
    if (!resolved.startsWith(__dirname)) return null;
    return fs.existsSync(resolved) && fs.statSync(resolved).isDirectory() ? resolved : null;
}

app.get('/api/folders', (req, res) => {
    const folders = fs.readdirSync(__dirname, { withFileTypes: true })
        .filter(d => d.isDirectory() && !d.name.startsWith('.') && !IGNORED_DIRS.has(d.name))
        .map(d => d.name)
        .sort((a, b) => a.localeCompare(b, 'ru', { numeric: true }));
    res.json(folders);
});

app.get('/api/tasks', async (req, res) => {
    const folderPath = getSafeFolderPath(req.query.folder);
    if (!folderPath || !fs.existsSync(folderPath)) return res.json([]);

    const files = fs.readdirSync(folderPath).filter(f => f.startsWith('task_') && f.endsWith('.py'));
    const tasks = await Promise.all(files.map(async (file) => {
        const fullPath = path.join(folderPath, file);
        const mtime = fs.statSync(fullPath).mtimeMs;
        const cached = metaCache.get(fullPath);
        if (cached && cached.mtime === mtime) return cached.data;

        try {
            const meta = JSON.parse(await runPython(fullPath, ['--meta']));
            const data = { file, id: meta.id ?? 999, title: meta.title || file };
            metaCache.set(fullPath, { mtime, data });
            return data;
        } catch {
            return null;
        }
    }));

    res.json(tasks.filter(Boolean).sort((a, b) => a.id - b.id));
});

app.post('/api/generate-data', async (req, res) => {
    const { folder, className, students = [], tasks = [] } = req.body;
    const folderPath = getSafeFolderPath(folder);
    if (!folderPath || !fs.existsSync(folderPath)) {
        return res.status(400).json({ error: 'Папка с заданиями не найдена' });
    }

    // Нормализация списка заданий (поддержка строк и объектов с count)
    const taskList = [];
    tasks.forEach(item => {
        if (typeof item === 'string') {
            taskList.push(path.basename(item));
        } else if (item && item.file) {
            const count = Math.max(1, Math.min(50, parseInt(item.count, 10) || 1));
            const baseFile = path.basename(item.file);
            for (let i = 0; i < count; i++) taskList.push(baseFile);
        }
    });

    if (!students.length || !taskList.length) {
        return res.status(400).json({ error: 'Укажите учеников и выберите задания' });
    }

    const startTime = Date.now();
    const jobs = [];
    students.forEach((_, sIdx) => taskList.forEach((taskFile, tIdx) => {
        jobs.push({ sIdx, tIdx, taskFile });
    }));

    const concurrency = Math.max(4, Math.min(16, (os.cpus().length || 4) * 2));
    const results = await mapConcurrent(jobs, concurrency, async (job) => {
        const fullPath = path.join(folderPath, job.taskFile);
        for (let attempt = 0; attempt < 3; attempt++) {
            try {
                const stdout = await runPython(fullPath, ['--generate']);
                const parsed = JSON.parse(stdout);
                if (parsed && parsed.task) {
                    parsed._file = job.taskFile;
                    return { ...job, data: parsed };
                }
            } catch {}
        }
        return {
            ...job,
            data: { task: 'Ошибка генерации задания (' + job.taskFile + ')', answer: '—', _file: job.taskFile }
        };
    });

    const variants = students.map((student, sIdx) => ({
        variantNum: sIdx + 1,
        student,
        tasks: results.filter(r => r.sIdx === sIdx).sort((a, b) => a.tIdx - b.tIdx).map(r => r.data)
    }));

    res.json({ folder, className, variants, debug: { totalMs: Date.now() - startTime } });
});

// Точечная перегенерация одного задания по клику на кружок
app.post('/api/regenerate-task', async (req, res) => {
    const { folder, file } = req.body;
    const folderPath = getSafeFolderPath(folder);
    if (!folderPath) return res.status(400).json({ error: 'Папка не найдена' });

    const cleanFile = path.basename(String(file || ''));
    const fullPath = path.join(folderPath, cleanFile);
    if (!cleanFile.startsWith('task_') || !cleanFile.endsWith('.py') || !fs.existsSync(fullPath)) {
        return res.status(404).json({ error: 'Файл задания не найден: ' + cleanFile });
    }

    for (let attempt = 0; attempt < 3; attempt++) {
        try {
            const stdout = await runPython(fullPath, ['--generate']);
            const parsed = JSON.parse(stdout);
            if (parsed && parsed.task) {
                parsed._file = cleanFile;
                return res.json({ ok: true, data: parsed });
            }
        } catch (err) {
            if (attempt === 2) {
                return res.status(500).json({ ok: false, error: err.message || 'Ошибка Python' });
            }
        }
    }
    res.status(500).json({ ok: false, error: 'Не удалось сгенерировать задание после 3 попыток' });
});

app.get('/editor', renderEditorPage);
app.post('/api/export-pdf', exportPdfHandler);

app.get('/', (req, res) => {
    res.send(`<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Генератор индивидуальных вариантов ВПР и ОГЭ по информатике</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background: #f1f5f9; color: #1e293b; margin: 0; padding: 30px 20px;
        }
        .vpr-card {
            max-width: 980px; margin: 0 auto; background: #fff;
            border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.08);
            overflow: hidden; border: 1px solid #e2e8f0;
        }
        .vpr-header {
            background: linear-gradient(135deg, #4caf50, #2e7d32); color: #fff;
            padding: 18px 28px; font-size: 18px; font-weight: 700;
            display: flex; justify-content: space-between; align-items: center;
        }
        .vpr-header-sub { font-size: 13px; font-weight: 500; opacity: 0.92; }
        .vpr-body { padding: 24px 28px 28px; }
        .vpr-top-selectors {
            display: flex; gap: 20px; margin-bottom: 20px;
            background: #f8fafc; padding: 16px; border-radius: 10px; border: 1px solid #e2e8f0;
        }
        .vpr-top-col { flex: 1; }
        .vpr-grid { display: flex; gap: 28px; }
        .vpr-col { flex: 1; display: flex; flex-direction: column; }
        .vpr-label { display: block; margin-bottom: 6px; font-weight: 600; font-size: 13px; color: #2e7d32; }
        .vpr-label-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
        .vpr-badge {
            background: #e8f5e9; color: #2e7d32; border: 1px solid #c8e6c9;
            padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 700;
        }
        .vpr-input, .vpr-select, .vpr-textarea {
            width: 100%; padding: 9px 12px; background: #fff;
            border: 1px solid #cbd5e1; color: #1e293b; border-radius: 8px;
            font-size: 14px; font-family: inherit; outline: none; transition: .2s;
        }
        .vpr-input:focus, .vpr-select:focus, .vpr-textarea:focus {
            border-color: #2e7d32; box-shadow: 0 0 0 3px rgba(46,125,50,0.15);
        }
        .vpr-textarea { height: 210px; resize: vertical; line-height: 1.45; margin-bottom: 12px; }
        .vpr-btn-group, .vpr-task-actions { display: flex; gap: 8px; }
        .vpr-task-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; }
        .vpr-mini-btn, .vpr-btn-sec {
            background: #f1f5f9; color: #334155; border: 1px solid #cbd5e1;
            border-radius: 6px; font-weight: 600; cursor: pointer;
        }
        .vpr-mini-btn { padding: 4px 10px; font-size: 11.5px; }
        .vpr-btn-sec { flex: 1; padding: 9px 12px; font-size: 13px; border-radius: 8px; }
        .vpr-mini-btn:hover, .vpr-btn-sec:hover { background: #e2e8f0; }
        .vpr-btn-clear {
            flex: 1; background: #fef2f2; color: #dc2626; border: 1px solid #fecaca;
            border-radius: 8px; padding: 9px 12px; font-size: 13px; font-weight: 600; cursor: pointer;
        }
        .vpr-btn-clear:hover { background: #fee2e2; }
        .vpr-task-list {
            flex-grow: 1; height: 252px; overflow-y: auto; background: #f8fafc;
            padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 8px; margin-bottom: 12px;
        }
        .vpr-task-item {
            display: flex; align-items: center; gap: 10px; padding: 6px 8px;
            border-radius: 6px; font-size: 13.5px; cursor: pointer; user-select: none;
        }
        .vpr-task-item:hover { background: #e8f5e9; }
        .vpr-task-item input[type="checkbox"] {
            width: 16px; height: 16px; margin: 0; accent-color: #2e7d32; cursor: pointer; flex-shrink: 0;
        }
        .vpr-task-title-text { flex: 1; }
        .vpr-qty-box {
            display: inline-flex; align-items: center; gap: 2px; margin-left: auto;
            background: #fff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 1px 3px;
        }
        .vpr-task-item input[type="checkbox"]:not(:checked) ~ .vpr-qty-box { opacity: 0.35; pointer-events: none; }
        .vpr-qty-btn {
            background: #f1f5f9; border: none; border-radius: 4px;
            width: 20px; height: 20px; font-weight: 700; font-size: 13px;
            line-height: 1; color: #334155; cursor: pointer;
            display: flex; align-items: center; justify-content: center; padding: 0;
        }
        .vpr-qty-btn:hover { background: #cbd5e1; color: #0f172a; }
        .vpr-qty-input {
            width: 32px; height: 20px; border: none; text-align: center;
            font-size: 12.5px; font-weight: 700; color: #1e293b; outline: none;
            background: transparent; -moz-appearance: textfield; appearance: textfield; padding: 0;
        }
        .vpr-qty-input::-webkit-outer-spin-button, .vpr-qty-input::-webkit-inner-spin-button {
            -webkit-appearance: none; margin: 0;
        }
        .vpr-btn-main {
            background: linear-gradient(135deg, #4caf50, #2e7d32); color: #fff;
            border: none; border-radius: 8px; padding: 12px 18px; font-size: 15px;
            font-weight: 700; cursor: pointer; width: 100%;
            box-shadow: 0 4px 12px rgba(46,125,50,0.25); transition: .15s;
        }
        .vpr-btn-main:hover:not(:disabled) { transform: translateY(-1px); opacity: 0.96; }
        .vpr-btn-main:disabled { opacity: 0.6; cursor: not-allowed; }
    </style>
</head>
<body>
    <div class="vpr-card">
        <div class="vpr-header">
            <span>🖨️ Генератор индивидуальных вариантов ВПР и ОГЭ</span>
            <span class="vpr-header-sub">Информатика</span>
        </div>
        <div class="vpr-body">
            <div class="vpr-top-selectors">
                <div class="vpr-top-col">
                    <label class="vpr-label" for="classSelector">Выберите параллель:</label>
                    <select id="classSelector" class="vpr-select" onchange="onFolderChange()"></select>
                </div>
            </div>
            <div class="vpr-grid">
                <div class="vpr-col">
                    <div style="margin-bottom: 14px;">
                        <label class="vpr-label" for="className">Название класса:</label>
                        <input type="text" id="className" class="vpr-input" value="7-1">
                    </div>
                    <div class="vpr-label-row">
                        <label class="vpr-label" for="studentsList" style="margin: 0;">Список учеников:</label>
                        <span id="countBadge" class="vpr-badge">4 уч.</span>
                    </div>
                    <textarea id="studentsList" class="vpr-textarea" oninput="updateCount()">Храмцов Андрей
Перхурова Екатерина
Елькина Милина
Яцкевич Арина</textarea>
                    <div class="vpr-btn-group">
                        <button type="button" class="vpr-btn-sec" onclick="pasteStudents()">📋 Вставить</button>
                        <button type="button" class="vpr-btn-clear" onclick="clearStudents()">🗑 Очистить</button>
                    </div>
                </div>
                <div class="vpr-col">
                    <div class="vpr-task-header">
                        <label class="vpr-label" style="margin: 0;">Выбор заданий:</label>
                        <div class="vpr-task-actions">
                            <select id="bulkQtySelect" class="vpr-mini-btn" title="Установить количество всем отмеченным заданиям" style="outline: none;">
                                <option value="" selected disabled>По N шт...</option>
                                <option value="1">Всем по 1 шт.</option>
                                <option value="2">Всем по 2 шт.</option>
                                <option value="3">Всем по 3 шт.</option>
                                <option value="5">Всем по 5 шт.</option>
                                <option value="10">Всем по 10 шт.</option>
                            </select>
                            <button type="button" class="vpr-mini-btn" onclick="toggleAll(true)">Выбрать все</button>
                            <button type="button" class="vpr-mini-btn" onclick="toggleAll(false)">Снять все</button>
                        </div>
                    </div>
                    <div id="tasksContainer" class="vpr-task-list">
                        <div style="color: #64748b; padding: 10px;">⏳ Загрузка заданий...</div>
                    </div>
                    <button type="button" class="vpr-btn-main" id="genBtn" onclick="generate()">✨ Сгенерировать варианты</button>
                </div>
            </div>
        </div>
    </div>

    <script>
        const $ = id => document.getElementById(id);

        function updateCount() {
            const count = $('studentsList').value.split('\\n').filter(s => s.trim()).length;
            $('countBadge').innerText = count + ' уч.';
        }

        function toggleAll(state) {
            document.querySelectorAll('.task-cb').forEach(cb => { cb.checked = state; });
        }

        async function pasteStudents() {
            try {
                const text = await navigator.clipboard.readText();
                const el = $('studentsList');
                el.value = el.value.trim() ? el.value.trim() + '\\n' + text.trim() : text.trim();
                updateCount();
            } catch {
                alert('Используйте комбинацию клавиш Ctrl+V');
            }
        }

        function clearStudents() {
            $('studentsList').value = '';
            updateCount();
        }

        function getFolderLabel(folder) {
            if (/^7/i.test(folder)) return folder + ' (ВПР)';
            if (/^8/i.test(folder)) return folder + ' (ВПР)';
            if (/^9/i.test(folder)) return folder + ' (ОГЭ)';
            return folder;
        }

        async function initFolders() {
            try {
                const folders = await (await fetch('/api/folders')).json();
                $('classSelector').innerHTML = folders.map(f =>
                    '<option value="' + f + '">' + getFolderLabel(f) + '</option>'
                ).join('');
                onFolderChange();
            } catch (err) {
                $('tasksContainer').innerHTML = '<div style="color:#dc2626;">Ошибка загрузки списка папок</div>';
            }
        }

        async function onFolderChange() {
            const folder = $('classSelector').value;
            const numMatch = folder.match(/^(\\d+)/);
            const clsInput = $('className');
            if (numMatch && /^\\d+(-|$)/.test(clsInput.value)) {
                clsInput.value = numMatch[1] + '-' + (clsInput.value.split('-')[1] || '1');
            }

            $('tasksContainer').innerHTML = '<div style="color:#64748b;padding:10px;">⏳ Загрузка заданий...</div>';
            try {
                const tasks = await (await fetch('/api/tasks?folder=' + encodeURIComponent(folder))).json();
                if (!tasks.length) {
                    $('tasksContainer').innerHTML = '<em>В выбранной папке нет файлов task_*.py</em>';
                    return;
                }
                $('tasksContainer').innerHTML = tasks.map(t =>
                    '<label class="vpr-task-item">' +
                        '<input type="checkbox" class="task-cb" value="' + t.file + '" checked>' +
                        '<span class="vpr-task-title-text"><b>' + t.id + '.</b> ' + t.title + '</span>' +
                        '<div class="vpr-qty-box">' +
                            '<button type="button" class="vpr-qty-btn" data-dir="-1">−</button>' +
                            '<input type="number" class="vpr-qty-input" value="1" min="1" max="50">' +
                            '<button type="button" class="vpr-qty-btn" data-dir="1">+</button>' +
                        </div>' +
                    '</label>'
                ).join('');
            } catch (err) {
                $('tasksContainer').innerHTML = '<div style="color:#dc2626;">Ошибка загрузки заданий</div>';
            }
        }

        // Обработка кликов внутри списка заданий (кнопки +/- количества)
        $('tasksContainer').addEventListener('click', (e) => {
            if (e.target.closest('.vpr-qty-box')) {
                e.preventDefault();
            }
            const btn = e.target.closest('.vpr-qty-btn');
            if (btn) {
                const inp = btn.parentElement.querySelector('.vpr-qty-input');
                const cur = parseInt(inp.value, 10) || 1;
                inp.value = Math.max(1, Math.min(50, cur + Number(btn.dataset.dir)));
            }
        });

        // Массовое изменение количества заданий
        $('bulkQtySelect').addEventListener('change', (e) => {
            const val = parseInt(e.target.value, 10);
            if (val > 0) {
                document.querySelectorAll('.vpr-task-item').forEach(row => {
                    if (row.querySelector('.task-cb')?.checked) {
                        row.querySelector('.vpr-qty-input').value = val;
                    }
                });
            }
            e.target.value = '';
        });

        async function generate() {
            const folder = $('classSelector').value;
            const className = $('className').value.trim() || 'Класс';
            const students = $('studentsList').value.split('\\n').map(s => s.trim()).filter(Boolean);

            const tasks = [];
            document.querySelectorAll('.vpr-task-item').forEach(row => {
                const cb = row.querySelector('.task-cb');
                if (cb && cb.checked) {
                    const qty = Math.max(1, Math.min(50, parseInt(row.querySelector('.vpr-qty-input')?.value, 10) || 1));
                    for (let i = 0; i < qty; i++) {
                        tasks.push(cb.value);
                    }
                }
            });

            if (!students.length || !tasks.length) {
                return alert('Укажите учеников и выберите хотя бы одно задание!');
            }

            const win = window.open('about:blank', '_blank');
            win.document.write('<body style="background:#e2e8f0;color:#1e293b;font-family:Segoe UI,sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;"><div style="background:#fff;padding:24px 36px;border-radius:12px;box-shadow:0 8px 25px rgba(0,0,0,0.1);text-align:center;"><h2>⏳ Генерация вариантов...</h2><p style="color:#64748b;">Пожалуйста, подождите, идёт выполнение Python-скриптов</p></div></body>');

            const btn = $('genBtn');
            btn.disabled = true;
            btn.innerText = '⏳ Генерация вариантов...';

            try {
                const res = await fetch('/api/generate-data', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ folder, className, students, tasks })
                });
                if (!res.ok) {
                    const errData = await res.json().catch(() => ({}));
                    throw new Error(errData.error || 'Ошибка сервера при генерации');
                }
                const data = await res.json();
                localStorage.setItem('editor_data', JSON.stringify(data));
                localStorage.setItem('msh_vpr_editor_data', JSON.stringify(data));
                win.location.href = '/editor';
            } catch (err) {
                win.close();
                alert('Ошибка генерации: ' + err.message);
            } finally {
                btn.disabled = false;
                btn.innerText = '✨ Сгенерировать варианты';
            }
        }

        window.onload = () => {
            initFolders();
            updateCount();
        };
    </script>
</body>
</html>`);
});

app.listen(PORT, () => console.log(`Сервер запущен: http://localhost:${PORT}`));
