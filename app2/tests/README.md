# Testing Guide for UTMS Application

This directory contains automated tests for the UTMS (University Transfer Management System) web application.

## Setup

### 1. Install Test Dependencies

Add these to your `requirements.txt`:
```
pytest==7.4.3
pytest-flask==1.3.0
pytest-cov==4.1.0
```

Then install:
```bash
pip install -r requirements.txt
```

### 2. Running Tests

#### Run all tests:
```bash
pytest
```

#### Run specific test file:
```bash
pytest tests/test_auth.py
```

#### Run specific test class:
```bash
pytest tests/test_auth.py::TestAuthRoutes
```

#### Run specific test:
```bash
pytest tests/test_auth.py::TestAuthRoutes::test_home_page_loads
```

#### Run with verbose output:
```bash
pytest -v
```

#### Run with coverage report:
```bash
pytest --cov=app tests/
```

#### Run with detailed output (including print statements):
```bash
pytest -s
```

## Test Structure

### Fixtures (in `conftest.py`)

Fixtures are reusable test utilities that set up test data and clients:

**Flask App & Database:**
- `app` - Flask test app with isolated SQLite database
- `client` - Unauthenticated test client
- `db_instance` - Database instance for manual queries

**User Fixtures:**
- `applicant_user` - Test applicant user
- `dean_user` - Test dean user
- `oidb_user` - Test OIDB user
- `ydyo_user` - Test YDYO user
- `ygk_user` - Test YGK user

**Authenticated Clients:**
- `auth_client_applicant` - Client logged in as applicant
- `auth_client_dean` - Client logged in as dean
- `auth_client_oidb` - Client logged in as OIDB
- `auth_client_ydyo` - Client logged in as YDYO
- `auth_client_ygk` - Client logged in as YGK

**Application Fixtures:**
- `application_draft` - Draft application for testing
- `application_submitted` - Submitted application for testing

### Test Modules

- **test_auth.py** - Authentication and session management
- **test_applicant.py** - Applicant dashboard and workflows
- **test_roles.py** - Role-based access control
- **test_database.py** - Database models and relationships

## Example: Writing Your Own Tests

### Test Authentication
```python
def test_applicant_login(auth_client_applicant):
    """Test applicant is logged in."""
    with auth_client_applicant.session_transaction() as sess:
        assert sess.get("user_role") == "applicant"
```

### Test Route Access
```python
def test_dashboard_shows_applications(auth_client_applicant):
    """Test applicant dashboard loads."""
    resp = auth_client_applicant.get("/dashboard/")
    assert resp.status_code == 200
```

### Test Form Submission
```python
def test_submit_application(auth_client_applicant):
    """Test application submission."""
    resp = auth_client_applicant.post("/api/applicant/submit", json={
        "id_number": "123456789",
        "target_program": "Computer Science"
    })
    assert resp.status_code in [200, 201]
```

### Test Database Operations
```python
def test_user_creation(app):
    """Test user model."""
    with app.app_context():
        user = User(email="test@test.com", password_hash="hash", role="applicant")
        db.session.add(user)
        db.session.commit()
        
        retrieved = User.query.filter_by(email="test@test.com").first()
        assert retrieved is not None
```

## Key Testing Patterns

### Check Response Status
```python
assert resp.status_code == 200  # OK
assert resp.status_code == 302  # Redirect
assert resp.status_code == 403  # Forbidden
assert resp.status_code == 404  # Not Found
```

### Check Session Data
```python
with client.session_transaction() as sess:
    assert sess.get("user_id") is not None
    assert sess.get("user_role") == "applicant"
```

### Check Database State
```python
with app.app_context():
    user = User.query.get(1)
    assert user is not None
```

### Check Redirect
```python
resp = client.get("/protected-route", follow_redirects=False)
assert resp.status_code == 302
assert "login" in resp.location.lower()
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines. Example GitHub Actions workflow:

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
      - run: pytest --cov=app tests/
```

## Debugging Tests

### Print debug info:
```python
def test_something(client):
    resp = client.get("/route")
    print(f"Status: {resp.status_code}")
    print(f"Data: {resp.data}")
    assert False  # This will show the prints
```

Then run with `-s`:
```bash
pytest -s tests/test_file.py::test_something
```

### Drop into debugger:
```python
import pdb; pdb.set_trace()
```

Or use pytest's built-in:
```python
pytest --pdb tests/test_file.py
```

### Check what's in session/request:
```python
def test_check_session(client):
    with client.session_transaction() as sess:
        print(f"Session contents: {dict(sess)}")
```

## Test Coverage

Run tests with coverage:
```bash
pytest --cov=app --cov-report=html tests/
```

This generates an HTML report in `htmlcov/index.html` showing:
- Which lines of code are tested
- Which functions/classes need more tests
- Overall coverage percentage

Aim for:
- 70%+ for business logic
- 50%+ for routes (harder to test due to browser interaction)

## Next Steps

1. Run `pytest` to see baseline results
2. Add tests for critical user workflows
3. Add tests for error cases
4. Set up CI/CD to run tests on every push
5. Aim for 70%+ code coverage on core business logic
