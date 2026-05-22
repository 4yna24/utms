# UTMS Application - Architecture & Refactoring Guide

## Executive Summary

This Flask application manages university transfer applications with role-based workflows. The codebase has **significant architectural issues** that must be addressed systematically:

### Critical Issues (Blockers)
1. **Business logic scattered in routes** ← Routes contain form parsing, validation, DB calls
2. **Monolithic user classes** (335 lines in users.py) ← Should be 5 separate files
3. **Boolean returns without context** ← Can't debug failures; no error codes
4. **Database access is stringly-typed** ← String-based action dispatch, no type safety
5. **No service layer** ← Business logic not abstracted from HTTP concerns

### Current Architecture (Problematic)
```
HTTP Request
    ↓
Routes (applicant.py, dean.py, ...)
    ↓
User Role Classes (Applicant, DeanOffice, ...)
    ↓
Database Adapter (string-based execute_query)
    ↓
SQLAlchemy ORM Models
    ↓
Database
```

**Problems with this architecture**:
- Routes shouldn't do form parsing or call business logic
- User classes shouldn't import db or do file I/O
- No service layer to abstract concerns
- Error handling is nil (silent failures, bare bool returns)
- String-based DB actions = no type safety

### Target Architecture (Desired)
```
HTTP Request
    ↓
Routes (thin HTTP layer only)
    ↓
Services (business logic orchestration)
    ↓
User Role Classes (domain logic, state transitions)
    ↓
Repositories (type-safe data access)
    ↓
Models (ORM + validation)
    ↓
Database
```

## Refactoring Roadmap

### ✓ Phase 0: Foundation (Do First)
**Create result/error handling objects**

File: `app/core/result.py`

```python
from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, TypeVar

T = TypeVar('T')

class ErrorCode(Enum):
    """Centralized error codes."""
    # Validation errors
    VALIDATION_FAILED = "VALIDATION_FAILED"
    INVALID_FILE_FORMAT = "INVALID_FILE_FORMAT"
    INVALID_STATUS_TRANSITION = "INVALID_STATUS_TRANSITION"
    
    # Not found errors
    NOT_FOUND = "NOT_FOUND"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    APPLICATION_NOT_FOUND = "APPLICATION_NOT_FOUND"
    
    # Conflict errors
    CONFLICT = "CONFLICT"
    USER_EXISTS = "USER_EXISTS"
    APPLICATION_EXISTS = "APPLICATION_EXISTS"
    
    # Database errors
    DB_ERROR = "DB_ERROR"
    DB_INTEGRITY_ERROR = "DB_INTEGRITY_ERROR"
    
    # File errors
    FILE_NOT_SAVED = "FILE_NOT_SAVED"
    
    # Unknown
    UNKNOWN_ERROR = "UNKNOWN_ERROR"

@dataclass
class OperationResult(Generic[T]):
    """Rich result object for all operations."""
    success: bool
    data: T | None = None
    error_code: ErrorCode | None = None
    error_msg: str = ""
    
    def is_success(self) -> bool:
        return self.success
    
    def is_error(self, code: ErrorCode) -> bool:
        return not self.success and self.error_code == code
```

**Directory structure**:
```
app/
  core/
    __init__.py
    result.py         # OperationResult, ErrorCode
    exceptions.py     # Custom exceptions (optional)
```

### ▶ Phase 1: Database Layer Refactoring
**Replace string-based dispatch with repositories**

Target files: `database/`, `models/`

```
database/
  __init__.py
  models.py           # Move from app/models/ or create here
  repositories/
    __init__.py
    base.py
    user.py
    application.py
    document.py
  interfaces.py       # Repository interfaces
  
models/               # Keep old location for now, plan deprecation
  __init__.py
```

**Timeline**: 1-2 weeks

**Tasks**:
- [ ] Create OperationResult (Phase 0)
- [ ] Create UserRepository, ApplicationRepository, DocumentRepository
- [ ] Move/consolidate interfaces from database/interfaces.py and classes/interfaces.py
- [ ] Update all query logic to use repositories
- [ ] Return OperationResult from repository methods

**Verification**:
- No string-based actions (if 'action_name' == ...) anywhere
- All repository methods are type-safe
- All repository methods return OperationResult

### ▶ Phase 2: Service Layer Creation
**Encapsulate business logic away from routes and classes**

```
services/
  __init__.py
  user_service.py
  applicant_service.py
  dean_service.py
  oidb_service.py
  ydyo_service.py
  ygk_service.py
  auth_service.py
```

**Timeline**: 1-2 weeks

**Example - ApplicantService**:
```python
# services/applicant_service.py
from core.result import OperationResult, ErrorCode
from database.repositories import ApplicationRepository, DocumentRepository

class ApplicantService:
    def __init__(self, applicant_id: int, user_repo, app_repo, doc_repo):
        self.applicant_id = applicant_id
        self.user_repo = user_repo
        self.app_repo = app_repo
        self.doc_repo = doc_repo
    
    def submit_application(
        self, 
        form_data: dict,
        files: dict,
        document_slots: list
    ) -> OperationResult:
        """Submit new application."""
        # Validate form
        validation_result = self._validate_form(form_data)
        if not validation_result.success:
            return validation_result
        
        # Check if applicant already has application
        existing = self.app_repo.find_by_applicant_id(self.applicant_id)
        if existing:
            return OperationResult(
                success=False,
                error_code=ErrorCode.APPLICATION_EXISTS,
                error_msg="You already have an application"
            )
        
        # Create application
        try:
            app_result = self.app_repo.create(
                applicant_id=self.applicant_id,
                **form_data
            )
            if not app_result.success:
                return app_result
            
            # Save documents
            doc_result = self.doc_repo.save_documents(
                application_id=app_result.data.id,
                files=files,
                slots=document_slots
            )
            if not doc_result.success:
                return doc_result
            
            return OperationResult(success=True, data=app_result.data)
        except Exception as e:
            return OperationResult(
                success=False,
                error_code=ErrorCode.DB_ERROR,
                error_msg=str(e)
            )
```

**Verification**:
- All business logic is in services
- Services use repositories, not direct db access
- Services return OperationResult
- Services are dependency-injected (no global imports)

### ▶ Phase 3: Refactor Classes Directory
**Split monolithic user classes into separate files**

```
classes/
  __init__.py
  users/
    __init__.py
    base.py           # Abstract User class
    applicant.py      # Applicant role
    dean.py           # DeanOffice
    oidb.py           # OIDB
    ydyo.py           # YDYO
    ygk.py            # YGK
  auth.py             # Keep as-is
  interfaces.py       # Move here from database/
  result.py           # Or keep in core/
```

**Timeline**: 1 week

**Remove from classes**:
- Form parsing (move to routes/forms/)
- Direct database calls (use repositories)
- File I/O (use file_service)

**What stays in classes**:
- Domain logic (state transitions, business rules)
- Role-specific behavior (validate, submit, review)

**Verification**:
- No import of db directly
- No form.get() calls
- No file operations (open, save)
- All return OperationResult

### ▶ Phase 4: Refactor Routes
**Make routes thin HTTP layer only**

```
routes/
  __init__.py
  common.py           # Decorators, helpers
  forms/              # NEW - form parsing
    __init__.py
    validators.py
    parsers.py
  web/                # NEW - HTML routes
    __init__.py
    applicant.py
    dashboard.py
    # ...
  api/                # Existing - JSON routes
    applicant.py
    dean.py
    # ...
```

**Example - Refactored Route**:
```python
# routes/web/applicant.py (BEFORE - current)
@applicant_api_bp.route("/submit-documents", methods=["POST"])
def create_application():
    form_data = Applicant.parse_form_data(request.form)  # ← Wrong!
    valid, msg = Applicant.validate_form_data(form_data)  # ← Wrong!
    applicant = Applicant(session["user_id"], ...)        # ← Wrong!
    success, msg = applicant.submit(form_data, ...)       # ← Calling class directly

# routes/web/applicant.py (AFTER - desired)
@applicant_api_bp.route("/submit-documents", methods=["POST"])
def create_application():
    # Extract HTTP inputs
    form_data = request.form
    files = request.files
    
    # Delegate to service
    service = get_applicant_service(session["user_id"])
    result = service.submit_application(form_data, files)
    
    # Return HTTP response
    if result.success:
        flash("Application submitted successfully", "success")
        return redirect(url_for("dashboard.index"))
    else:
        flash(result.error_msg, "error")
        return redirect(url_for("applicant_web.submit_documents"))
```

**Timeline**: 1-2 weeks

**Verification**:
- Routes have max 10 lines per handler
- No db.session calls in routes
- No User class instantiation in routes
- All business logic calls go through services

### ▶ Phase 5: Refactor Models
**Move to database layer, add validation**

```
database/
  models.py           # Consolidate with ORM models
```

**Add to models**:
- Timestamps (created_at, updated_at)
- Validation decorators (@validates)
- State transition methods
- Check constraints

**Timeline**: 1 week

**Verification**:
- Timestamps on all models
- Enum validation on status fields
- Models in database/ not app/models/

## Dependency Order (Must Follow!)

```
1. Phase 0: OperationResult class
   ↓ (all phases depend on this)
2. Phase 1: Repositories (database layer)
   ↓ (phases 2, 3, 4 depend on repositories)
3. Phase 2: Services layer
4. Phase 3: Refactor classes (use services, repos)
5. Phase 4: Refactor routes (use services)
6. Phase 5: Refactor models (move to database/)
```

**Why this order?**
- Phase 0: Foundation for error handling everywhere
- Phase 1: Foundation for data access everywhere
- Phase 2: Encapsulates business logic away from routes
- Phase 3: Clean up user classes using repositories & services
- Phase 4: Make routes thin (call services only)
- Phase 5: Consolidate and strengthen models

## Current Codebase Snapshot

| Layer | Current | Issues | Target |
|-------|---------|--------|--------|
| **Routes** | HTTP + business logic + form parsing | Mixed concerns | HTTP only |
| **Services** | None | N/A | Full orchestration layer |
| **Classes** | 5 roles in users.py (335 lines) | Monolithic, form logic, direct db | Split, clean, repos only |
| **Database** | String-based actions, no repos | No type safety | Repositories + models |
| **Models** | app/models/, no validation | Missing constraints | database/models/ + validation |
| **Error Handling** | bare bool, None | Silent failures | OperationResult everywhere |

## What Agents Should Know

### DO:
- ✅ Follow dependency order strictly
- ✅ Return OperationResult from all business operations
- ✅ Use repositories for all data access
- ✅ Keep routes thin (5-10 lines max per handler)
- ✅ Inject dependencies (no global imports)
- ✅ Write tests for each layer separately

### DO NOT:
- ❌ Return bare bool/None from business logic methods
- ❌ Call db.session in routes
- ❌ Import db directly in classes
- ❌ Put business logic in routes
- ❌ Instantiate User classes in routes (use services)
- ❌ Use string-based dispatch for database actions
- ❌ Scatter form parsing logic across files

## Testing Strategy

Each phase should include unit tests:

```
tests/
  unit/
    test_repositories.py        # Test queries
    test_services.py            # Test business logic
    test_models.py              # Test validation
  integration/
    test_routes.py              # Test HTTP layer
    test_workflows.py           # End-to-end application flows
```

**Key test priorities**:
1. Repository query correctness
2. Service error handling (all OperationResult codes tested)
3. Model state transitions
4. Route HTTP status codes

## Documentation Files

Each directory has a `.AGENT.md` file:

- [classes/.AGENT.md](./classes/.AGENT.md) - User role classes, monolithic users.py issue
- [routes/.AGENT.md](./routes/.AGENT.md) - HTTP layer, business logic in routes issue
- [database/.AGENT.md](./database/.AGENT.md) - String-based dispatch, no repositories
- [models/.AGENT.md](./models/.AGENT.md) - No validation, missing timestamps

## Quick Reference

### Issue: Boolean returns without context
**File**: classes/users.py
**Problem**: `return False` with no error code
**Solution**: Return `OperationResult(success=False, error_code=ErrorCode.XXX, error_msg="...")`

### Issue: Routes have business logic
**File**: routes/*.py
**Problem**: Form parsing, validation, db calls in route handlers
**Solution**: Create services layer, routes delegate to services

### Issue: Users.py is 335 lines
**File**: classes/users.py
**Problem**: 5 role classes in one file
**Solution**: Split into classes/users/ directory, one file per role

### Issue: Database access is stringly-typed
**File**: database/adapters.py
**Problem**: `execute_query('action_name', {'key': value})`
**Solution**: Create repositories with typed methods

## FAQ

**Q: Why OperationResult?**
A: When operations fail, we need to know WHY. Bool/None gives no context. OperationResult carries error_code for logging, error_msg for users.

**Q: Why services?**
A: Routes shouldn't do business logic. Services encapsulate domain logic away from HTTP concerns, allowing reuse from CLI, scheduled tasks, etc.

**Q: Why repositories?**
A: Scattered query logic across codebase = unmaintainable. Repositories centralize data access, making it testable and optimizable.

**Q: Can I skip Phase 1?**
A: No. Repositories are foundation for Phases 2-4. All must have type-safe, error-aware data access.

**Q: What about legacy code during refactoring?**
A: Implement phases incrementally. Services can coexist with old code. Gradually migrate routes to new services.
