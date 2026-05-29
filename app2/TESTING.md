# UTMS Automated Testing

## Quick start

```bash
cd /home/ayna/CODES/utms/app2
/home/ayna/316Project/.venv/bin/pytest           # run all 72 tests
/home/ayna/316Project/.venv/bin/pytest -v        # verbose
/home/ayna/316Project/.venv/bin/pytest tests/test_roles.py   # one file
/home/ayna/316Project/.venv/bin/pytest --cov=app --cov-report=html
```

Current status: **72 tests, all passing.**

---

## Test file overview

| File | Classes | What is covered |
|------|---------|-----------------|
| `test_auth.py` | `TestPublicPages`, `TestLoginFlow`, `TestSessionManagement` | Home page, portal redirects, login/register, session lifecycle, logout |
| `test_applicant.py` | `TestApplicantAccess`, `TestApplicantTabContent`, `TestApplicantSubmission` | Dashboard access, lazy-load tab endpoint, resubmit / cancel guards |
| `test_roles.py` | `TestRoleAccess`, `TestRoleIsolation`, `TestTabContentEndpoint`, `TestOidbForwardWorkflow`, `TestOidbRoutes` | All-role dashboard access, cross-role action blocks, lazy-load endpoint, OIDB business logic (forward / return / cancel-forward), redirect assertions |
| `test_database.py` | `TestUserModel`, `TestApplicationModel`, `TestApplicationRepository` | ORM constraints, password hashing, status transitions, repository layer |

---

## Fixtures (conftest.py)

### Users
All created with password `"test"` via `werkzeug.security.generate_password_hash`.

| Fixture | Role |
|---------|------|
| `applicant_user` | applicant |
| `applicant_user_2` | applicant (second user) |
| `dean_user` | dean |
| `oidb_user` | oidb |
| `ydyo_user` | ydyo |
| `ygk_user` | ygk |

### Authenticated clients
Each `auth_client_*` fixture wraps the plain `client` with session cookies already set.

```python
def test_something(auth_client_oidb):
    resp = auth_client_oidb.get("/dashboard/tab/check-documents")
    assert resp.status_code == 200
```

### Applications

| Fixture | Status | Owner |
|---------|--------|-------|
| `application_submitted` | `submitted` | `applicant_user` |
| `application_returned` | `returned` | `applicant_user` |
| `application_forwarded_to_ydyo` | `forwarded_to_ydyo` | `applicant_user_2` |

---

## Writing tests

### HTTP test
```python
def test_oidb_tab_loads(auth_client_oidb):
    resp = auth_client_oidb.get("/dashboard/tab/check-documents")
    assert resp.status_code == 200
    assert b"Documents" in resp.data
```

### Business-logic unit test (Oidb class)
```python
from app.classes.users.oidb import Oidb
from app.models import ApplicationORM

def test_forward_changes_status(app, oidb_user, application_submitted):
    with app.app_context():
        oidb = Oidb(oidb_user.id, oidb_user.email, "oidb")
        result = oidb.forward_to_ydyo(application_submitted.id)
        assert result.success
        assert ApplicationORM.query.get(application_submitted.id).status == "forwarded_to_ydyo"
```

### Repository test
```python
from app.database.application_repository import ApplicationRepository

def test_find_by_id(app, application_submitted):
    result = ApplicationRepository.find_by_id(application_submitted.id)
    assert result.success and result.data is not None
```

---

## Key design rules for tests

- **ORM class names**: `UserORM`, `ApplicationORM`, `ApplicationDocumentORM` — not `User` / `Application`.
- **Valid statuses**: `submitted`, `returned`, `forwarded_to_ydyo`, `forwarded_to_dean`, `forwarded_to_ygk`, `cancelled`. There is no `draft`.
- **`create_app(test_config=…)`**: Pass `SQLALCHEMY_DATABASE_URI` pointing to a temp file so tests never touch the real DB.
- **`Query.get()` warnings**: SQLAlchemy 2.x warns against `Model.query.get(id)` — use `db.session.get(Model, id)` in new tests.

---

## Coverage

```bash
/home/ayna/316Project/.venv/bin/pytest --cov=app --cov-report=html
open htmlcov/index.html
```

Focus areas for future coverage growth:
- Dean and YDYO forward workflows (mirror OIDB tests)
- Full applicant submission (multipart form with files)
- Admin backup / restore routes
- Edge cases: duplicate application submit, GPA out of range
