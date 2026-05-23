# UTMS Automated Testing - Quick Start

## Installation (One-time setup)

```bash
cd /home/ayna/CODES/utms/app2
source ../.venv/bin/activate
pip install pytest pytest-flask pytest-cov
```

## Running Tests

### Run ALL tests:
```bash
pytest
# Or use the convenience script:
./run_tests.sh              # Linux/Mac
run_tests.bat              # Windows
```

### Run specific test file:
```bash
pytest tests/test_auth.py
pytest tests/test_applicant.py
```

### Run with detailed output:
```bash
pytest -v
```

### Run with coverage report:
```bash
pytest --cov=app --cov-report=html
# Then open htmlcov/index.html in browser
```

### Run single test:
```bash
pytest tests/test_auth.py::TestAuthRoutes::test_home_page_loads
```

## Test Files Overview

| File | Tests | Coverage |
|------|-------|----------|
| **test_auth.py** | Authentication & session management (10 tests) | Login/Register routes, role redirects |
| **test_applicant.py** | Applicant workflows (10 tests) | Dashboard, form submission, document handling |
| **test_roles.py** | Role-based access control (10 tests) | Dean, OIDB, YDYO, YGK access & isolation |
| **test_database.py** | Models & database (9 tests) | User/Application creation, queries, relationships |

## Available Fixtures (in conftest.py)

### Users:
- `applicant_user`, `applicant_user_2`, `applicant_user_3`
- `dean_user`, `oidb_user`, `ydyo_user`, `ygk_user`

### Authenticated Clients:
- `auth_client_applicant`, `auth_client_dean`, etc.
- Automatically logged in - use like: `auth_client_applicant.get("/dashboard/")`

### Test Data:
- `application_draft` - Draft application ready for testing
- `application_submitted` - Submitted application in workflow

## Writing Your Own Tests

Example test that checks applicant can submit form:
```python
def test_applicant_submit_form(auth_client_applicant):
    """Test applicant can submit application form."""
    resp = auth_client_applicant.post("/api/applicant/submit", json={
        "id_number": "123456789",
        "target_program": "Computer Science"
    })
    assert resp.status_code in [200, 201]
```

Example test that checks database operations:
```python
def test_create_application_in_db(app, applicant_user):
    """Test creating application in database."""
    with app.app_context():
        app_obj = Application(
            applicant_id=applicant_user.id,
            status="draft",
            full_name="John Doe",
            current_gpa="3.5"
        )
        db.session.add(app_obj)
        db.session.commit()
        
        retrieved = Application.query.get(app_obj.id)
        assert retrieved.status == "draft"
```

## Common Test Patterns

```python
# Check HTTP response status
assert resp.status_code == 200

# Check redirect
assert resp.status_code == 302
assert "dashboard" in resp.location

# Check session data
with client.session_transaction() as sess:
    assert sess.get("user_id") is not None

# Check database state
with app.app_context():
    user = User.query.get(1)
    assert user is not None

# Check JSON response
resp = client.get("/api/track-application")
data = resp.get_json()
assert data["status"] == "submitted"
```

## Running in CI/CD

These tests can run automatically on every commit. Example for GitHub Actions:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - run: pip install -r requirements.txt
      - run: pytest --cov=app
```

## Coverage Reports

After running `pytest --cov=app --cov-report=html`:
- Open `htmlcov/index.html` in your browser
- See which lines are tested
- Identify code that needs more tests

## Troubleshooting

**Tests fail on import?**
```bash
# Make sure you're in the right directory and venv is activated
cd /home/ayna/CODES/utms/app2
source ../.venv/bin/activate
```

**"Module not found" errors?**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**Want to debug a test?**
```bash
# Add breakpoint in test code
import pdb; pdb.set_trace()

# Then run with -s flag
pytest -s tests/test_file.py::test_name
```

## Next Steps

1. ✅ **Basic tests created** - 39 tests covering auth, routes, roles, database
2. Add tests for **service layer** operations
3. Add tests for **error cases** and edge conditions
4. Add **integration tests** for full workflows (e.g., applicant → dean → OIDB → YDYO → YGK)
5. Set up **CI/CD pipeline** to run tests on every push
6. Increase coverage to **70%+ on critical business logic**

## Questions?

See [tests/README.md](tests/README.md) for comprehensive documentation.
