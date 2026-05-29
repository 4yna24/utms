"""Pytest configuration and fixtures."""

import os
import tempfile

import pytest
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models import ApplicationORM, UserORM


@pytest.fixture
def app():
    """Create Flask app with isolated temporary SQLite database."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

    test_app = create_app(test_config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "WTF_CSRF_ENABLED": False,
    })

    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


# ── User helpers ──────────────────────────────────────────────────────────────

def _make_user(email: str, role: str, password: str = "test") -> UserORM:
    user = UserORM(email=email, role=role, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def applicant_user(app):
    return _make_user("applicant@test.com", "applicant")


@pytest.fixture
def applicant_user_2(app):
    return _make_user("applicant2@test.com", "applicant")


@pytest.fixture
def dean_user(app):
    return _make_user("dean@test.com", "dean")


@pytest.fixture
def oidb_user(app):
    return _make_user("oidb@test.com", "oidb")


@pytest.fixture
def ydyo_user(app):
    return _make_user("ydyo@test.com", "ydyo")


@pytest.fixture
def ygk_user(app):
    return _make_user("ygk@test.com", "ygk")


# ── Auth client helpers ───────────────────────────────────────────────────────

def _set_session(client, user):
    with client.session_transaction() as sess:
        sess["user_id"] = user.id
        sess["user_email"] = user.email
        sess["user_role"] = user.role
    return client


@pytest.fixture
def auth_client_applicant(client, applicant_user):
    return _set_session(client, applicant_user)


@pytest.fixture
def auth_client_dean(client, dean_user):
    return _set_session(client, dean_user)


@pytest.fixture
def auth_client_oidb(client, oidb_user):
    return _set_session(client, oidb_user)


@pytest.fixture
def auth_client_ydyo(client, ydyo_user):
    return _set_session(client, ydyo_user)


@pytest.fixture
def auth_client_ygk(client, ygk_user):
    return _set_session(client, ygk_user)


# ── Application helpers ───────────────────────────────────────────────────────

def _make_application(applicant_id: int, status: str, **kwargs) -> ApplicationORM:
    defaults = dict(
        full_name="Test Applicant",
        id_number="123456789",
        target_program="Computer Engineering",
        target_semester="2025–2026 / Fall",
        is_currently_enrolled=False,
        current_gpa="3.50",
    )
    defaults.update(kwargs)
    app_obj = ApplicationORM(applicant_id=applicant_id, status=status, **defaults)
    db.session.add(app_obj)
    db.session.commit()
    return app_obj


@pytest.fixture
def application_submitted(app, applicant_user):
    """Application in submitted status owned by applicant_user."""
    return _make_application(applicant_user.id, "submitted")


@pytest.fixture
def application_returned(app, applicant_user):
    """Application returned to applicant."""
    return _make_application(
        applicant_user.id, "returned",
        full_name="Returned Applicant",
        id_number="999888777",
        oidb_notes="Missing transcript.",
    )


@pytest.fixture
def application_forwarded_to_ydyo(app, applicant_user_2):
    """Application forwarded to YDYO (for cancel-forward tests)."""
    return _make_application(
        applicant_user_2.id, "forwarded_to_ydyo",
        full_name="Forwarded Applicant",
        id_number="444555666",
    )
