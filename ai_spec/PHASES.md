# Refactoring Phases - Central Tracking

**Last Updated**: May 22, 2026  
**Current Phase**: 2 (Service Layer)

## Phase Overview

This is the SINGLE SOURCE OF TRUTH for refactoring phases. Each directory's `.AGENT.md` contains only coding rules, NOT phase information.

### Phase 0: OperationResult & ErrorCode ✅ COMPLETE
- Created `app/core/result.py` with OperationResult[T] generic and ErrorCode enum
- Updated all methods in auth.py, users.py to return OperationResult
- All files compile without errors

### Phase 1: Repository Pattern & Split Classes ✅ COMPLETE  
- Created `app/database/application_repository.py` with typed methods returning OperationResult
- Split `app/classes/users.py` (335 lines) into `app/classes/users/` directory (6 files)
- All role classes now use ApplicationRepository instead of direct db.session
- Fixed critical architectural issue: database switching now possible without code changes

### Phase 2: Service Layer 🔄 IN PROGRESS
**Goal**: Thin HTTP routes by moving business logic to services  
**Deliverables**:
- [ ] Create `app/services/` directory with service classes
- [ ] ApplicationService wraps application operations
- [ ] UserService wraps user operations
- [ ] Routes delegate to services instead of direct class calls
- [ ] Error handling with OperationResult and toast messages

**Example Pattern**:
```python
# routes/applicant.py - AFTER Phase 2
result = get_applicant_service(session["user_id"]).submit(form, files)
if result.success:
    flash(result.data.get("message"), "success")
else:
    flash(result.error_msg, "error")  # Toast appears automatically
```

### Phase 3: Refactor Other Classes 🔲 NOT STARTED
**Goal**: Apply repository pattern to other entities (Document, Intibak, etc.)  
**Note**: Skip users.py - already done in Phase 1

### Phase 4: Refactor Routes 🔲 NOT STARTED
**Goal**: Make routes thin HTTP layer only  
**Current State**: Routes contain business logic, form parsing, database calls  
**Blockers**: Requires Phase 2 (services) to be complete first  
**Warning**: Routes will break temporarily until Phase 2 services exist

### Phase 5: Refactor Models 🔲 NOT STARTED
**Goal**: Add validation, timestamps, and proper ORM setup  
**Tasks**: Add created_at, updated_at, validators, relationships

## Critical Constraints

### Database Abstraction (Phase 1+ Requirement)
- ❌ NO direct `db.session` in business classes
- ✅ All data access through repositories (ApplicationRepository, UserRepository)
- ✅ All repository methods return OperationResult with error codes

### Return Types (Phase 0+ Requirement)
- ❌ NO bare `bool`, `tuple[bool, str]`, or `None` returns
- ✅ ALL methods return OperationResult with success/error_code/data/error_msg

### Error Handling (Phase 2 Requirement)
- ❌ NO silent failures (returning None without explanation)
- ✅ All errors have specific ErrorCode (not generic DB_ERROR when VALIDATION_FAILED is better)
- ✅ Flash messages display error_msg to user as red toast

## File Structure After Phase 2

```
app/
  core/                    # ✅ Phase 0
    result.py             
    __init__.py
  database/                # ✅ Phase 1
    application_repository.py
    interfaces.py
    adapters.py
    __init__.py
  classes/                 # ✅ Phase 1
    users/
      applicant.py
      dean.py
      # ... other roles
    auth.py
    interfaces.py
  services/                # 🔄 Phase 2 (NEW)
    __init__.py
    application_service.py
    user_service.py
    # ... other services
  routes/                  # 🔲 Phase 4 (TODO)
    applicant.py
    auth.py
    # ... other routes
  models/                  # 🔲 Phase 5 (TODO)
```

## Dependencies Between Phases

```
Phase 0 (OperationResult)
    ↓
Phase 1 (Repositories, Split Classes)
    ↓
Phase 2 (Services) ← Routes need this before refactoring
    ↓
Phase 4 (Routes refactor) ← Cannot start until Phase 2 done
```

**Implication**: Cannot safely refactor routes (Phase 4) until services (Phase 2) exist.

## When to Update This File

Update PHASES.md when:
- ✅ Completing a phase (mark checkbox, update date)
- ✅ Starting new phase (mark 🔄 IN PROGRESS)
- ✅ Discovering blockers (add to phase description)
- ✅ Major architectural decisions (document here, NOT in .AGENT.md files)

DO NOT update for:
- Small code changes within a phase
- Coding style updates
- File renames
- Minor bug fixes

## Quick Reference

| Phase | Status | Key Requirement | File Location |
|-------|--------|-----------------|---------------|
| 0 | ✅ COMPLETE | OperationResult + ErrorCode | app/core/result.py |
| 1 | ✅ COMPLETE | Repositories + Split classes | app/database/ + app/classes/users/ |
| 2 | 🔄 IN PROGRESS | Services layer | app/services/ (NEW) |
| 3 | 🔲 TODO | Other repositories | app/database/ |
| 4 | 🔲 TODO | Thin routes | app/routes/ |
| 5 | 🔲 TODO | Validation + timestamps | app/models/ |
