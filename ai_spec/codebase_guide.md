# Codebase Guide

This file explains where things live and why, so that new code goes in the right layer the first time. UTMS uses a three-layer architecture: **Services** (business orchestration) → **Classes** (domain logic) → **Repositories** (data access).

---

## Layer Overview

```
app/
├── core/
│   ├── result.py       ← OperationResult[T], ErrorCode enum (NO exceptions)
│   └── __init__.py
├── services/           ← Service layer
│   ├── base_service.py ← BaseService with error(), ok(), validate_required_fields()
│   ├── application_service.py ← Submit, resubmit, cancel operations
│   ├── auth_service.py ← Login, register, password_reset
│   ├── user_service.py ← User operations
│   └── __init__.py
├── classes/            ← Role classes with business logic
│   ├── users/
│   │   ├── base.py     ← Abstract User class
│   │   ├── admin.py        ← Admin role (user mgmt, config, DB backup/restore)
│   │   ├── applicant.py    ← Applicant role (submit, track)
│   │   ├── dean.py         ← DeanOffice role (review, return to applicant/OIDB/YDYO, forward to YGK)
│   │   ├── oidb.py         ← Oidb role (document verification)
│   │   ├── ydyo.py         ← Ydyo role (prep school marking)
│   │   ├── ygk.py          ← YGK role (approval)
│   │   └── __init__.py
│   ├── auth.py         ← Auth class (credentials, tokens)
│   └── interfaces.py   ← IReviewer, IDocumentHandler abstract bases
├── database/           ← Repository pattern
│   ├── application_repository.py ← ApplicationRepository (all ApplicationORM queries)
│   ├── interfaces.py   ← ILowLevelDatabase, IHighLevelDatabase, IUserRepository
│   ├── adapters.py     ← SQLAlchemyUserDataService (implements IUserRepository)
│   └── __init__.py
├── models/             ← SQLAlchemy ORM (data shape only, no logic)
│   ├── user.py         ← UserORM
│   ├── application.py  ← ApplicationORM, ApplicationDocumentORM
│   └── __init__.py
├── routes/             ← Thin HTTP controllers
│   ├── admin.py        ← Admin API (role changes, backup, restore)
│   ├── auth.py         ← Login, register endpoints (includes /auth/admin/login)
│   ├── applicant.py    ← Submit, resubmit, cancel (uses ApplicationService)
│   ├── dean.py         ← Review, return to applicant/OIDB/YDYO, forward to YGK
│   ├── oidb.py         ← Verify docs, forward to YDYO
│   ├── ydyo.py         ← Mark prep school, forward
│   ├── ygk.py          ← Approve applications
│   ├── dashboard.py    ← Dashboard page load, tab data gathering
│   ├── common.py       ← Shared decorators (@login_required, @role_required)
│   └── __init__.py
├── cli.py              ← Flask CLI management commands (init-admin, seed-db)
├── static/
│   ├── css/
│   │   ├── main.css        ← Toast styling, global layout
│   │   ├── auth.css        ← Auth page centering
│   │   └── dashboard.css   ← Dashboard tab system
│   └── js/
│       └── dashboard.js    ← Tab switching, filters, sorting, expand rows
├── templates/
│   ├── base.html       ← Page shell with nav, flash messages
│   ├── dashboard.html  ← Tab system (auto-includes partials)
│   ├── login.html, register.html, etc. ← Standalone pages
│   └── partials/       ← Dashboard tab content fragments
│       ├── panel_applicant_*.html
│       ├── panel_oidb_documents.html
│       ├── panel_admin_users.html
│       ├── panel_admin_config.html
│       ├── panel_admin_database.html
│       └── ...
├── __init__.py         ← create_app(), db initialization, auto-fingerprint listener
└── config.py           ← PHASE1_TABS, AVAILABLE_PROGRAMS, feature flags
```

The project root also has:
- `run.py` — Flask app entry point
- `entrypoint.sh` — Docker startup script (runs `init-admin` then starts server)
- `Dockerfile` — uses `entrypoint.sh` as CMD

---

## ORM Model Naming Convention

ORM model class names carry the `ORM` suffix so they are never confused with domain entities (in `classes/entities/`) or service-layer objects.

| ORM Class | SQLAlchemy table | File |
|---|---|---|
| `UserORM` | `user` | `models/user.py` |
| `ApplicationORM` | `application` | `models/application.py` |
| `ApplicationDocumentORM` | `application_document` | `models/application.py` |

**Rule**: When a class name does not match the default SQLAlchemy snake-case derivation, you MUST declare `__tablename__` explicitly. All three models above have it. If you add a new ORM model, always declare `__tablename__` to prevent silent table-name drift.

```python
class SomethingNewORM(db.Model):
    __tablename__ = "something_new"   # always explicit
    ...
```

---

## The Three-Layer Architecture

### Layer 1: `routes/` — HTTP Controllers (Thin)
Routes are stateless HTTP handlers that:
1. Parse the request (form data, URL params)
2. Call ONE service/class method
3. Handle the OperationResult (success or error)
4. Flash message to user
5. Redirect or render

```python
# Correct pattern (all routes follow this):
@applicant_api.route("/submit-documents", methods=["POST"])
@login_required
def submit_documents():
    service = get_application_service(session["user_id"])
    result = service.submit_application(request.form, request.files)
    
    if result.success:
        flash("Application submitted successfully.", "success")  # Static message
    else:
        flash(result.error_msg, "error")  # Error already formatted by business layer
    
    return redirect(url_for("applicant_api.submit_documents"))
```

**Route Rules**:
- ❌ NO business logic, NO database queries, NO file processing
- ✅ Call service/class method and handle OperationResult
- ✅ Display static success messages (hardcoded, not extracted from result.data)
- ✅ Display error messages from result.error_msg (already formatted by business layer)
- ✅ Never use isinstance checks (result.data type is guaranteed by OperationResult contract)

### Layer 2: `services/` — Business Orchestration
Services orchestrate business operations by:
1. Validating inputs
2. Calling business classes and repositories
3. Handling errors with specific ErrorCodes
4. Returning OperationResult[T] with typed data

**Service Rules**:
- ✅ Return ALL methods as OperationResult[T]
- ✅ Use specific ErrorCodes (VALIDATION_FAILED, NOT_FOUND, etc.)
- ✅ Provide user-friendly error messages in result.error_msg
- ✅ Return business objects in result.data (ApplicationORM, ApplicationDocumentORM, UserORM)
- ❌ NO exception throwing (use ErrorCode instead)

### Layer 3: `classes/` — Domain Logic
Role classes (`Applicant`, `DeanOffice`, `Admin`, etc.) implement domain rules:
- State transitions (can only forward if status is correct)
- Business validations (GPA ranges, document requirements)
- Data mutations (forward application, mark as reviewed)

All access to data goes through repositories (`ApplicationRepository`, `get_user_repository()`).

```python
class Oidb(User):
    def return_application(self, application_id, notes):
        app_repo = get_application_repository()
        result = app_repo.find_by_id(application_id)
        if not result.success:
            return result
        app = result.data
        if app.status != "forwarded_to_oidb":
            return OperationResult.error(
                ErrorCode.INVALID_STATUS_TRANSITION,
                f"Cannot return application in status '{app.status}'"
            )
        app.status = "returned"
        app.return_notes = notes
        return app_repo.update(app)
```

**Class Rules**:
- ✅ ALL methods return OperationResult[T]
- ✅ Instantiated per request with user context: `Oidb(user_id, email, "oidb")`
- ✅ Use repositories for ALL data access (no direct db.session)
- ❌ NO direct db.session, NO exception throwing

### Layer 4: `database/` — Data Access
Repositories provide typed methods returning OperationResult.

```python
class ApplicationRepository:
    def find_by_id(self, app_id) -> OperationResult[ApplicationORM]:
        try:
            app = ApplicationORM.query.get(app_id)
            if not app:
                return OperationResult.error(ErrorCode.NOT_FOUND, "Application not found")
            return OperationResult.ok(data=app)
        except Exception as e:
            return OperationResult.error(ErrorCode.DB_ERROR, str(e))
```

**Repository Rules**:
- ✅ ALL methods return OperationResult[T]
- ✅ Typed return: result.data is ApplicationORM/ApplicationDocumentORM/list, never None for success
- ✅ Use specific ErrorCodes for each failure mode
- ✅ Only place where db.session is used directly

### Layer 5: `models/` — Data Shape (No Logic)
SQLAlchemy ORM models define columns, relationships, and basic serialization. NO business logic. See **ORM Model Naming Convention** above.

---

## Auto-fingerprint on ApplicationORM

`ApplicationORM` has two audit columns:

```python
last_edited_by_id = db.Column(db.Integer, nullable=True)
last_edited_at    = db.Column(db.DateTime, nullable=True)
```

These are set **automatically** by a SQLAlchemy `before_flush` event listener registered in `app/__init__.py`. It fires before every commit and sets both fields from `flask.session["user_id"]` for any dirty or new `ApplicationORM` in the session.

**Rule**: Never manually set `last_edited_by_id` or `last_edited_at` in business code. The listener handles it. If you find manual assignments to these fields, remove them.

---

## The OperationResult Contract (CRITICAL)

Every method in services, classes, and repositories returns OperationResult with this contract:

```python
@dataclass
class OperationResult(Generic[T]):
    success: bool          # True if operation succeeded
    data: T | None         # Business object (ApplicationORM, ApplicationDocumentORM, UserORM, list)
    error_code: ErrorCode | None
    error_msg: str         # User-friendly message, always set on error
```

**Contract Rules**:
1. **SUCCESS PATH**: `OperationResult.ok(data=business_object)`
   - `success = True`
   - `data = ApplicationORM | ApplicationDocumentORM | list | UserORM` (NEVER dict with message)
   - Routes display static message, may use result.data for business logic

2. **ERROR PATH**: `OperationResult.error(ErrorCode.SPECIFIC, "user message")`
   - `success = False`
   - `data = None`
   - `error_msg = "User-friendly message"` — already formatted, ready to flash

**Anti-Patterns (Will be caught in code review)**:
```python
# ❌ WRONG: Wrapping data with message dict
return OperationResult.ok(data={"message": "Success", "app": app})

# ❌ WRONG: Routes extracting message from ApplicationORM object
if result.success:
    msg = result.data.get("message")  # ApplicationORM has no .get()!

# ❌ WRONG: isinstance checks in routes
if isinstance(result.data, dict):
    msg = result.data.get("message")
```

**Correct Pattern**:
```python
result = service.operation(args)
if result.success:
    flash("Static message", "success")  # NOT extracted
else:
    flash(result.error_msg, "error")    # Error already formatted
```

---

## Admin Role

Admin is a special role for managing the software itself. It is separate from all business roles (applicant, oidb, dean, ygk, ydyo).

**Key properties**:
- Role slug: `"admin"`
- NOT in `ROLE_DEFINITIONS` → does not appear on the public portal page or staff role selector
- Login at `/auth/admin/login` (navigate directly; not linked from the main portal)
- No self-registration; create accounts via `flask init-admin` or the Flask shell

**Admin class** (`classes/users/admin.py`):
- `list_users()` → all users, ordered by role then email
- `change_user_role(user_id, new_role)` → only assignable (non-admin) roles allowed
- `get_config_summary()` → current feature flag dict from `config.py`
- `get_all_applications()` → all applications for DB overview
- `trigger_backup()` → timestamped SQLite backup in `instance/backups/`
- `list_backups()` → backup metadata list, newest first
- `restore_backup(filename)` → replaces live DB; disposes engine before swapping the file

**Admin blueprint** (`routes/admin.py`, prefix `/api/admin/`):
- `POST /users/change-role` — change a user's role
- `POST /backup` — create a new backup
- `POST /restore` — restore from a named backup (filename validated, no path traversal)

**Dashboard**: Admin goes to the same `/dashboard/` as other roles, with admin-specific tabs defined in `PHASE1_TABS["admin"]`.

---

## How the Dashboard Tab System Works

Tabs use **lazy loading**: the dashboard shell renders immediately with empty panels. When a user clicks a tab button, JavaScript fetches `/dashboard/tab/<slug>?page=N` which returns the panel HTML fragment. This keeps the initial page load fast regardless of how many applications are in the database.

### URL structure

- `/dashboard/` — the shell (no DB queries)
- `/dashboard/?tab=check-documents` — shell opens on the Check Documents tab automatically
- `/dashboard/?tab=check-documents&page=2` — opens tab on page 2 (survives refresh)
- `/dashboard/tab/check-documents?page=2` — the fetch endpoint (returns HTML fragment only)

### Tab slugs

Slugs are computed from tab titles by `_slugify()` in `dashboard.py`:
`re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')`

| Role | Tab title | Slug |
|------|-----------|------|
| OIDB | Check Documents | `check-documents` |
| Dean | Receive & Forward Applications | `receive-forward-applications` |
| YDYO | Set Prep School Status | `set-prep-school-status` |
| Applicant | Track Application | `track-application` |
| Applicant | Submit Application | `submit-application` |

### Adding a new tab — four touches

1. **`config.py` → `PHASE1_TABS`** — add entry with `"title"` and `"partial"` keys.

2. **`templates/partials/panel_<role>_<tab>.html`** — create the panel partial. Add a `{% if pagination … %}` block at the bottom if it shows a list.

3. **`routes/dashboard.py` → `_get_tab_data()`** — add a branch for `(role_slug, tab_slug)` that returns the template context dict. Use `_build_pagination()` and Python-slice the list if pagination is needed. Pass `status_counts` if the partial uses stat chips.

4. **Action routes** that POST and redirect: use `url_for("dashboard.index", tab="<slug>")` so the user lands back on the correct tab after an action.

`dashboard.html` does not need to change; it renders empty panels and the JS handles the rest.

### Error handling

- **Fetch errors** (network down, HTTP 4xx/5xx): `dashboard.js` calls `showToast()` which creates a dismissible toast using the same `.flash-msg` CSS classes as server-rendered flash messages. Toasts auto-dismiss after 5 seconds.
- **Server-rendered flash messages** (after form actions): rendered by `base.html`, auto-dismissed after 4 seconds by the same JS.

### Pagination, filtering, and sorting

`_get_tab_data()` uses `_PER_PAGE = 10`. For each paginated staff panel it:

1. Fetches all records from the role class.
2. Computes `status_counts` on the **full** list — chip totals always reflect the complete dataset.
3. Calls `_filter_apps(apps, filter_status)` — supports a single status string **or** comma-separated values (e.g. `"forwarded_to_ydyo,forwarded_to_dean"` for the OIDB "Forwarded" chip).
4. Calls `_sort_apps(apps, sort_col, sort_dir, col_map)` — numeric-aware sort using a `(bucket, numeric, string)` tuple key so integer IDs sort correctly as numbers, not strings.
5. Slices for the requested page.

Filter and sort travel as query params: `?filter=submitted&sort_col=1&sort_dir=asc`. The JS sends these on every chip click and column-header click (server-side re-fetch replaces DOM-only manipulation), so the filter/sort applies to the **full dataset** before pagination, not just the current page.

**Panel state element**: Every paginated staff panel partial embeds a hidden `<div class="panel-tab-state" data-filter="…" data-sort-col="…" data-sort-dir="…">` at the top. `dashboard.js` reads this after each fetch to carry filter/sort state into the next chip click, sort click, or page-navigation click. Panels without this element (e.g. admin tables) fall back to the old client-side filter/sort.

**Active chip highlighting**: The server renders the active chip with `chip-active` class and re-renders the sort indicator span on the active column header — no JS is needed to restore visual state after a re-fetch.

Partials receive: `pagination` dict, `status_counts` dict, `active_filter` str, `active_sort_col` int|None, `active_sort_dir` str.

**Admin and ROLE_DEFINITIONS**: Admin tabs live in `PHASE1_TABS["admin"]` but `ROLE_DEFINITIONS` does NOT include admin. This means admin's display name won't resolve through the normal lookup — `dashboard.py` handles this with a local `_ROLE_DISPLAY` dict that adds `"admin": "Administrator"`.

---

## Config as the Single Source of Truth

`config.py` owns three categories of constants:

**Tab definitions** (`PHASE1_TABS`) — tabs per role, including `"admin"`. `"partial": None` entries fall back to "coming soon" text.

**Reference data** — lists that populate dropdowns:
- `AVAILABLE_PROGRAMS` — applicant target programs
- `AVAILABLE_SEMESTERS` — available intake semesters
- `AVAILABLE_FACULTIES` — faculty names

**Document slots** (`APPLICATION_DOCUMENT_SLOTS`) — ordered list of `{slot, label, optional?}` dicts used by all submit and review screens. Current slots:

| Slot | Label | Optional |
|------|-------|---------|
| 1 | Student Certificate | No |
| 2 | Transcript | No |
| 3 | OYSM Points | No |
| 4 | English Proficiency Certificate | Yes |
| 5 | OYSM Certificate | Yes |

Optional slots remain technically optional (not validated on submit) but the `(optional)` text label is intentionally hidden from the UI — do not add it back.

**Feature flags** — `APPLICATION_SUBMISSION_PERIOD_OPEN`, `APPLICATION_CANCELLATION_ALLOWED`, `APPLICATION_RESUBMISSION_ALLOWED`. Flip these to open/close periods without touching logic.

---

## CLI Management Commands

Registered in `app/cli.py` and attached to the Flask app in `create_app()`.

```bash
FLASK_APP=run.py flask init-admin                      # create admin@admin/admin if not exists
FLASK_APP=run.py flask init-admin --email x --password y  # custom credentials
FLASK_APP=run.py flask seed-db                         # wipe + reseed with test data (prompts)
FLASK_APP=run.py flask seed-db --yes                   # skip confirmation (useful in scripts)
```

**`init-admin`** is idempotent — safe to run on every container boot. The Docker `entrypoint.sh` calls it before starting the server so the admin account always exists when the volume is fresh.

**`seed-db`** wipes ALL data and recreates:
- Staff: `admin@admin/admin`, `oidb@test/test`, `dean@test/test`, `ygk@test/test`, `ydyo@test/test`
- Applicants `applicant1@test` … `applicant7@test` (password: `test`), one per workflow status

---

## Backup / Restore System

Managed through `SQLAlchemyDatabaseAdapter` (the `ILowLevelDatabase` implementation) and surfaced via the `Admin` class.

- **Backups directory**: `instance/backups/` — timestamped `.bak` files (`project_YYYYMMDD_HHMMSS.bak`)
- **Create**: `Admin.trigger_backup()` → calls `db_interface.backup()`
- **List**: `Admin.list_backups()` → returns `[{filename, created_at, size_kb}]` sorted newest first
- **Restore**: `Admin.restore_backup(filename)` → validates filename (no `/` or `\`, must end `.bak`), calls `db.engine.dispose()` to flush pooled connections, then copies the backup over the live `project.db`

The engine auto-reconnects on the next request after a restore.

---

## Adding a New Column to ApplicationORM

New columns require two changes or existing databases will break on startup:

1. **`models/application.py`** — add the `db.Column(...)` declaration to `ApplicationORM`.
2. **`app/__init__.py` → `_ensure_application_new_columns()`** — add the column name and its SQLite type string to the `additions` dict.

The helper runs `ALTER TABLE application ADD COLUMN …` for any missing column at startup, keeping existing SQLite files compatible.

Columns currently managed by this helper: `id_number`, `target_program`, `target_semester`, `is_currently_enrolled`, `oidb_notes`, `prep_school_status`, `forwarded_faculty`, `last_edited_by_id`, `last_edited_at`, `estimated_gpa`, `oysm_points`, `doc_checker_status`, `doc_checker_errors`, `dean_notes`.

---

## Status Badge CSS Convention

Status badges use `.status-badge.status-<status>` classes defined in `main.css`. The class name mirrors the `ApplicationORM.status` value exactly (underscores included). All `forwarded_*` statuses are **green** — they represent progression. `submitted` and `returned` are yellow and red respectively.

**Exception — Dean panel only**: `forwarded_to_dean` appears yellow inside the Dean's own panel (because it is *pending* from the dean's perspective). This is achieved with a separate `.status-pending-dean` class applied only in `panel_dean_applications.html`. The global `.status-forwarded_to_dean` rule stays green so other panels (OIDB, YDYO) see the correct colour.

**Rule**: Never change a global `.status-*` rule to solve a role-specific display need. Add a role-specific override class instead.

---

## Role Implementation Checklist

| Role | Class file | Route file | Dashboard partial | `_get_role_data` branch |
|------|-----------|-----------|-------------------|------------------------|
| Admin | `classes/users/admin.py` | `routes/admin.py` | `panel_admin_*.html` (3 tabs) | ✓ |
| Applicant | `classes/users/applicant.py` | `routes/applicant.py` | `panel_applicant_*.html` | ✓ |
| OIDB | `classes/users/oidb.py` | `routes/oidb.py` | `panel_oidb_documents.html` | ✓ |
| Dean | `classes/users/dean.py` | `routes/dean.py` | `panel_dean_applications.html` | ✓ | `get_document()`, view-document route |
| YDYO | `classes/users/ydyo.py` | `routes/ydyo.py` | `panel_ydyo_documents.html` | ✓ |
| YGK | `classes/users/ygk.py` | `routes/ygk.py` | — (partial: None) | — |

---

## Dashboard Animations (`static/css/dashboard.css`)

Three keyframes are defined at the top of `dashboard.css`:

| Keyframe | Used on | Purpose |
|---|---|---|
| `fadeSlideIn` | `.workspace-panel.active`, `.tab-content-wrap`, `.module-card` | Fade + 6px upward slide on enter |
| `loadingPulse` | `.tab-loading-placeholder` | Opacity pulse while content is fetching |

Animation specifics:
- **Panel switch** — `.workspace-panel.active` plays `fadeSlideIn 0.2s` every time a tab becomes active.
- **Card stagger** — `.cards-grid .module-card` plays `fadeSlideIn 0.25s` with `:nth-child(1–6)` delays (0–0.30s, step 0.06s).
- **Card hover** — `.module-card` has `transition: box-shadow, transform` and lifts 2px on hover.
- **Lazy content** — fetched tab HTML is wrapped in `<div class="tab-content-wrap">` so every load replays `fadeSlideIn 0.22s`.
- **Re-fetch dim** — `.panel-fetching` sets `opacity: 0.4; pointer-events: none` while a filter/sort/page fetch is in flight; the class is added/removed by `fetchTabContent` in JS.

---

## Dashboard JavaScript (`static/js/dashboard.js`)

All interactive behavior for the dashboard lives here:
- **Tab switching** — `.tab-button` clicks toggle `.workspace-panel.active`
- **Chip filters** — any `.stats-row[data-filter-table="<id>"]` auto-wires its `[data-filter]` chips to filter the named table by `data-status` on header rows
- **Column sort** — any `<table id="...">` with `<th data-sort="N">` gets clickable sort (row-pairs kept together during sort so expand rows stay linked)
- **Expand rows** — `.expand-btn` opens/closes `.app-row-expand` with animated slide; only one open at a time

### Re-fetch (filter / sort / page)

`fetchTabContent` checks for `.tab-content-wrap` inside the panel to distinguish first load from re-fetch:
- **First load** — replaces panel innerHTML with the loading placeholder.
- **Re-fetch** — adds `.panel-fetching` (dims existing content) instead of wiping it. Removes the class and swaps innerHTML when the response arrives. This prevents the "white flash" that would occur if the DOM were cleared before the fetch completed.

### Expand / collapse animation

`expandRow(row)` and `collapseRow(row)` drive the animation. Key design decisions:

- **Wrapper div** — on first call, `getExpandWrap(content)` inserts `<div class="expand-anim-wrap" style="overflow:hidden">` around `.expand-content` inside the `<td>`. We animate `max-height` on this wrapper (which has no padding or border of its own) rather than on `.expand-content` directly. This guarantees `max-height: 0` means true 0 height — animating the inner div would leave residual height from its `padding: 16px`.
- **Forced reflow** — `void wrap.offsetHeight` is used (not `requestAnimationFrame`) to commit the initial 0-height state before the transition begins.
- **`offsetHeight` not `scrollHeight`** — `collapseRow` reads `wrap.offsetHeight` (current rendered height) to start from the correct mid-animation position. `scrollHeight` returns 0 when `overflow:hidden; max-height:0` is already set, which would produce a no-op transition and leave the row stuck (never hidden).
- **Immediate bail** — if `wrap.offsetHeight === 0` when `collapseRow` is called (already collapsed), `row.hidden = true` is set immediately with no transition; this prevents a stuck open state when clicking rapidly.
- **`<td>` border** — the `<td>` in `.app-row-expand` has `border-bottom: 1px` in CSS. `collapseRow` zeroes this inline before the animation starts and restores it in the `transitionend` cleanup. Without this, a 1px residual row remained visible until `row.hidden = true` fired, causing a visible jerk.
- **Listener guard** — each wrap stores its active `transitionend` listener as `wrap._anim`. Both functions cancel any in-progress animation (remove old listener, restart) before adding a new one.

---

## Auth Routes

| Endpoint | Who | Notes |
|---|---|---|
| `/auth/applicant/login` | Applicants | No role selector |
| `/auth/applicant/register` | Applicants | Open self-registration |
| `/auth/staff/login` | Staff roles (oidb, dean, ygk, ydyo) | Role dropdown; role validated against `_STAFF_SLUGS` |
| `/auth/staff/register` | Disabled | Redirects to staff login with message; staff accounts created via admin |
| `/auth/admin/login` | Admin only | No role selector, no register link, not linked from main page |

Admin is excluded from `_STAFF_SLUGS` — attempting to log in as admin via the staff login route returns "Invalid role selected."

---

## Standalone Pages vs. Dashboard

Routes like `/api/oidb/check-documents` and `/api/dean/check-applicants` render standalone templates. These exist for direct URL access but are **not** the primary UI — the dashboard is.

---

## How a Request Flows

```
Browser
  → route function (routes/<role>.py)
      → _svc() instantiates role class (classes/users/<role>.py)
          → class method queries/updates via ApplicationRepository / UserRepository
      → flash message + redirect  OR  render_template
          → dashboard.html shell
              → {% include tab.partial %} (templates/partials/)
```
 