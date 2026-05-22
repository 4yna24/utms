# Codebase Guide

This file explains where things live and why, so that new code goes in the right layer the first time. UTMS uses a three-layer architecture: **Services** (business orchestration) → **Classes** (domain logic) → **Repositories** (data access).

---

## Layer Overview

```
app/
├── core/
│   ├── result.py       ← OperationResult[T], ErrorCode enum (NO exceptions)
│   └── __init__.py
├── services/           ← ✅ Phase 2: Service layer (NEW)
│   ├── base_service.py ← BaseService with error(), ok(), validate_required_fields()
│   ├── application_service.py ← Submit, resubmit, cancel operations
│   ├── auth_service.py ← Login, register, password_reset
│   ├── user_service.py ← User operations
│   └── __init__.py
├── classes/            ← ✅ Phase 1: Split into users/ directory
│   ├── users/          ← Role classes with business logic
│   │   ├── base.py     ← Abstract User class
│   │   ├── applicant.py    ← Applicant role (submit, track)
│   │   ├── dean.py         ← DeanOffice role (review, forward)
│   │   ├── oidb.py         ← Oidb role (document verification)
│   │   ├── ydyo.py         ← Ydyo role (prep school marking)
│   │   ├── ygk.py          ← YGK role (approval)
│   │   └── __init__.py
│   ├── auth.py         ← Auth class (credentials, tokens)
│   └── interfaces.py   ← IReviewer, IDocumentHandler abstract bases
├── database/           ← ✅ Phase 1: Repository pattern
│   ├── application_repository.py ← ApplicationRepository (all Application queries)
│   ├── interfaces.py   ← ILowLevelDatabase, IHighLevelDatabase, IUserRepository
│   ├── adapters.py     ← SQLAlchemyUserDataService (implements IUserRepository)
│   └── __init__.py
├── models/             ← SQLAlchemy ORM (data shape only, no logic)
│   ├── user.py
│   ├── application.py
│   └── __init__.py
├── routes/             ← ✅ Phase 2: Thin HTTP controllers
│   ├── auth.py         ← Login, register endpoints (uses AuthService)
│   ├── applicant.py    ← Submit, resubmit, cancel (uses ApplicationService)
│   ├── dean.py         ← Review, forward to YGK (calls DeanOffice class)
│   ├── oidb.py         ← Verify docs, forward to YDYO (calls Oidb class)
│   ├── ydyo.py         ← Mark prep school, forward (calls Ydyo class)
│   ├── ygk.py          ← Approve applications (calls YGK class)
│   ├── dashboard.py    ← Dashboard page load, tab data gathering
│   ├── common.py       ← Shared decorators (@require_role)
│   └── __init__.py
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
│       └── ...
├── __init__.py         ← create_app(), db initialization
└── config.py           ← PHASE1_TABS, AVAILABLE_PROGRAMS, feature flags
```

---

## The Three-Layer Architecture (Phase 2)

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
@require_login
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

### Layer 2: `services/` — Business Orchestration (NEW - Phase 2)
Services orchestrate business operations by:
1. Validating inputs
2. Calling business classes and repositories
3. Handling errors with specific ErrorCodes
4. Returning OperationResult[T] with typed data

Services are instantiated per request with user context and are NOT directly used by routes — routes call services.

```python
# Service example (ApplicationService):
class ApplicationService(BaseService):
    def submit_application(self, form_data, files):
        # Validate
        parsed = self.parse_form_data(form_data)
        error = self.validate_form_data(parsed)
        if error:
            return error
        
        # Delegate to class
        applicant = Applicant(self.user_id, self.email)
        return applicant.submit(parsed, files)  # Returns OperationResult
```

**Service Rules**:
- ✅ Return ALL methods as OperationResult[T]
- ✅ Use specific ErrorCodes (VALIDATION_FAILED, NOT_FOUND, etc.)
- ✅ Provide user-friendly error messages in result.error_msg
- ✅ Return business objects in result.data (Application, Document, User)
- ❌ NO exception throwing (use ErrorCode instead)

### Layer 3: `classes/` — Domain Logic (Phase 1)
Role classes (`Applicant`, `DeanOffice`, `Oidb`, etc.) implement domain rules:
- State transitions (can only forward if status is correct)
- Business validations (GPA ranges, document requirements)
- Data mutations (forward application, mark as reviewed)

All access to data goes through repositories (ApplicationRepository, etc.).

```python
# Class example (role method):
class Oidb(User):
    def return_application(self, application_id, notes):
        app_repo = get_application_repository()
        
        # Get application
        result = app_repo.find_by_id(application_id)
        if not result.success:
            return result
        
        app = result.data
        if app.status != "forwarded_to_oidb":
            return OperationResult.error(
                ErrorCode.INVALID_STATUS_TRANSITION,
                f"Cannot return application in status '{app.status}'"
            )
        
        # Update and commit via repository
        app.status = "returned"
        app.return_notes = notes
        return app_repo.update(app)  # Returns OperationResult with Application
```

**Class Rules**:
- ✅ ALL methods return OperationResult[T]
- ✅ Instantiated per request with user context: `Oidb(user_id, email, "oidb")`
- ✅ Use repositories for ALL data access (no direct db.session)
- ✅ Return business objects in result.data (Application, Document lists, etc.)
- ❌ NO direct db.session, NO exception throwing

### Layer 4: `database/` — Data Access (Phase 1)
Repositories provide typed methods returning OperationResult:

```python
# Repository example (ApplicationRepository):
class ApplicationRepository:
    def find_by_id(self, app_id) -> OperationResult[Application]:
        try:
            app = Application.query.get(app_id)
            if not app:
                return OperationResult.error(ErrorCode.NOT_FOUND, "Application not found")
            return OperationResult.ok(data=app)
        except Exception as e:
            return OperationResult.error(ErrorCode.DB_ERROR, str(e))
```

**Repository Rules**:
- ✅ ALL methods return OperationResult[T]
- ✅ Typed return: result.data is Application/Document/list, never None for success
- ✅ Use specific ErrorCodes for each failure mode
- ✅ Only place where db.session is used directly

### Layer 5: `models/` — Data Shape (No Logic)
SQLAlchemy ORM models define columns, relationships, and basic serialization. NO business logic.

---

## The OperationResult Contract (Phase 2 CRITICAL)

Every method in services, classes, and repositories returns OperationResult with this contract:

```python
@dataclass
class OperationResult(Generic[T]):
    success: bool          # True if operation succeeded
    data: T | None         # Business object (Application, Document, User, list)
    error_code: ErrorCode | None
    error_msg: str         # User-friendly message, always set on error
```

**Contract Rules**:
1. **SUCCESS PATH**: `OperationResult.ok(data=business_object)`
   - `success = True`
   - `data = Application | Document | list | User` (NEVER dict with message)
   - `error_code = None`
   - Routes display static message, may use result.data for business logic

2. **ERROR PATH**: `OperationResult.error(ErrorCode.SPECIFIC, "user message")`
   - `success = False`
   - `data = None`
   - `error_code = ErrorCode.SPECIFIC` (VALIDATION_FAILED, NOT_FOUND, DB_ERROR, etc.)
   - `error_msg = "User-friendly message"` — already formatted, ready to flash

**Anti-Patterns (Will be caught in code review)**:
```python
# ❌ WRONG: Wrapping data with message dict
return OperationResult.ok(data={"message": "Success", "app": app})

# ❌ WRONG: Bare exceptions instead of ErrorCode
try:
    ...
except Exception:
    raise  # Should return OperationResult.error() instead

# ❌ WRONG: Routes extracting message from Application object
result = service.return_application(app_id, notes)
if result.success:
    msg = result.data.get("message")  # Application has no .get()!
    flash(msg, "success")

# ❌ WRONG: isinstance checks in routes
if isinstance(result.data, dict):
    msg = result.data.get("message")
else:
    msg = "default"
flash(msg, "success")
```

**Correct Pattern (All routes must follow)**:
```python
result = service.operation(args)
if result.success:
    flash("Static message", "success")  # NOT extracted
    # Optionally use result.data for business logic
    app = result.data  # Type-safe, guaranteed to be Application or None
else:
    flash(result.error_msg, "error")  # Error message already formatted
```

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
