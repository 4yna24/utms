document.addEventListener('DOMContentLoaded', () => {

    // ── Tab switching ──
    const tabButtons = document.querySelectorAll('.tab-button');
    const panels = document.querySelectorAll('.workspace-panel');

    function activatePanel(targetId) {
        panels.forEach(p => p.classList.toggle('active', p.id === targetId));
        tabButtons.forEach(b => {
            const active = b.dataset.target === targetId;
            b.classList.toggle('active', active);
            b.setAttribute('aria-pressed', String(active));
        });
    }

    tabButtons.forEach(b => b.addEventListener('click', () => activatePanel(b.dataset.target)));

    // Tab-jump buttons (in cards and tracker)
    document.querySelectorAll('.tab-jump').forEach(b => {
        b.addEventListener('click', () => activatePanel(b.dataset.target));
    });

    // Clicking the H1 dashboard title goes back to main
    const dashTitle = document.getElementById('dash-title');
    if (dashTitle) {
        dashTitle.addEventListener('click', () => activatePanel('panel-main'));
    }

    // ── Enrolled checkbox → show/hide university field ──
    [['enrolled-dash', 'univ-dash'], ['enrolled-standalone', 'univ-standalone']].forEach(([cbId, fieldId]) => {
        const cb = document.getElementById(cbId);
        const field = document.getElementById(fieldId);
        if (cb && field) {
            cb.addEventListener('change', () => {
                field.style.display = cb.checked ? 'block' : 'none';
            });
        }
    });

    // ── Multi-step application form ──
    const appForm = document.getElementById('app-form');
    if (appForm) {
        const steps = Array.from(appForm.querySelectorAll('.form-step'));
        const indicators = Array.from(document.querySelectorAll('.step-ind'));
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
                if (!el.value.trim()) {
                    el.style.borderColor = '#ef4444';
                    ok = false;
                }
            });
            // GPA range check
            const gpaInput = step.querySelector('input[name="current_gpa"]');
            if (gpaInput && gpaInput.value) {
                const v = parseFloat(gpaInput.value);
                if (isNaN(v) || v < 0 || v > 4.0) {
                    gpaInput.style.borderColor = '#ef4444';
                    ok = false;
                }
            }
            // File inputs
            const fileInputs = step.querySelectorAll('input[type="file"][required]');
            fileInputs.forEach(el => {
                el.style.outline = '';
                if (!el.files || el.files.length === 0) {
                    el.style.outline = '2px solid #ef4444';
                    ok = false;
                }
            });
            return ok;
        }

        appForm.querySelectorAll('.next-step').forEach(btn => {
            btn.addEventListener('click', () => {
                if (validateStep(currentStep)) showStep(currentStep + 1);
            });
        });

        appForm.querySelectorAll('.prev-step').forEach(btn => {
            btn.addEventListener('click', () => {
                if (currentStep > 0) showStep(currentStep - 1);
            });
        });

        function populateReview() {
            function val(name) {
                const el = appForm.querySelector(`[name="${name}"]`);
                if (!el) return '—';
                if (el.tagName === 'SELECT') return el.options[el.selectedIndex]?.text || '—';
                return el.value.trim() || '—';
            }

            const rvProgram = document.getElementById('rv-program');
            const rvSemester = document.getElementById('rv-semester');
            const rvName = document.getElementById('rv-name');
            const rvId = document.getElementById('rv-id');
            const rvGpa = document.getElementById('rv-gpa');
            const rvUniv = document.getElementById('rv-univ');
            const rvDocs = document.getElementById('rv-docs');

            if (rvProgram) rvProgram.textContent = val('target_program');
            if (rvSemester) rvSemester.textContent = val('target_semester');
            if (rvName) rvName.textContent = val('full_name');
            if (rvId) rvId.textContent = val('id_number');
            if (rvGpa) rvGpa.textContent = val('current_gpa');
            const cb = appForm.querySelector('[name="is_currently_enrolled"]');
            const univ = val('source_university');
            if (rvUniv) rvUniv.textContent = (cb && cb.checked && univ !== '—') ? univ : 'Not enrolled';

            if (rvDocs) {
                const fileInputs = appForm.querySelectorAll('input[type="file"]');
                rvDocs.innerHTML = '';
                fileInputs.forEach(fi => {
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

    // ── OIDB expand rows ──
    document.querySelectorAll('.expand-btn').forEach(btn => {
        btn.addEventListener('click', e => {
            e.stopPropagation();
            const id = btn.dataset.appId;
            const row = document.getElementById('expand-' + id);
            if (!row) return;
            const wasHidden = row.hidden;

            document.querySelectorAll('.app-row-expand').forEach(r => { r.hidden = true; });
            document.querySelectorAll('.app-row-header').forEach(r => r.classList.remove('expanded'));
            document.querySelectorAll('.expand-btn').forEach(b => { b.textContent = 'Expand'; });

            if (wasHidden) {
                row.hidden = false;
                btn.closest('tr').classList.add('expanded');
                btn.textContent = 'Collapse';
            }
        });
    });

});
