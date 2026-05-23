"""Pytest configuration and fixtures."""

import os
import tempfile
from pathlib import Path

import pytest
from flask import session

from app import create_app, db
from app.models import User, Application


@pytest.fixture
def app():
    """Create Flask app with test database."""
    # Create temp file for SQLite
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    
    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Flask CLI test runner."""
    return app.test_cli_runner()


@pytest.fixture
def db_instance(app):
    """Database instance for use in tests."""
    return db


# ============================================================================
# USER FIXTURES
# ============================================================================

@pytest.fixture
def applicant_user(app):
    """Create and return a test applicant user."""
    user = User(
        email="applicant@test.com",
        password_hash="hashed_password",
        role="applicant"
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def dean_user(app):
    """Create and return a test dean user."""
    user = User(
        email="dean@test.com",
        password_hash="hashed_password",
        role="dean"
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def oidb_user(app):
    """Create and return a test OIDB user."""
    user = User(
        email="oidb@test.com",
        password_hash="hashed_password",
        role="oidb"
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def ydyo_user(app):
    """Create and return a test YDYO user."""
    user = User(
        email="ydyo@test.com",
        password_hash="hashed_password",
        role="ydyo"
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def ygk_user(app):
    """Create and return a test YGK user."""
    user = User(
        email="ygk@test.com",
        password_hash="hashed_password",
        role="ygk"
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def applicant_user_2(app):
    """Create and return a second test applicant user."""
    user = User(
        email="applicant2@test.com",
        password_hash="hashed_password",
        role="applicant"
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def applicant_user_3(app):
    """Create and return a third test applicant user."""
    user = User(
        email="applicant3@test.com",
        password_hash="hashed_password",
        role="applicant"
    )
    db.session.add(user)
    db.session.commit()
    return user


# ============================================================================
# AUTHENTICATED CLIENT FIXTURES (use with client)
# ============================================================================

@pytest.fixture
def auth_client_applicant(client, applicant_user):
    """Client logged in as applicant."""
    with client.session_transaction() as sess:
        sess["user_id"] = applicant_user.id
        sess["user_email"] = applicant_user.email
        sess["user_role"] = applicant_user.role
    return client


@pytest.fixture
def auth_client_dean(client, dean_user):
    """Client logged in as dean."""
    with client.session_transaction() as sess:
        sess["user_id"] = dean_user.id
        sess["user_email"] = dean_user.email
        sess["user_role"] = dean_user.role
    return client


@pytest.fixture
def auth_client_oidb(client, oidb_user):
    """Client logged in as OIDB."""
    with client.session_transaction() as sess:
        sess["user_id"] = oidb_user.id
        sess["user_email"] = oidb_user.email
        sess["user_role"] = oidb_user.role
    return client


@pytest.fixture
def auth_client_ydyo(client, ydyo_user):
    """Client logged in as YDYO."""
    with client.session_transaction() as sess:
        sess["user_id"] = ydyo_user.id
        sess["user_email"] = ydyo_user.email
        sess["user_role"] = ydyo_user.role
    return client


@pytest.fixture
def auth_client_ygk(client, ygk_user):
    """Client logged in as YGK."""
    with client.session_transaction() as sess:
        sess["user_id"] = ygk_user.id
        sess["user_email"] = ygk_user.email
        sess["user_role"] = ygk_user.role
    return client


# ============================================================================
# APPLICATION FIXTURES
# ============================================================================

@pytest.fixture
def application_draft(app, applicant_user):
    """Create a draft application."""
    app_obj = Application(
        applicant_id=applicant_user.id,
        status="draft",
        id_number="123456789",
        full_name="John Doe",
        target_program="Computer Engineering",
        target_semester="Fall 2024",
        current_gpa="3.5"
    )
    db.session.add(app_obj)
    db.session.commit()
    return app_obj


@pytest.fixture
def application_submitted(app, applicant_user_2):
    """Create a submitted application."""
    app_obj = Application(
        applicant_id=applicant_user_2.id,
        status="submitted",
        id_number="123456789",
        full_name="John Doe",
        target_program="Computer Engineering",
        target_semester="Fall 2024",
        is_currently_enrolled=False,
        current_gpa="3.5"
    )
    db.session.add(app_obj)
    db.session.commit()
    return app_obj
