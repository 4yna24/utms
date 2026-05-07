# Codebase Guide

This file explains where things live and why, so that new code goes in the right layer the first time.

---

## Layer Overview

```
app/
├── classes/
│   ├── users.py        ← role classes (Applicant, DeanOffice, Oidb, Ydyo, YGK)
│   ├── auth.py         ← AuthClass (register, authenticate, validate_credentials)
│   ├── interfaces.py   ← IReviewer, IDocumentHandler abstract bases
│   └── entities/       ← domain dataclasses (Application, Document, IntibakTable)
│       ├── application.py
│       ├── intibak.py
│       └── __init__.py
├── database/       ← DB interface abstraction (used by auth)
├── models/         ← SQLAlchemy ORM models (data shape only)
├── routes/         ← thin HTTP handlers (one file per role)
├── static/
│   ├── css/        ← dashboard.css, main.css, auth.css
│   └── js/         ← dashboard.js (all dashboard interactivity)
├── templates/
│   ├── partials/   ← dashboard panel fragments, one per tab
│   └── *.html      ← standalone pages + base
├── __init__.py     ← create_app(), SQLite migration helpers
└── config.py       ← PHASE1_TABS, reference-data constants, feature flags
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

## Role Implementation Checklist

| Role | Class file | Route file | Dashboard partial | `_get_role_data` branch |
|------|-----------|-----------|-------------------|------------------------|
| Applicant | `classes/users.py` | `routes/applicant.py` | `panel_applicant_*.html` | ✓ |
| OIDB | `classes/users.py` | `routes/oidb.py` | `panel_oidb_documents.html` | ✓ |
| Dean | `classes/users.py` | `routes/dean.py` | `panel_dean_applications.html` | ✓ |
| YDYO | `classes/users.py` | `routes/ydyo.py` | `panel_ydyo_documents.html` | ✓ |
| YGK | `classes/users.py` | `routes/ygk.py` | — (partial: None) | — |

---

## Standalone Pages vs. Dashboard

Routes like `/api/oidb/check-documents` and `/api/dean/check-applicants` render standalone templates (`oidb_check_documents.html`, `dean_check_applicants.html`). These exist for direct URL access but are **not** the primary UI — the dashboard is. Standalone pages have their own inline JS for sort; `dashboard.js` only runs on the dashboard.

---

## Config as the Single Source of Truth

`config.py` owns three categories of constants:

**Tab definitions** (`PHASE1_TABS`) — what tabs exist per role, their titles, endpoints, and which partial they render. Change tab names or order here only. `"partial": None` entries fall back to "coming soon" text.

**Reference data** — lists that populate dropdowns in templates:
- `AVAILABLE_PROGRAMS` — applicant target programs
- `AVAILABLE_SEMESTERS` — available intake semesters
- `AVAILABLE_FACULTIES` — faculty names shown in Dean's forward-to-YGK dropdown

These are passed to every `render_template` call in `dashboard.py` so all partials can access them. Standalone pages (e.g. `routes/dean.py`) import and pass them explicitly.

**Feature flags** — `APPLICATION_SUBMISSION_PERIOD_OPEN`, `APPLICATION_CANCELLATION_ALLOWED`, `APPLICATION_RESUBMISSION_ALLOWED`. Flip these to open/close periods without touching logic.

---

## Adding a New Column to Application

New columns require two changes or existing databases will break on startup:

1. **`models/application.py`** — add the `db.Column(...)` declaration.
2. **`app/__init__.py` → `_ensure_application_new_columns()`** — add the column name and its SQLite type string to the `additions` dict.

The helper runs `ALTER TABLE application ADD COLUMN …` for any missing column at startup, keeping existing SQLite files compatible.
