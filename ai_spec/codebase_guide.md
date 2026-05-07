# Codebase Guide

This file explains where things live and why, so that new code goes in the right layer the first time.

---

## Layer Overview

```
app/
├── classes/        ← business logic (role classes)
├── database/       ← DB interface abstraction (used by auth)
├── models/         ← SQLAlchemy ORM models (data shape only)
├── routes/         ← thin HTTP handlers (one file per role)
├── static/
│   ├── css/        ← dashboard.css, main.css, auth.css
│   └── js/         ← dashboard.js (all dashboard interactivity)
├── templates/
│   ├── partials/   ← dashboard panel fragments, one per tab
│   └── *.html      ← standalone pages + base
└── config.py       ← constants, PHASE1_TABS, tab→partial mapping
```

---

## The Three Layers and What Goes Where

### `classes/` — Business Logic
This is where decisions happen. Role classes (`Oidb`, `DeanOffice`, `Applicant`, etc.) own all domain logic: querying applications, validating state transitions, committing changes.

- **Add logic here, not in routes.**
- Each role class is instantiated per request using session data: `DeanOffice(user_id, email, "dean")`.
- DB imports (`from .. import db`, `from ..models import Application`) go inside methods to avoid circular imports.
- `classes/interfaces.py` defines abstract base classes (`IReviewer`, `IDocumentHandler`) that role classes implement.

### `routes/` — HTTP Handlers Only
Routes parse the request, call one class method, flash the result, and return.

```python
# correct: route calls class method, does nothing else
def forward_to_ygk(application_id):
    ok, msg = _svc().forward_to_ygk(application_id)
    flash(msg, "success" if ok else "error")
    return redirect(url_for("dean_api.check_applicants"))
```

- **Do not put DB queries or status logic in routes.**
- Each route file has a `_svc()` helper that instantiates the role class from session.
- `dashboard.py` uses `_get_role_data(role_slug, user_id, email)` to delegate data loading to the right class.

### `models/` — Data Shape Only
SQLAlchemy ORM models (`User`, `Application`, `ApplicationDocument`). They define columns, relationships, and password hashing. No business logic lives here.

---

## How the Dashboard Tab System Works

Adding a new tab requires exactly three touches:

1. **`config.py` → `PHASE1_TABS`** — add the tab entry with a `"partial"` key pointing to the template fragment:
   ```python
   {"title": "My Tab", "description": "...", "partial": "partials/panel_myrole_mytab.html"}
   ```

2. **`templates/partials/panel_<role>_<tab>.html`** — create the panel content. It has access to every variable passed to `render_template` in `dashboard.py`.

3. **`routes/dashboard.py` → `_get_role_data()`** — if the tab needs data, add a branch here that calls the role class method and returns a dict (e.g., `{"my_applications": svc.get_things()}`).

`dashboard.html` itself does not need to change. It just does `{% include tab.partial %}` for every tab.

---

## How a Request Flows

```
Browser
  → route function (routes/<role>.py)
      → _svc() instantiates role class (classes/users.py)
          → class method queries/updates via SQLAlchemy (models/)
      → flash message + redirect  OR  render_template
          → dashboard.html shell
              → {% include tab.partial %} (templates/partials/)
```

For the dashboard specifically: `dashboard.py` calls `_get_role_data()` which calls the class, and all returned data is spread into `render_template`. Partials reference those variables directly.

---

## Dashboard JavaScript (`static/js/dashboard.js`)

All interactive behavior for the dashboard lives here:
- **Tab switching** — `.tab-button` clicks toggle `.workspace-panel.active`
- **Chip filters** — any `.stats-row[data-filter-table="<id>"]` auto-wires its `[data-filter]` chips to filter the named table by `data-status` on header rows
- **Column sort** — any `<table id="...">` with `<th data-sort="N">` gets clickable sort (row-pairs kept together during sort so expand rows stay linked)
- **Expand rows** — `.expand-btn` toggles `.app-row-expand` visibility; only one open at a time

To add filter chips to a new table: put `data-filter-table="your-table-id"` on the `.stats-row` container, add `data-filter="<status_value>"` on each chip, and `data-status="{{ app.status }}"` on each header `<tr>`.

---

## Standalone Pages vs. Dashboard

Routes like `/api/oidb/check-documents` and `/api/dean/check-applicants` render standalone templates (`oidb_check_documents.html`, `dean_check_applicants.html`). These exist for direct URL access but are **not** the primary UI — the dashboard is. Standalone pages have their own inline JS for sort; `dashboard.js` only runs on the dashboard.

---

## Config as the Single Source of Truth for Tabs

`config.py` is the only place that defines what tabs exist per role, what they're called, and which partial they render. If a tab is renamed or reordered, change it here only.

The `"partial": None` entries in `PHASE1_TABS` are tabs that fall back to "coming soon" text — they have no panel content yet.
