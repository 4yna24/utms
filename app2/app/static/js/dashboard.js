// ── Toast notification (reuses flash CSS classes) ──
function showToast(msg, type) {
    type = type || 'error';
    let wrap = document.querySelector('.flash-wrap');
    if (!wrap) {
        wrap = document.createElement('div');
        wrap.className = 'flash-wrap';
        document.body.prepend(wrap);
    }
    const el = document.createElement('div');
    el.className = `flash-msg flash-${type}`;
    el.textContent = msg;
    wrap.appendChild(el);
    setTimeout(() => el.remove(), 5000);
}

// Auto-dismiss server-rendered flash messages after 4 s
document.querySelectorAll('.flash-msg').forEach(el => {
    setTimeout(() => el.remove(), 4000);
});

document.addEventListener('DOMContentLoaded', () => {

    const tabButtons = document.querySelectorAll('.tab-button');
    const panels = document.querySelectorAll('.workspace-panel');
    const loaded = {};  // panelId → true once content has been fetched

    // ── Core: activate a panel, lazy-fetch if needed ──
    function activatePanel(targetId, slug, page) {
        page = Math.max(1, parseInt(page || 1, 10));

        panels.forEach(p => p.classList.toggle('active', p.id === targetId));
        tabButtons.forEach(b => {
            const active = b.dataset.target === targetId;
            b.classList.toggle('active', active);
            b.setAttribute('aria-pressed', String(active));
        });

        if (targetId === 'panel-main') {
            pushUrl('', 1);
            return;
        }

        if (!slug) return;
        const panel = document.getElementById(targetId);
        if (!panel) return;

        if (!loaded[targetId]) {
            fetchTabContent(panel, slug, page);
        } else {
            pushUrl(slug, page);
        }
    }

    function fetchTabContent(panel, slug, page, filterState) {
        const state = filterState || {};
        const filter = state.filter || 'all';
        const sortCol = (state.sortCol !== undefined && state.sortCol !== null) ? state.sortCol : null;
        const sortDir = state.sortDir || 'asc';

        let url = `/dashboard/tab/${slug}?page=${page}`;
        if (filter !== 'all') url += `&filter=${encodeURIComponent(filter)}`;
        if (sortCol !== null) url += `&sort_col=${sortCol}&sort_dir=${sortDir}`;

        panel.innerHTML = '<div class="tab-loading-placeholder">Loading…</div>';
        fetch(url)
            .then(r => {
                if (!r.ok) throw new Error(`HTTP ${r.status}`);
                return r.text();
            })
            .then(html => {
                panel.innerHTML = html;
                loaded[panel.id] = true;
                pushUrl(slug, page);
                initPanelInteractions(panel, slug);
            })
            .catch(() => {
                panel.innerHTML = '';
                showToast('Failed to load tab content. Please try again.', 'error');
            });
    }

    function pushUrl(slug, page) {
        const url = new URL(window.location);
        if (slug) {
            url.searchParams.set('tab', slug);
            if (page > 1) {
                url.searchParams.set('page', String(page));
            } else {
                url.searchParams.delete('page');
            }
        } else {
            url.searchParams.delete('tab');
            url.searchParams.delete('page');
        }
        history.replaceState({}, '', url);
    }

    // ── Wire up everything inside a freshly loaded panel ──
    function initPanelInteractions(panel, slug) {
        // Read server-rendered filter/sort state (present on paginated staff panels)
        const stateEl = panel.querySelector('.panel-tab-state');
        const filterState = stateEl ? {
            filter: stateEl.dataset.filter || 'all',
            sortCol: stateEl.dataset.sortCol !== '' ? parseInt(stateEl.dataset.sortCol) : null,
            sortDir: stateEl.dataset.sortDir || 'asc',
        } : { filter: 'all', sortCol: null, sortDir: 'asc' };

        // Re-apply sort indicator from server state
        if (stateEl && filterState.sortCol !== null) {
            const th = panel.querySelector(`table[id] thead th[data-sort="${filterState.sortCol}"]`);
            if (th) {
                const ind = document.createElement('span');
                ind.className = 'sort-ind';
                ind.textContent = filterState.sortDir === 'asc' ? ' ▲' : ' ▼';
                ind.style.fontSize = '10px';
                th.appendChild(ind);
            }
        }

        // Pagination buttons
        panel.querySelectorAll('.page-btn[data-page]').forEach(btn => {
            btn.addEventListener('click', () => {
                const page = parseInt(btn.dataset.page, 10);
                loaded[panel.id] = false;
                fetchTabContent(panel, slug, page, filterState);
            });
        });

        // Expand/collapse rows
        panel.querySelectorAll('.expand-btn').forEach(btn => {
            btn.addEventListener('click', e => {
                e.stopPropagation();
                const id = btn.dataset.appId;
                const row = panel.querySelector('#expand-' + id);
                if (!row) return;
                const wasHidden = row.hidden;
                panel.querySelectorAll('.app-row-expand').forEach(r => { r.hidden = true; });
                panel.querySelectorAll('.app-row-header').forEach(r => r.classList.remove('expanded'));
                panel.querySelectorAll('.expand-btn').forEach(b => { b.textContent = 'Expand'; });
                if (wasHidden) {
                    row.hidden = false;
                    btn.closest('tr').classList.add('expanded');
                    btn.textContent = 'Collapse';
                }
            });
        });

        // Chip filters: server-side re-fetch on paginated panels, client-side otherwise
        panel.querySelectorAll('.stats-row[data-filter-table]').forEach(group => {
            const table = panel.querySelector('#' + group.dataset.filterTable);
            const chips = group.querySelectorAll('[data-filter]');
            chips.forEach(chip => {
                chip.addEventListener('click', function () {
                    if (stateEl) {
                        const alreadyActive = this.classList.contains('chip-active');
                        const newFilter = alreadyActive ? 'all' : this.dataset.filter;
                        loaded[panel.id] = false;
                        fetchTabContent(panel, slug, 1, { ...filterState, filter: newFilter });
                    } else {
                        const alreadyActive = this.classList.contains('chip-active');
                        chips.forEach(c => c.classList.remove('chip-active'));
                        const filter = alreadyActive ? 'all' : this.dataset.filter;
                        if (!alreadyActive) this.classList.add('chip-active');
                        if (table) filterTableRows(table, filter);
                    }
                });
            });
        });

        // Sortable columns: server-side re-fetch on paginated panels, client-side otherwise
        panel.querySelectorAll('table[id]').forEach(table => {
            if (stateEl) {
                table.querySelectorAll('thead th[data-sort]').forEach(th => {
                    th.style.cursor = 'pointer';
                    th.title = 'Click to sort';
                    th.addEventListener('click', function () {
                        const col = parseInt(this.dataset.sort);
                        const isSameCol = filterState.sortCol === col;
                        const dir = (isSameCol && filterState.sortDir === 'asc') ? 'desc' : 'asc';
                        loaded[panel.id] = false;
                        fetchTabContent(panel, slug, 1, { ...filterState, sortCol: col, sortDir: dir });
                    });
                });
            } else {
                initSortableTable(table);
            }
        });

        // Tab-jump buttons inside lazy-loaded content (e.g. applicant track → submit)
        panel.querySelectorAll('.tab-jump').forEach(b => {
            b.addEventListener('click', () => {
                if (b.dataset.selectApp) {
                    sessionStorage.setItem('ygk_selected_app', b.dataset.selectApp);
                    loaded[b.dataset.target] = false; // force reload so selector pre-selects
                }
                const slug = b.dataset.tabSlug ||
                    document.getElementById(b.dataset.target)?.dataset.tabSlug || '';
                activatePanel(b.dataset.target, slug);
            });
        });

        // Intibak panel
        if (slug === 'intibak-table') initIntibakPanel(panel);

        // Enrolled checkbox inside fetched content
        const cb = panel.querySelector('#enrolled-dash');
        const univField = panel.querySelector('#univ-dash');
        if (cb && univField) {
            cb.addEventListener('change', () => {
                univField.style.display = cb.checked ? 'block' : 'none';
            });
        }

        // Multi-step application form
        initAppForm(panel);
    }

    // ── Multi-step form ──
    function initAppForm(container) {
        const appForm = container.querySelector('#app-form');
        if (!appForm) return;

        const steps = Array.from(appForm.querySelectorAll('.form-step'));
        const indicators = Array.from(container.querySelectorAll('.step-ind'));
        let currentStep = 0;

        function showStep(n) {
            steps.forEach((s, i) => s.classList.toggle('active', i === n));
            indicators.forEach((ind, i) => {
                ind.classList.toggle('active', i === n);
                ind.classList.toggle('done', i < n);
            });
            currentStep = n;
            if (n === steps.length - 1) populateReview();
        }

        function validateStep(n) {
            const step = steps[n];
            const inputs = step.querySelectorAll('input[required], select[required], textarea[required]');
            let ok = true;
            inputs.forEach(el => {
                el.style.borderColor = '';
                if (!el.value.trim()) { el.style.borderColor = '#ef4444'; ok = false; }
            });
            const gpaInput = step.querySelector('input[name="current_gpa"]');
            if (gpaInput && gpaInput.value) {
                const v = parseFloat(gpaInput.value);
                if (isNaN(v) || v < 0 || v > 4.0) { gpaInput.style.borderColor = '#ef4444'; ok = false; }
            }
            return ok;
        }

        appForm.querySelectorAll('.next-step').forEach(btn => {
            btn.addEventListener('click', () => { if (validateStep(currentStep)) showStep(currentStep + 1); });
        });
        appForm.querySelectorAll('.prev-step').forEach(btn => {
            btn.addEventListener('click', () => { if (currentStep > 0) showStep(currentStep - 1); });
        });

        function populateReview() {
            function val(name) {
                const el = appForm.querySelector(`[name="${name}"]`);
                if (!el) return '—';
                if (el.tagName === 'SELECT') return el.options[el.selectedIndex]?.text || '—';
                return el.value.trim() || '—';
            }
            const get = id => container.querySelector('#' + id);
            if (get('rv-program')) get('rv-program').textContent = val('target_program');
            if (get('rv-semester')) get('rv-semester').textContent = val('target_semester');
            if (get('rv-name')) get('rv-name').textContent = val('full_name');
            if (get('rv-id')) get('rv-id').textContent = val('id_number');
            if (get('rv-gpa')) get('rv-gpa').textContent = val('current_gpa');
            if (get('rv-univ')) get('rv-univ').textContent = val('source_university') || 'Not enrolled';
            const rvDocs = get('rv-docs');
            if (rvDocs) {
                rvDocs.innerHTML = '';
                appForm.querySelectorAll('input[type="file"]').forEach(fi => {
                    const row = document.createElement('div');
                    row.className = 'review-row';
                    const label = fi.closest('label')?.querySelector('.doc-upload-name')?.textContent || fi.name;
                    const file = fi.files && fi.files[0] ? fi.files[0].name : '(no file selected)';
                    row.innerHTML = `<span>${label}</span><span>${file}</span>`;
                    rvDocs.appendChild(row);
                });
            }
        }
    }

    // ── Shared helpers ──
    function filterTableRows(table, filter) {
        const rows = Array.from(table.querySelectorAll('tbody tr'));
        for (let i = 0; i < rows.length; i += 2) {
            const header = rows[i];
            const expand = rows[i + 1];
            const show = filter === 'all' || header.dataset.status === filter;
            header.style.display = show ? '' : 'none';
            if (expand) expand.style.display = show ? '' : 'none';
        }
    }

    function initSortableTable(table) {
        if (!table) return;
        const headers = table.querySelectorAll('thead th[data-sort]');
        let currentCol = null, ascending = true;
        headers.forEach(th => {
            th.style.cursor = 'pointer';
            th.title = 'Click to sort';
            th.addEventListener('click', function () {
                const col = parseInt(this.dataset.sort);
                ascending = (currentCol === col) ? !ascending : true;
                currentCol = col;
                headers.forEach(h => { const ind = h.querySelector('.sort-ind'); if (ind) h.removeChild(ind); });
                const ind = document.createElement('span');
                ind.className = 'sort-ind';
                ind.textContent = ascending ? ' ▲' : ' ▼';
                ind.style.fontSize = '10px';
                this.appendChild(ind);
                const tbody = table.querySelector('tbody');
                const rows = Array.from(tbody.querySelectorAll('tr'));
                const pairs = [];
                for (let i = 0; i < rows.length; i += 2) pairs.push([rows[i], rows[i + 1]]);
                pairs.sort((a, b) => {
                    const aT = (a[0].cells[col] ? a[0].cells[col].textContent : '').trim();
                    const bT = (b[0].cells[col] ? b[0].cells[col].textContent : '').trim();
                    const aN = parseFloat(aT), bN = parseFloat(bT);
                    if (!isNaN(aN) && !isNaN(bN)) return ascending ? aN - bN : bN - aN;
                    return ascending ? aT.localeCompare(bT) : bT.localeCompare(aT);
                });
                pairs.forEach(pair => { tbody.appendChild(pair[0]); tbody.appendChild(pair[1]); });
            });
        });
    }

    // ── Intibak Panel ──
    function initIntibakPanel(panel) {
        const curriculumEl = panel.querySelector('#intibak-curriculum-data');
        const appsEl = panel.querySelector('#intibak-apps-data');
        if (!curriculumEl || !appsEl) return;

        const curriculum = JSON.parse(curriculumEl.dataset.json);
        const apps = JSON.parse(appsEl.dataset.json);
        if (!apps.length) return;

        const state = {};
        apps.forEach(a => { state[a.id] = { oldCourses: [], newCourses: [] }; });

        let currentAppId = null;
        let connectMode   = false;
        let selectedLeft  = new Set();
        let selectedRight = new Set();

        const selector          = panel.querySelector('#intibak-app-selector');
        const appBar            = panel.querySelector('#intibak-app-bar');
        const transcriptBtn     = panel.querySelector('#bar-transcript-btn');
        const noTranscriptNote  = panel.querySelector('#bar-no-transcript');
        const leftTbody         = panel.querySelector('#intibak-left-tbody');
        const rightTbody        = panel.querySelector('#intibak-right-tbody');
        const neededTbody       = panel.querySelector('#intibak-needed-tbody');
        const dropdown          = panel.querySelector('#curriculum-dropdown');
        const connectBtn        = panel.querySelector('#connect-btn');
        const confirmConnectBtn = panel.querySelector('#confirm-connect-btn');
        const cancelConnectBtn  = panel.querySelector('#cancel-connect-btn');
        const connectHint       = panel.querySelector('#connect-hint');
        const intibakLayout     = panel.querySelector('.intibak-layout');

        // ── Grade helpers ──
        function gradeToGPA(grade) {
            const g = String(grade || '').trim().toUpperCase();
            const TK = { AA: 4.0, BA: 3.5, BB: 3.0, CB: 2.5, CC: 2.0, DC: 1.5, DD: 1.0, FD: 0.5, FF: 0.0 };
            if (TK[g] !== undefined) return TK[g];
            const n = parseFloat(g);
            if (isNaN(n)) return null;
            if (n > 4.0) { // 0–100 scale
                if (n >= 90) return 4.0;
                if (n >= 85) return 3.5;
                if (n >= 80) return 3.0;
                if (n >= 75) return 2.5;
                if (n >= 70) return 2.0;
                if (n >= 65) return 1.5;
                if (n >= 60) return 1.0;
                if (n >= 50) return 0.5;
                return 0.0;
            }
            return Math.max(0, Math.min(4.0, n)); // already 0–4 scale
        }

        function gpaToLetter(gpa) {
            if (gpa === null) return null;
            if (gpa >= 4.0) return 'AA';
            if (gpa >= 3.5) return 'BA';
            if (gpa >= 3.0) return 'BB';
            if (gpa >= 2.5) return 'CB';
            if (gpa >= 2.0) return 'CC';
            if (gpa >= 1.5) return 'DC';
            if (gpa >= 1.0) return 'DD';
            if (gpa >= 0.5) return 'FD';
            return 'FF';
        }

        // Weighted average by credits of the mapped left courses
        function calcRightGrade(leftIndices) {
            const old = state[currentAppId].oldCourses;
            const graded = leftIndices.map(i => old[i]).filter(c => c && c.grade && c.grade.trim());
            if (!graded.length) return null;
            const pts = graded.map(c => ({ gpa: gradeToGPA(c.grade), cr: parseFloat(c.credits) || 1 }))
                               .filter(p => p.gpa !== null);
            if (!pts.length) return null;
            const totCr = pts.reduce((s, p) => s + p.cr, 0);
            const wsum  = pts.reduce((s, p) => s + p.gpa * p.cr, 0);
            return gpaToLetter(totCr > 0 ? wsum / totCr : 0);
        }

        function gradeClass(letter) {
            if (!letter) return '';
            const tier = { AA: 'gd-aa', BA: 'gd-ba', BB: 'gd-bb', CB: 'gd-cb', CC: 'gd-cc',
                           DC: 'gd-dc', DD: 'gd-dd', FD: 'gd-fd', FF: 'gd-ff' };
            return tier[letter] || '';
        }

        // ── Helpers ──
        function esc(s) {
            return String(s || '').replace(/[&<>"']/g, m =>
                ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[m]));
        }

        function getCurriculum(appId) {
            const app = apps.find(a => a.id == appId);
            const prog = app ? app.target_program : '';
            return curriculum[prog] || curriculum['Computer Engineering'] || [];
        }

        // ── Row builders ──
        function makeLeftRow(i, c) {
            const sel = connectMode && selectedLeft.has(i);
            const tr = document.createElement('tr');
            tr.dataset.leftIdx = i;
            if (sel) tr.classList.add('intibak-row-selected', 'intibak-sel-left');
            if (connectMode) tr.classList.add('intibak-row-selectable');
            tr.innerHTML =
                `<td><button class="intibak-del-btn" data-side="left" data-idx="${i}" title="Remove">×</button></td>` +
                `<td><input class="intibak-input" type="text" value="${esc(c.name)}" placeholder="Course name…" data-field="name" data-idx="${i}" data-side="left"></td>` +
                `<td><input class="intibak-input small" type="number" value="${c.credits||''}" placeholder="0" data-field="credits" data-idx="${i}" data-side="left" min="0" max="20"></td>` +
                `<td><input class="intibak-input small" type="number" value="${c.akts||''}" placeholder="0" data-field="akts" data-idx="${i}" data-side="left" min="0" max="30"></td>` +
                `<td><input class="intibak-input small intibak-grade-input" type="text" value="${esc(c.grade||'')}" placeholder="AA" data-field="grade" data-idx="${i}" data-side="left" maxlength="3"></td>`;
            return tr;
        }

        function makeRightRow(i, c) {
            const sel    = connectMode && selectedRight.has(i);
            const linked = c.linkedLeft && c.linkedLeft.length > 0;
            const gc     = gradeClass(c.grade);
            const gradeHtml = linked && c.grade
                ? `<span class="intibak-grade-badge ${gc}">${esc(c.grade)}</span>`
                : `<span class="intibak-grade-empty">—</span>`;
            const linkBadge = linked
                ? `<span class="intibak-link-badge" title="Linked to ${c.linkedLeft.length} left course(s)">↔${c.linkedLeft.length}</span> `
                : '';
            const tr = document.createElement('tr');
            tr.dataset.rightIdx = i;
            if (sel)    tr.classList.add('intibak-row-selected', 'intibak-sel-right');
            if (linked) tr.classList.add('intibak-row-linked');
            if (connectMode) tr.classList.add('intibak-row-selectable');
            tr.innerHTML =
                `<td><button class="intibak-del-btn" data-side="right" data-idx="${i}" title="Remove">×</button></td>` +
                `<td>${linkBadge}<span class="intibak-code">${esc(c.code)}</span></td>` +
                `<td>${esc(c.name)}</td>` +
                `<td>${c.credits}</td>` +
                `<td>${c.akts}</td>` +
                `<td>${gradeHtml}</td>`;
            return tr;
        }

        // ── Render ──
        function renderAll() { renderLeft(); renderRight(); renderNeeded(); }

        function renderLeft() {
            const courses = state[currentAppId].oldCourses;
            leftTbody.innerHTML = '';
            if (!courses.length) {
                leftTbody.innerHTML = '<tr><td colspan="5" style="text-align:center;color:#9ca3af;padding:18px;font-size:13px;">Press + to add courses</td></tr>';
                return;
            }
            courses.forEach((c, i) => leftTbody.appendChild(makeLeftRow(i, c)));
        }

        function renderRight() {
            const courses = state[currentAppId].newCourses;
            rightTbody.innerHTML = '';
            if (!courses.length) {
                rightTbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#9ca3af;padding:18px;font-size:13px;">Add courses from curriculum</td></tr>';
                return;
            }
            courses.forEach((c, i) => rightTbody.appendChild(makeRightRow(i, c)));
        }

        function renderNeeded() {
            const added = new Set(state[currentAppId].newCourses.map(c => c.code));
            const needed = getCurriculum(currentAppId).filter(c => !added.has(c.code));
            neededTbody.innerHTML = '';
            if (!needed.length) {
                neededTbody.innerHTML = '<tr><td colspan="4" style="text-align:center;color:#059669;padding:16px;font-size:13px;">All curriculum courses matched ✓</td></tr>';
                return;
            }
            needed.forEach(c => {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td><span class="intibak-code">${esc(c.code)}</span></td><td>${esc(c.name)}</td><td>${c.credits}</td><td>${c.akts}</td>`;
                neededTbody.appendChild(tr);
            });
        }

        function updateDropdown() {
            if (!currentAppId) return;
            const added = new Set(state[currentAppId].newCourses.map(c => c.code));
            const available = getCurriculum(currentAppId).filter(c => !added.has(c.code));
            dropdown.innerHTML = '';
            if (!available.length) { dropdown.innerHTML = '<div class="curriculum-empty">All courses added</div>'; return; }
            available.forEach(c => {
                const div = document.createElement('div');
                div.className = 'curriculum-item';
                div.dataset.code = c.code;
                div.innerHTML =
                    `<span class="intibak-code">${esc(c.code)}</span>` +
                    `<span style="flex:1">${esc(c.name)}</span>` +
                    `<span class="intibak-meta">${c.credits}cr&nbsp;/&nbsp;${c.akts}AKTS</span>`;
                dropdown.appendChild(div);
            });
        }

        // Recalculate all right courses that depend on a changed left index
        function recalcRight(leftIdx) {
            let changed = false;
            state[currentAppId].newCourses.forEach(c => {
                if (c.linkedLeft && c.linkedLeft.includes(leftIdx)) {
                    c.grade = calcRightGrade(c.linkedLeft);
                    changed = true;
                }
            });
            if (changed) renderRight();
        }

        // ── Applicant selection ──
        function selectApp(appId) {
            currentAppId = appId;
            const app = apps.find(a => a.id == appId);
            if (!app) return;
            panel.querySelector('#bar-name').textContent    = app.full_name;
            panel.querySelector('#bar-univ').textContent    = app.source_university || '—';
            panel.querySelector('#bar-program').textContent = app.target_program || '—';
            appBar.style.display = 'flex';
            if (app.transcript_doc_id) {
                transcriptBtn.href = `/api/ygk/view-document/${app.transcript_doc_id}`;
                transcriptBtn.style.display = '';
                noTranscriptNote.style.display = 'none';
            } else {
                transcriptBtn.style.display = 'none';
                noTranscriptNote.style.display = '';
            }
            exitConnectMode(false); // exit without re-render
            renderAll();
        }

        // ── Connect mode ──
        function enterConnectMode() {
            connectMode   = true;
            selectedLeft  = new Set();
            selectedRight = new Set();
            if (connectBtn)        connectBtn.style.display        = 'none';
            if (confirmConnectBtn) confirmConnectBtn.style.display = '';
            if (cancelConnectBtn)  cancelConnectBtn.style.display  = '';
            if (connectHint)       connectHint.style.display       = '';
            if (intibakLayout)     intibakLayout.classList.add('intibak-connecting');
            renderAll(); // re-render rows with selectable class
        }

        function exitConnectMode(rerender = true) {
            connectMode   = false;
            selectedLeft  = new Set();
            selectedRight = new Set();
            if (connectBtn)        connectBtn.style.display        = '';
            if (confirmConnectBtn) confirmConnectBtn.style.display = 'none';
            if (cancelConnectBtn)  cancelConnectBtn.style.display  = 'none';
            if (connectHint)       connectHint.style.display       = 'none';
            if (intibakLayout)     intibakLayout.classList.remove('intibak-connecting');
            if (rerender) renderAll();
        }

        function confirmConnection() {
            if (!currentAppId || !selectedLeft.size || !selectedRight.size) {
                exitConnectMode();
                return;
            }
            const nc = state[currentAppId].newCourses;
            selectedRight.forEach(ri => {
                if (!nc[ri]) return;
                nc[ri].linkedLeft = [...selectedLeft];
                nc[ri].grade      = calcRightGrade([...selectedLeft]);
            });
            exitConnectMode();
        }

        // ── Events: input ──
        panel.addEventListener('input', e => {
            const inp = e.target;
            if (!inp.classList.contains('intibak-input') || !currentAppId) return;
            const i    = parseInt(inp.dataset.idx);
            const field = inp.dataset.field;
            const side  = inp.dataset.side;
            const arr   = side === 'left' ? state[currentAppId].oldCourses : state[currentAppId].newCourses;
            if (arr[i] === undefined) return;
            if (field === 'name') {
                arr[i].name = inp.value;
            } else if (field === 'grade' && side === 'left') {
                arr[i].grade = inp.value.toUpperCase();
                inp.value    = arr[i].grade;
                recalcRight(i);
            } else {
                arr[i][field] = parseFloat(inp.value) || 0;
                if (field === 'credits' && side === 'left') recalcRight(i);
            }
        });

        // ── Events: click ──
        panel.addEventListener('click', e => {
            // Connect mode: row selection (skip if clicking buttons or inputs)
            if (connectMode && !e.target.closest('.intibak-del-btn') && e.target.tagName !== 'INPUT' && e.target.tagName !== 'BUTTON') {
                const lr = e.target.closest('[data-left-idx]');
                if (lr) {
                    const idx = parseInt(lr.dataset.leftIdx);
                    if (selectedLeft.has(idx)) { selectedLeft.delete(idx); lr.classList.remove('intibak-row-selected', 'intibak-sel-left'); }
                    else { selectedLeft.add(idx); lr.classList.add('intibak-row-selected', 'intibak-sel-left'); }
                    return;
                }
                const rr = e.target.closest('[data-right-idx]');
                if (rr) {
                    const idx = parseInt(rr.dataset.rightIdx);
                    if (selectedRight.has(idx)) { selectedRight.delete(idx); rr.classList.remove('intibak-row-selected', 'intibak-sel-right'); }
                    else { selectedRight.add(idx); rr.classList.add('intibak-row-selected', 'intibak-sel-right'); }
                    return;
                }
            }

            // Connect/Confirm/Cancel buttons
            if (e.target.id === 'connect-btn')        { enterConnectMode(); return; }
            if (e.target.id === 'confirm-connect-btn') { confirmConnection(); return; }
            if (e.target.id === 'cancel-connect-btn')  { exitConnectMode(); return; }

            // Delete row
            const del = e.target.closest('.intibak-del-btn');
            if (del && currentAppId) {
                const i    = parseInt(del.dataset.idx);
                const side = del.dataset.side;
                if (side === 'left') {
                    state[currentAppId].oldCourses.splice(i, 1);
                    // Fix right-course linkedLeft indices
                    state[currentAppId].newCourses.forEach(c => {
                        if (!c.linkedLeft || !c.linkedLeft.length) return;
                        c.linkedLeft = c.linkedLeft.filter(li => li !== i).map(li => li > i ? li - 1 : li);
                        c.grade = c.linkedLeft.length ? calcRightGrade(c.linkedLeft) : null;
                    });
                } else {
                    state[currentAppId].newCourses.splice(i, 1);
                }
                renderAll();
                if (side === 'right') updateDropdown();
                return;
            }

            // Add left row
            if (e.target.id === 'add-left-row' && currentAppId) {
                state[currentAppId].oldCourses.push({ name: '', credits: 0, akts: 0, grade: '' });
                renderLeft();
                const inputs = leftTbody.querySelectorAll('.intibak-input[data-field="name"]');
                if (inputs.length) inputs[inputs.length - 1].focus();
                return;
            }

            // Toggle curriculum dropdown
            if (e.target.id === 'add-right-btn') { updateDropdown(); dropdown.classList.toggle('dropdown-open'); return; }

            // Pick from curriculum
            const item = e.target.closest('.curriculum-item');
            if (item && currentAppId) {
                const course = getCurriculum(currentAppId).find(c => c.code === item.dataset.code);
                if (course) {
                    state[currentAppId].newCourses.push({ ...course, grade: null, linkedLeft: [] });
                    dropdown.classList.remove('dropdown-open');
                    renderRight();
                    renderNeeded();
                    updateDropdown();
                }
                return;
            }

            // Close dropdown if clicking outside
            if (!e.target.closest('.curriculum-dropdown-wrap')) dropdown.classList.remove('dropdown-open');
        });

        // ── Selector ──
        if (selector) {
            selector.addEventListener('change', () => { selectApp(selector.value); updateDropdown(); });
            const preSelected = sessionStorage.getItem('ygk_selected_app');
            if (preSelected) {
                sessionStorage.removeItem('ygk_selected_app');
                if (apps.find(a => a.id == preSelected)) selector.value = preSelected;
            }
            if (selector.value) { selectApp(selector.value); updateDropdown(); }
        }
    }

    // ── Static tab buttons (main nav) ──
    tabButtons.forEach(b => {
        b.addEventListener('click', () => activatePanel(b.dataset.target, b.dataset.tabSlug));
    });

    // Tab-jump in the main cards panel (these are in the static DOM)
    document.querySelectorAll('#panel-main .tab-jump').forEach(b => {
        b.addEventListener('click', () => activatePanel(b.dataset.target, b.dataset.tabSlug));
    });

    // H1 title → back to main
    const dashTitle = document.getElementById('dash-title');
    if (dashTitle) dashTitle.addEventListener('click', () => activatePanel('panel-main', ''));

    // ── Activate tab from URL on load ──
    const urlParams = new URLSearchParams(window.location.search);
    const initSlug = urlParams.get('tab');
    const initPage = Math.max(1, parseInt(urlParams.get('page') || '1', 10));

    if (initSlug) {
        const btn = Array.from(tabButtons).find(b => b.dataset.tabSlug === initSlug);
        if (btn) activatePanel(btn.dataset.target, initSlug, initPage);
    }

});
