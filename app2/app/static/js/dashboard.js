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

    function fetchTabContent(panel, slug, page) {
        panel.innerHTML = '<div class="tab-loading-placeholder">Loading…</div>';
        fetch(`/dashboard/tab/${slug}?page=${page}`)
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
        // Pagination buttons
        panel.querySelectorAll('.page-btn[data-page]').forEach(btn => {
            btn.addEventListener('click', () => {
                const page = parseInt(btn.dataset.page, 10);
                loaded[panel.id] = false;
                fetchTabContent(panel, slug, page);
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

        // Chip filters (filter rows in current page only)
        panel.querySelectorAll('.stats-row[data-filter-table]').forEach(group => {
            const table = panel.querySelector('#' + group.dataset.filterTable);
            if (!table) return;
            const chips = group.querySelectorAll('[data-filter]');
            chips.forEach(chip => {
                chip.addEventListener('click', function () {
                    const alreadyActive = this.classList.contains('chip-active');
                    chips.forEach(c => c.classList.remove('chip-active'));
                    const filter = alreadyActive ? 'all' : this.dataset.filter;
                    if (!alreadyActive) this.classList.add('chip-active');
                    filterTableRows(table, filter);
                });
            });
        });

        // Sortable columns
        panel.querySelectorAll('table[id]').forEach(table => initSortableTable(table));

        // Tab-jump buttons inside lazy-loaded content (e.g. applicant track → submit)
        panel.querySelectorAll('.tab-jump').forEach(b => {
            b.addEventListener('click', () => {
                const slug = b.dataset.tabSlug ||
                    document.getElementById(b.dataset.target)?.dataset.tabSlug || '';
                activatePanel(b.dataset.target, slug);
            });
        });

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
