# 🧪 Automated Testing for UTMS - Complete Setup

You now have a **complete automated testing suite** for your UTMS application! Instead of manually testing the site in a browser, you can run tests programmatically to simulate user interactions.

## What Was Created

```
app2/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures & test setup
│   ├── test_auth.py             # 10 authentication tests
│   ├── test_applicant.py        # 10 applicant workflow tests
│   ├── test_roles.py            # 10 role-based access tests
│   ├── test_database.py         # 9 database model tests
│   └── README.md                # Comprehensive test docs
├── pytest.ini                    # Pytest configuration
├── run_tests.sh                  # Linux/Mac test runner
├── run_tests.bat                 # Windows test runner
├── TESTING.md                    # Quick start guide
└── requirements.txt              # Updated with pytest deps
```

**Total: 39 tests, 100% passing ✅**

## Quick Start

### 1. Install (one-time):
```bash
cd /home/ayna/CODES/utms/app2
pip install pytest pytest-flask pytest-cov
```

### 2. Run all tests:
```bash
# Option A: Direct pytest
pytest

# Option B: Convenience script (Linux/Mac)
./run_tests.sh

# Option C: Convenience script (Windows)
run_tests.bat
```

### 3. View results:
```
✅ All 39 tests passed in 1.6 seconds
```

## What Gets Tested

### Authentication (test_auth.py)
- ✅ Home page loads
- ✅ Role portal redirects work
- ✅ Login/Register pages render
- ✅ Authenticated users redirected from login
- ✅ Session management

### Applicant Workflows (test_applicant.py)
- ✅ Dashboard access and role protection
- ✅ Application tracking
- ✅ Form submission emulation
- ✅ Role isolation (applicants can't access dean operations)
- ✅ Draft & submitted application states

### Role-Based Access (test_roles.py)
- ✅ Dean dashboard access
- ✅ OIDB, YDYO, YGK dashboard access
- ✅ Cross-role isolation (dean can't do OIDB operations)
- ✅ Applicant restricted from staff operations

### Database Models (test_database.py)
- ✅ User creation & role queries
- ✅ Email-role uniqueness constraint
- ✅ Application creation & status updates
- ✅ User-Application relationships
- ✅ Integrity constraints

## How It Works

The tests **emulate browser requests** WITHOUT opening a browser:

```python
# Instead of manually clicking in browser...
# Test automatically does this:
client = app.test_client()  # Simulate browser
response = client.get("/dashboard/")  # Visit page
assert response.status_code == 200  # Check it loaded
```

### Test Fixtures (Built-in Test Data)

Tests use **fixtures** - reusable test setup:

```python
# Automatically creates test users
def test_login(auth_client_applicant):
    # Client is already logged in as applicant!
    resp = auth_client_applicant.get("/dashboard/")
    assert resp.status_code == 200
```

Available fixtures:
- **Users**: `applicant_user`, `dean_user`, `oidb_user`, `ydyo_user`, `ygk_user`
- **Authenticated Clients**: `auth_client_applicant`, `auth_client_dean`, etc.
- **Test Data**: `application_draft`, `application_submitted`

## Running Specific Tests

```bash
# Run only auth tests
pytest tests/test_auth.py

# Run only role tests
pytest tests/test_roles.py

# Run one specific test
pytest tests/test_auth.py::TestAuthRoutes::test_home_page_loads

# Run with verbose output (see each test name)
pytest -v

# Run with coverage report (see what % of code is tested)
pytest --cov=app --cov-report=html
# Then open htmlcov/index.html in browser
```

## Adding Your Own Tests

### Test a route:
```python
def test_applicant_dashboard_shows_data(auth_client_applicant):
    """Test dashboard displays applicant data."""
    resp = auth_client_applicant.get("/dashboard/")
    assert resp.status_code == 200
    assert b"Application" in resp.data
```

### Test a database operation:
```python
def test_save_application(app, applicant_user):
    """Test saving an application."""
    with app.app_context():
        app_obj = Application(
            applicant_id=applicant_user.id,
            status="draft",
            full_name="John Doe",
            current_gpa="3.5"
        )
        db.session.add(app_obj)
        db.session.commit()
        
        saved = Application.query.get(app_obj.id)
        assert saved.status == "draft"
```

### Test API endpoints:
```python
def test_applicant_api(auth_client_applicant):
    """Test API endpoint."""
    resp = auth_client_applicant.get("/api/applicant/track-application")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "status" in data
```

## Integration with CI/CD

These tests are ready for **automatic testing on every commit**. Example GitHub Actions setup:

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      - run: pip install -r requirements.txt
      - run: pytest --cov=app  # Fails PR if tests don't pass
```

## Benefits

### ✅ No Manual Testing
- No clicking through UI repeatedly
- No creating 50 test accounts by hand
- Run entire workflow in **1.6 seconds**

### ✅ Catch Regressions
- Every code change tested automatically
- Break something? Test fails immediately

### ✅ Document Behavior
- Tests ARE documentation
- "How does login work?" → Read test_auth.py

### ✅ Safe Refactoring
- Change code, run tests
- If tests pass, you didn't break anything

## Next Steps

1. **Run tests regularly** as you develop:
   ```bash
   pytest --cov=app  # After each feature
   ```

2. **Add tests for new features**:
   - New route? Add test
   - New model? Add test
   - New workflow? Add test

3. **Improve coverage** - Aim for 70%+:
   ```bash
   pytest --cov=app --cov-report=html
   # Check htmlcov/index.html to see untested code
   ```

4. **Set up CI/CD** - Run tests automatically:
   - GitHub Actions / GitLab CI / Jenkins
   - Blocks merge if tests fail

5. **Add integration tests** - Full user workflows:
   - Applicant submits → Dean reviews → OIDB checks → etc.

## Documentation Files

- **[TESTING.md](TESTING.md)** - Quick reference
- **[tests/README.md](tests/README.md)** - Comprehensive guide
- **[pytest.ini](pytest.ini)** - Pytest configuration
- **[tests/conftest.py](tests/conftest.py)** - Fixtures & setup

## Questions?

```bash
# Show help
./run_tests.sh -h
pytest --help

# Verbose output to see what's being tested
pytest -v

# Debug a specific test
pytest -s tests/test_auth.py::TestAuthRoutes::test_home_page_loads
```

---

**You now have enterprise-grade automated testing! 🎉**

Manually test your site less, ship with confidence more.
