const fs = require('fs');
const path = require('path');
const os = require('os');
const { pathToFileURL } = require('url');
const { execFileSync } = require('child_process');

function getSystemBrowserPath() {
    const candidates = [
        // Windows
        path.join(process.env['ProgramFiles(x86)'] || 'C:\\Program Files (x86)', 'Microsoft\\Edge\\Application\\msedge.exe'),
        path.join(process.env['ProgramFiles'] || 'C:\\Program Files', 'Microsoft\\Edge\\Application\\msedge.exe'),
        path.join(process.env['ProgramFiles'] || 'C:\\Program Files', 'Google\\Chrome\\Application\\chrome.exe'),
        path.join(process.env['ProgramFiles(x86)'] || 'C:\\Program Files (x86)', 'Google\\Chrome\\Application\\chrome.exe'),
        path.join(process.env['LocalAppData'] || '', 'Microsoft\\Edge\\Application\\msedge.exe'),
        path.join(process.env['LocalAppData'] || '', 'Google\\Chrome\\Application\\chrome.exe'),
        // macOS
        '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
        '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
        '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser',
        '/Applications/Chromium.app/Contents/MacOS/Chromium',
        // Linux
        '/usr/bin/chromium',
        '/usr/bin/chromium-browser',
        '/usr/bin/google-chrome'
    ];
    return candidates.find(p => fs.existsSync(p)) || null;
}

function exportPdfHandler(req, res) {
    const { className = 'Варианты', viewportHtml, styles, cssVariables = {} } = req.body;
    const browserPath = getSystemBrowserPath();

    if (!browserPath) {
        return res.status(500).json({
            error: "Браузер Edge/Chrome не найден. Используйте кнопку '🖨️ Печать' -> 'Сохранить как PDF'."
        });
    }

    const tempId = `${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
    const tempHtmlPath = path.join(os.tmpdir(), `vpr_${tempId}.html`);
    const tempPdfPath = path.join(os.tmpdir(), `vpr_${tempId}.pdf`);

    const fullHtml = `<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <style>
        ${styles}
        :root {
            --page-padding: ${cssVariables.padding || '5mm'};
            --font-family: ${cssVariables.font || "'Courier New', Courier, monospace"};
            --font-size: ${cssVariables.fontSize || '11pt'};
            --zoom-scale: 1.0;
        }
        .task-circle .tc-num { opacity: 1 !important; animation: none !important; }
        .task-circle .tc-icon { display: none !important; }
        .overflow-badge { display: none !important; }
        .sheet-label { display: none !important; }
    </style>
</head>
<body><div class="viewport">${viewportHtml}</div></body>
</html>`;

    try {
        fs.writeFileSync(tempHtmlPath, fullHtml, 'utf-8');
        execFileSync(browserPath, [
            '--headless',
            '--disable-gpu',
            '--run-all-compositor-stages-before-draw',
            '--no-pdf-header-footer',
            `--print-to-pdf=${tempPdfPath}`,
            pathToFileURL(tempHtmlPath).href
        ], { windowsHide: true, timeout: 45000 });

        const pdfBuffer = fs.readFileSync(tempPdfPath);
        const utf8Name = `${className}_Варианты.pdf`;
        res.setHeader('Content-Type', 'application/pdf');
        res.setHeader('Content-Disposition', `attachment; filename="variants.pdf"; filename*=UTF-8''${encodeURIComponent(utf8Name)}`);
        res.send(pdfBuffer);
    } catch (e) {
        res.status(500).json({ error: 'Ошибка генерации PDF: ' + e.message });
    } finally {
        if (fs.existsSync(tempHtmlPath)) try { fs.unlinkSync(tempHtmlPath); } catch {}
        if (fs.existsSync(tempPdfPath)) try { fs.unlinkSync(tempPdfPath); } catch {}
    }
}

function renderEditorPage(req, res) {
    res.send(`<!DOCTYPE html>
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
        body { margin: 0; background: #e2e8f0; color: #1e293b; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; }
        
        /* Панель инструментов */
        .toolbar {
            position: sticky; top: 0; z-index: 1000;
            background: linear-gradient(135deg, #4caf50, #2e7d32); color: #fff;
            padding: 10px 20px; display: flex; flex-wrap: wrap; gap: 14px; align-items: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }
        .toolbar-group { display: flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; }
        .toolbar select {
            background: #fff; color: #1e293b; border: 1px solid rgba(0,0,0,0.2);
            padding: 5px 10px; border-radius: 6px; font-size: 13px; font-weight: 600;
            cursor: pointer; outline: none;
        }
        .toolbar-check {
            display: inline-flex; align-items: center; gap: 6px;
            background: rgba(255,255,255,0.18); padding: 5px 10px; border-radius: 6px;
            cursor: pointer; user-select: none; font-size: 12.5px;
        }
        .toolbar-check input { margin: 0; width: 15px; height: 15px; cursor: pointer; accent-color: #1b5e20; }
        .toolbar-right { margin-left: auto; display: flex; align-items: center; gap: 10px; }
        .toolbar-overflow-warn {
            display: none; align-items: center; background: #dc2626; color: #fff;
            border: 1.5px solid #fecaca; padding: 6px 12px; border-radius: 8px;
            font-size: 12.5px; font-weight: 700; cursor: pointer;
            box-shadow: 0 2px 8px rgba(220,38,38,0.45); white-space: nowrap;
        }
        .toolbar-overflow-warn:hover { background: #b91c1c; }
        .btn-print {
            background: #fff !important; color: #1b5e20 !important; border: none !important;
            padding: 7px 16px; border-radius: 8px; font-size: 13.5px; font-weight: 800;
            cursor: pointer; box-shadow: 0 2px 6px rgba(0,0,0,0.18);
        }
        .btn-print:hover { opacity: 0.92; }
        .btn-pdf {
            background: #0284c7 !important; color: #fff !important; border: none !important;
            padding: 7px 16px; border-radius: 8px; font-size: 13.5px; font-weight: 800;
            cursor: pointer; box-shadow: 0 2px 6px rgba(0,0,0,0.18);
        }
        .btn-pdf:hover { background: #0369a1 !important; }
        .btn-pdf:disabled, .btn-print:disabled { opacity: 0.6; cursor: not-allowed; }

        /* Область предпросмотра */
        .viewport { padding: 32px 10px; display: flex; flex-direction: column; align-items: center; gap: 24px; }
        .sheet-container {
            width: calc(297mm * var(--zoom-scale));
            height: calc(210mm * var(--zoom-scale));
            position: relative; margin-bottom: 18px; flex-shrink: 0;
        }
        .sheet-label { position: absolute; top: -22px; left: 0; color: #334155; font-size: 12px; font-weight: 700; }

        /* Лист A4 (297 x 210 мм) */
        .page {
            background: #fff;
            width: 297mm !important; height: 210mm !important;
            min-width: 297mm !important; max-width: 297mm !important;
            min-height: 210mm !important; max-height: 210mm !important;
            box-shadow: 0 8px 25px rgba(0,0,0,0.22);
            padding: var(--page-padding);
            position: absolute; top: 0; left: 0;
            color: #000;
            font-family: var(--font-family);
            font-size: var(--font-size);
            line-height: 1.2;
            text-rendering: geometricPrecision;
            transform-origin: top left;
            transform: scale(var(--zoom-scale));
            overflow: hidden;
        }
        .overflow-badge {
            display: none; position: absolute; bottom: 4px; right: 8px;
            background: #dc3545; color: #fff; padding: 3px 10px; border-radius: 4px;
            font-size: 11px; font-family: sans-serif; font-weight: bold; z-index: 500;
        }

        /* Режимы колонок */
        .one-column-mode { display: grid; grid-template-columns: minmax(0, 1fr); grid-template-rows: minmax(0, 1fr); }
        .two-columns-mode {
            display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
            grid-template-rows: minmax(0, 1fr); column-gap: calc(var(--page-padding) * 1.6);
        }
        .column-block { position: relative; width: 100%; height: 100%; min-height: 0; max-height: 100%; overflow: hidden; display: block; }

        /* Заголовок варианта */
        .variant-header {
            display: flex; justify-content: space-between; align-items: baseline;
            border-bottom: 1.5px solid #000; padding-bottom: 2px; margin-bottom: 4px;
            font-weight: bold; line-height: 1.15;
        }
        .variant-left { font-size: 1.02em; }
        .variant-right { font-size: 0.88em; }

        /* Блок задания */
        .task-block { margin-bottom: 4px; break-inside: avoid; }
        .task-title { font-weight: bold; margin-bottom: 2px; display: flex; gap: 6px; align-items: baseline; line-height: 1.18; }
        
        /* Интерактивный кружок перегенерации задания */
        @keyframes tcPulseNum { 0%, 72%, 100% { opacity: 1; } 78%, 94% { opacity: 0; } }
        @keyframes tcPulseIcon { 0%, 72%, 100% { opacity: 0; } 78%, 94% { opacity: 1; } }
        @keyframes tcSpin { to { transform: rotate(360deg); } }
        .task-circle {
            position: relative; display: inline-flex; align-items: center; justify-content: center;
            width: 1.3em; height: 1.3em; font-size: 1.15em; line-height: 1;
            flex-shrink: 0; user-select: none; cursor: pointer;
        }
        .task-circle .tc-num { animation: tcPulseNum 4s infinite; transition: opacity .15s; }
        .task-circle .tc-icon {
            position: absolute; font-size: 0.8em; opacity: 0;
            animation: tcPulseIcon 4s infinite; transition: opacity .15s, transform .15s;
        }
        .task-circle:hover .tc-num, .task-circle.is-loading .tc-num { opacity: 0 !important; animation: none !important; }
        .task-circle:hover .tc-icon { opacity: 1 !important; animation: none !important; transform: scale(1.15); }
        .task-circle.is-loading .tc-icon { opacity: 1 !important; animation: tcSpin .6s linear infinite !important; }

        .task-body { margin-left: 18px; line-height: 1.18; }
        .task-line { margin-bottom: 1px; word-break: break-word; }
        .task-line-with-table { margin-bottom: 2px; line-height: 1.2; }
        .task-line-text { display: inline; }

        .variants-inline-flow { margin: 2px 0; display: flex; flex-wrap: wrap; align-items: baseline; gap: 3px 12px; line-height: 1.2; }
        .variant-chip { white-space: nowrap; display: inline-flex; gap: 4px; }
        .last-variant-row { display: flex; justify-content: space-between; align-items: baseline; flex-wrap: wrap; }
        .inline-answer { font-weight: bold; white-space: nowrap; margin-left: 10px; }
        .answer-line { margin-top: 2px; font-weight: bold; line-height: 1.18; }

        .answer-grid { border-collapse: collapse; margin: 1px 0 1px 8px; display: inline-table; vertical-align: middle; }
        .answer-grid td { border: 1px solid #000; min-width: 22px; height: 17px; padding: 0 3px; text-align: center; font-size: 0.82em; }
        .answer-grid tr:first-child td { font-weight: bold; background: #f2f2f2; }

        .keys-table { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 0.88em; }
        .keys-table th, .keys-table td { border: 1px solid #000; padding: 4px 5px; text-align: center; }
        .keys-table th { background: #f2f2f2; }
        .keys-table td:nth-child(2) { text-align: left; }

        @media print {
            html, body { width: 297mm !important; margin: 0 !important; padding: 0 !important; background: #fff !important; }
            .toolbar, .sheet-label, .overflow-badge { display: none !important; }
            .task-circle .tc-num { opacity: 1 !important; animation: none !important; }
            .task-circle .tc-icon { display: none !important; }
            .viewport { display: block !important; padding: 0 !important; margin: 0 !important; }
            .sheet-container {
                width: 297mm !important; height: 210mm !important; margin: 0 !important; padding: 0 !important;
                page-break-after: always !important; break-after: page !important; overflow: hidden !important;
            }
            .sheet-container:last-child { page-break-after: auto !important; break-after: auto !important; }
            .page {
                position: relative !important; box-shadow: none !important; margin: 0 !important;
                width: 297mm !important; height: 210mm !important; transform: none !important;
            }
            @page { size: 297mm 210mm; margin: 0; }
        }
    </style>
</head>
<body>
    <div class="toolbar">
        <div class="toolbar-group">
            <label for="fontFamilySelect">Шрифт:</label>
            <select id="fontFamilySelect" onchange="rebuildPages()">
                <option value="'Courier New', Courier, monospace" selected>Courier New</option>
                <option value="'Times New Roman', Times, serif">Times New Roman</option>
                <option value="Arial, sans-serif">Arial</option>
                <option value="Calibri, sans-serif">Calibri</option>
            </select>
        </div>
        <div class="toolbar-group">
            <label for="fontSizeSelect">Кегль:</label>
            <select id="fontSizeSelect" onchange="rebuildPages()">
                <option value="6pt">6 пт</option>
                <option value="7pt">7 пт</option>
                <option value="8pt">8 пт</option>
                <option value="9pt">9 пт</option>
                <option value="10pt">10 пт</option>
                <option value="11pt" selected>11 пт</option>
                <option value="12pt">12 пт</option>
                <option value="13pt">13 пт</option>
                <option value="14pt">14 пт</option>
            </select>
        </div>
        <div class="toolbar-group">
            <label for="marginsSelect">Поля:</label>
            <select id="marginsSelect" onchange="rebuildPages()">
                <option value="1mm">0.1 см (1 мм)</option>
                <option value="5mm" selected>0.5 см (5 мм)</option>
                <option value="10mm">1.0 см (10 мм)</option>
                <option value="15mm">1.5 см (15 мм)</option>
            </select>
        </div>
        <div class="toolbar-group">
            <label class="toolbar-check">
                <input type="checkbox" id="twoColumnsCheckbox" checked onchange="rebuildPages()">
                <span>В два столбца (2 ученика на лист)</span>
            </label>
        </div>
        <div class="toolbar-group">
            <label class="toolbar-check">
                <input type="checkbox" id="duplexCheckbox" checked onchange="rebuildPages()">
                <span>🖨️ Двусторонняя печать (перенос на оборот)</span>
            </label>
        </div>
        <div class="toolbar-group">
            <label for="zoomSelect">Масштаб:</label>
            <select id="zoomSelect" onchange="applyZoom()">
                <option value="fit">По ширине</option>
                <option value="0.65">65%</option>
                <option value="0.82" selected>82%</option>
                <option value="1.0">100%</option>
            </select>
        </div>
        <div class="toolbar-right">
            <div id="toolbarOverflowWarn" class="toolbar-overflow-warn"></div>
            <button type="button" class="btn-print" id="printBtn" onclick="window.print()">🖨️ Печать</button>
            <button type="button" class="btn-pdf" id="pdfBtn" onclick="exportToPdf()">💾 Скачать PDF</button>
        </div>
    </div>

    <div class="viewport" id="viewportArea"></div>

    <script>
        let DATA = null;
        const $ = id => document.getElementById(id);
        const CIRCLED = ["①","②","③","④","⑤","⑥","⑦","⑧","⑨","⑩","⑪","⑫","⑬","⑭","⑮","⑯","⑰","⑱","⑲","⑳","㉑","㉒","㉓","㉔","㉕","㉖","㉗","㉘","㉙","㉚"];

        function applyZoom() {
            const val = $('zoomSelect').value;
            const scale = val === 'fit'
                ? Math.min(1.0, Math.max(0.4, (window.innerWidth - 60) / ((297 / 25.4) * 96)))
                : parseFloat(val);
            document.documentElement.style.setProperty('--zoom-scale', scale);
        }

        function buildTableHtml(t) {
            const tbl = t.table || t.code_table || (Array.isArray(t.answer_table) ? {
                headers: t.answer_table,
                rows: [t.answer_table.map(() => '&nbsp;')]
            } : null);
            if (!tbl || !Array.isArray(tbl.headers)) return '';
            return '<table class="answer-grid"><tr>' + tbl.headers.map(h => '<td>' + h + '</td>').join('') + '</tr>' +
                (tbl.rows || []).map(r => '<tr>' + r.map(c => '<td>' + c + '</td>').join('') + '</tr>').join('') + '</table>';
        }

        function renderTaskHtml(t, idx, vIdx) {
            const lines = String(t.task || '').split('\\n').map(s => s.trim()).filter(Boolean);
            const titleLine = lines[0] || '';
            const bodyLines = lines.slice(1);
            const tableHtml = buildTableHtml(t);
            const numIcon = CIRCLED[idx] || (idx + 1) + '.';

            let html = '<div class="task-block"><div class="task-title">' +
                '<span class="task-circle" contenteditable="false" data-v="' + vIdx + '" data-t="' + idx + '" title="Нажмите, чтобы перегенерировать это задание">' +
                '<span class="tc-num">' + numIcon + '</span>' +
                '<span class="tc-icon">🔄</span>' +
                '</span>' +
                '<span>' + titleLine + '</span></div><div class="task-body">';

            if (tableHtml) {
                if (!bodyLines.length) {
                    html += '<div class="task-line-with-table">' + tableHtml + '</div>';
                } else {
                    bodyLines.slice(0, -1).forEach(l => { html += '<div class="task-line">' + l + '</div>'; });
                    html += '<div class="task-line-with-table"><span class="task-line-text">' + bodyLines[bodyLines.length - 1] + '</span>' + tableHtml + '</div>';
                }
                const isAnsTbl = Array.isArray(t.answer_table) || ((t.table || t.code_table)?.rows || []).some(r => r.some(c => !String(c ?? '').replace(/&nbsp;/g, '').trim()));
                if (!isAnsTbl) {
                    html += '<div class="answer-line">Ответ: ___________</div>';
                }
            } else if (Array.isArray(t.variants) && t.variants.length) {
                bodyLines.forEach(l => { html += '<div class="task-line">' + l + '</div>'; });
                const isInline = t.variant_style === 'inline' || (t.variant_style !== 'block' && t.variants.every(v => String(v).length < 25 && !String(v).includes('\\\\')));

                if (isInline) {
                    html += '<div class="variants-inline-flow">' +
                        t.variants.map((v, i) => '<span class="variant-chip"><strong>' + (i + 1) + ')</strong> ' + v + '</span>').join('') +
                        '<span class="inline-answer">Ответ: ___________</span></div>';
                } else {
                    t.variants.forEach((v, i) => {
                        html += i === t.variants.length - 1
                            ? '<div class="task-line last-variant-row"><div><strong>' + (i + 1) + ')</strong> ' + v + '</div><div class="inline-answer">Ответ: ___________</div></div>'
                            : '<div class="task-line"><strong>' + (i + 1) + ')</strong> ' + v + '</div>';
                    });
                }
            } else {
                bodyLines.forEach(l => { html += '<div class="task-line">' + l + '</div>'; });
                html += '<div class="answer-line">Ответ: ___________</div>';
            }

            return html + '</div></div>';
        }

        function fillColumn(colElement, tasks, vIdx) {
            const maxH = colElement.clientHeight;
            const overflow = [];
            let full = false;

            tasks.forEach((task, idx) => {
                if (full) return overflow.push({ task, idx });
                const wrapper = document.createElement('div');
                wrapper.innerHTML = renderTaskHtml(task, idx, vIdx);
                const node = wrapper.firstElementChild;
                colElement.appendChild(node);

                if (colElement.scrollHeight > maxH + 1) {
                    colElement.removeChild(node);
                    full = true;
                    overflow.push({ task, idx });
                }
            });
            return overflow;
        }

        function createSheet(viewport, labelText, modeClass) {
            const container = document.createElement('div');
            container.className = 'sheet-container';
            container.innerHTML = '<div class="sheet-label">' + labelText + '</div>';
            const page = document.createElement('div');
            page.className = 'page ' + (modeClass || '');
            page.contentEditable = "true";
            page.innerHTML = '<div class="overflow-badge"></div>';
            container.appendChild(page);
            viewport.appendChild(container);
            return page;
        }

        function headerHtml(variantNum, student, className, onlyVariant = false) {
            return onlyVariant
                ? '<div class="variant-header"><div class="variant-left">Вариант ' + variantNum + '</div></div>'
                : '<div class="variant-header"><div class="variant-left">Вариант ' + variantNum + '</div><div class="variant-right">' + (student || '') + ' &nbsp;&nbsp;&nbsp; Класс: ' + (className || '') + '</div></div>';
        }

        function rebuildPages() {
            if (!DATA) return;
            document.documentElement.style.setProperty('--font-family', $('fontFamilySelect').value);
            document.documentElement.style.setProperty('--font-size', $('fontSizeSelect').value);
            document.documentElement.style.setProperty('--page-padding', $('marginsSelect').value);
            document.documentElement.style.setProperty('--zoom-scale', '1');

            const viewport = $('viewportArea');
            viewport.innerHTML = '';

            const isTwoCol = $('twoColumnsCheckbox').checked;
            const isDuplex = $('duplexCheckbox').checked;
            const step = isTwoCol ? 2 : 1;
            const modeClass = isTwoCol ? 'two-columns-mode' : 'one-column-mode';
            let sheetNum = 1;

            for (let i = 0; i < DATA.variants.length; i += step) {
                const pair = DATA.variants.slice(i, i + step);
                const curSheet = sheetNum++;
                const desc = isTwoCol
                    ? 'Вар. ' + (i + 1) + (pair[1] ? ' и ' + (i + 2) : '')
                    : 'Вариант ' + (i + 1);

                // Лицевая сторона
                const frontLabel = isDuplex ? '📄 Лист ' + curSheet + ' (ЛИЦО • ' + desc + ')' : '📄 Лист ' + curSheet + ' (' + desc + ')';
                const frontPage = createSheet(viewport, frontLabel, modeClass);
                const overflows = [];

                for (let s = 0; s < step; s++) {
                    const col = document.createElement('div');
                    col.className = 'column-block';
                    frontPage.appendChild(col);
                    const v = pair[s];
                    const vIdx = i + s;
                    if (!v) { overflows.push([]); continue; }

                    col.innerHTML = headerHtml(vIdx + 1, v.student, DATA.className);
                    if (isDuplex) {
                        overflows.push(fillColumn(col, v.tasks, vIdx));
                    } else {
                        col.insertAdjacentHTML('beforeend', v.tasks.map((t, idx) => renderTaskHtml(t, idx, vIdx)).join(''));
                    }
                }

                // Оборотная сторона (при включенной двусторонней печати)
                if (isDuplex) {
                    const backOrder = isTwoCol ? [1, 0] : [0];
                    const backDesc = isTwoCol
                        ? 'Вар. ' + (pair[1] ? i + 2 : '—') + ' слева, Вар. ' + (i + 1) + ' справа'
                        : 'Вариант ' + (i + 1);
                    const backPage = createSheet(viewport, '📄 Лист ' + curSheet + ' (ОБОРОТ • ' + backDesc + ')', modeClass);

                    backOrder.forEach(s => {
                        const col = document.createElement('div');
                        col.className = 'column-block';
                        const v = pair[s];
                        if (v) {
                            const vIdx = i + s;
                            col.innerHTML = headerHtml(vIdx + 1, null, null, true) +
                                overflows[s].map(x => renderTaskHtml(x.task, x.idx, vIdx)).join('');
                        }
                        backPage.appendChild(col);
                    });
                }
            }

            buildKeysSheets(viewport, sheetNum);
            checkOverflows();
            applyZoom();
        }

        function buildKeysSheets(viewport, sheetNum) {
            const taskCount = DATA.variants[0]?.tasks?.length || 0;
            let thHtml = '<tr><th style="width:45px;">Вар.</th><th>Ученик</th>';
            for (let i = 0; i < taskCount; i++) thHtml += '<th>№' + (i + 1) + '</th>';
            thHtml += '</tr>';

            let idx = 0, part = 1;
            while (idx < DATA.variants.length || idx === 0) {
                const suffix = part > 1 ? ' (Часть ' + part + ')' : '';
                const page = createSheet(viewport, '📄 Лист ' + (sheetNum++) + ' (КЛЮЧИ И ОТВЕТЫ' + suffix + ')', 'keys-card');
                page.innerHTML =
                    '<h2 style="margin-top:0;border-bottom:2px solid #000;padding-bottom:4px;font-size:1.1em;">' +
                    'КЛЮЧИ И ОТВЕТЫ (Класс: ' + (DATA.className || '') + ')' + suffix +
                    '</h2>' +
                    '<table class="keys-table"><thead>' + thHtml + '</thead><tbody></tbody></table>';

                const tbody = page.querySelector('tbody');
                const maxH = page.clientHeight;
                let added = 0;

                while (idx < DATA.variants.length) {
                    const v = DATA.variants[idx];
                    const tr = document.createElement('tr');
                    tr.innerHTML = '<td>' + (idx + 1) + '</td><td>' + v.student + '</td>' + v.tasks.map(t => '<td><b>' + (t.answer || '—') + '</b></td>').join('');
                    tbody.appendChild(tr);

                    if (page.scrollHeight > maxH && added > 0) {
                        tbody.removeChild(tr);
                        break;
                    }
                    added++;
                    idx++;
                }
                if (!DATA.variants.length) break;
                part++;
            }
        }

        function checkOverflows() {
            let overflowCount = 0;
            let maxExMm = 0;
            let firstOverflowSheet = null;

            document.querySelectorAll('.page:not(.keys-card)').forEach(page => {
                const badge = page.querySelector('.overflow-badge');
                if (!badge) return;
                let excess = 0;
                page.querySelectorAll('.column-block').forEach(c => {
                    excess = Math.max(excess, c.scrollHeight - c.clientHeight);
                });
                const isOver = excess > 2;
                badge.style.display = isOver ? 'block' : 'none';
                if (isOver) {
                    const mm = Math.max(1, Math.round((excess / 96) * 25.4));
                    badge.innerText = '⚠️ Не влезает: +' + mm + ' мм — уменьшите кегль или включите двустороннюю печать!';
                    overflowCount++;
                    maxExMm = Math.max(maxExMm, mm);
                    if (!firstOverflowSheet) firstOverflowSheet = page.closest('.sheet-container');
                }
            });

            const topWarn = $('toolbarOverflowWarn');
            if (topWarn) {
                if (overflowCount > 0) {
                    topWarn.style.display = 'inline-flex';
                    topWarn.innerText = '⚠️ Не влезает (' + overflowCount + ' л., до +' + maxExMm + ' мм)';
                    topWarn.title = 'Нажмите, чтобы перейти к проблемному листу';
                    topWarn.onclick = () => firstOverflowSheet?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else {
                    topWarn.style.display = 'none';
                    topWarn.onclick = null;
                }
            }
        }

        // Перегенерация отдельного задания по клику на кружок номера
        $('viewportArea').addEventListener('click', async (e) => {
            const circle = e.target.closest('.task-circle');
            if (!circle || circle.classList.contains('is-loading')) return;
            e.preventDefault();
            e.stopPropagation();

            const vIdx = Number(circle.dataset.v);
            const tIdx = Number(circle.dataset.t);
            const curTask = DATA?.variants?.[vIdx]?.tasks?.[tIdx];
            if (!curTask || (!curTask._file && !curTask._key)) return;

            const taskFile = curTask._file || pathBasename(curTask._key);
            circle.classList.add('is-loading');

            try {
                const res = await fetch('/api/regenerate-task', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ folder: DATA.folder, file: taskFile })
                });
                const json = await res.json();
                if (!res.ok || !json.ok) throw new Error(json.error || 'Ошибка перегенерации задания');

                const nextTask = json.data;
                nextTask._file = taskFile;
                DATA.variants[vIdx].tasks[tIdx] = nextTask;
                localStorage.setItem('editor_data', JSON.stringify(DATA));
                rebuildPages();
            } catch (err) {
                alert('Ошибка перегенерации: ' + err.message);
                circle.classList.remove('is-loading');
            }
        });

        function pathBasename(p) {
            if (!p) return '';
            const parts = String(p).split(/[\\\\/]/);
            return parts[parts.length - 1];
        }

        async function exportToPdf() {
            const btn = $('pdfBtn');
            btn.disabled = true;
            btn.innerText = '⏳ Сборка PDF...';
            try {
                const res = await fetch('/api/export-pdf', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        className: DATA.className,
                        viewportHtml: $('viewportArea').innerHTML,
                        styles: $('pageStyleBlock').innerHTML,
                        cssVariables: {
                            padding: $('marginsSelect').value,
                            font: $('fontFamilySelect').value,
                            fontSize: $('fontSizeSelect').value
                        }
                    })
                });
                if (!res.ok) throw new Error((await res.json()).error);
                const blob = await res.blob();
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = (DATA.className || 'Класс') + '_Варианты.pdf';
                a.click();
            } catch (e) {
                alert(e.message || 'Ошибка экспорта PDF');
            } finally {
                btn.disabled = false;
                btn.innerText = '💾 Скачать PDF';
            }
        }

        window.onload = () => {
            const raw = localStorage.getItem('editor_data') || localStorage.getItem('msh_vpr_editor_data');
            if (raw) {
                DATA = JSON.parse(raw);
                document.title = (DATA.className || 'Варианты') + ' — Редактор вариантов';
                rebuildPages();
            } else {
                $('viewportArea').innerHTML = '<div style="color:#64748b;padding:40px;text-align:center;"><h2>Нет данных для отображения</h2><p><a href="/" style="color:#007bff;">Вернуться на главную страницу генератора</a></p></div>';
            }
            $('viewportArea').addEventListener('input', checkOverflows);
        };
        window.onresize = () => { if ($('zoomSelect').value === 'fit') applyZoom(); };
    </script>
</body>
</html>`);
}

module.exports = { renderEditorPage, exportPdfHandler };
