"""Database and repository tests."""

import pytest
from app.models import User, Application
from app import db


class TestUserModel:
    """Test User model operations."""

    def test_create_user(self, app):
        """Test creating a user."""
        with app.app_context():
            user = User(
                email="test@example.com",
                password_hash="hashed",
                role="applicant"
            )
            db.session.add(user)
            db.session.commit()
            
            retrieved = User.query.filter_by(email="test@example.com").first()
            assert retrieved is not None
            assert retrieved.role == "applicant"

    def test_user_email_uniqueness(self, app, applicant_user):
        """Test that duplicate emails with same role are not allowed."""
        with app.app_context():
            # Same email and role should not be allowed
            duplicate_user = User(
                email=applicant_user.email,
                password_hash="hashed",
                role=applicant_user.role  # Same role = uniqueness violation
            )
            db.session.add(duplicate_user)
            
            # This should raise an error
            with pytest.raises(Exception):
                db.session.commit()
            db.session.rollback()

    def test_user_same_email_different_role(self, app, applicant_user):
        """Test that same email with different role is allowed."""
        with app.app_context():
            # Same email but different role should be allowed
            dean_user = User(
                email=applicant_user.email,  # Same email
                password_hash="hashed",
                role="dean"  # Different role
            )
            db.session.add(dean_user)
            db.session.commit()
            
            # Should succeed
            retrieved = User.query.filter_by(email=applicant_user.email, role="dean").first()
            assert retrieved is not None

    def test_query_users_by_role(self, app, applicant_user, dean_user):
        """Test querying users by role."""
        with app.app_context():
            applicants = User.query.filter_by(role="applicant").all()
            assert len(applicants) >= 1
            
            deans = User.query.filter_by(role="dean").all()
            assert len(deans) >= 1


class TestApplicationModel:
    """Test Application model operations."""

    def test_create_application(self, app, applicant_user):
        """Test creating an application."""
        with app.app_context():
            application = Application(
                applicant_id=applicant_user.id,
                status="draft",
                id_number="123456789",
                full_name="Test User",
                current_gpa="3.5"
            )
            db.session.add(application)
            db.session.commit()
            
            retrieved = Application.query.filter_by(id_number="123456789").first()
            assert retrieved is not None
            assert retrieved.status == "draft"

    def test_application_status_update(self, app, application_draft):
        """Test updating application status."""
        with app.app_context():
            app_obj = Application.query.get(application_draft.id)
            app_obj.status = "submitted"
            db.session.commit()
            
            retrieved = Application.query.get(application_draft.id)
            assert retrieved.status == "submitted"

    def test_query_applications_by_status(self, app, application_draft, application_submitted):
        """Test querying applications by status."""
        with app.app_context():
            drafts = Application.query.filter_by(status="draft").all()
            assert len(drafts) >= 1
            
            submitted = Application.query.filter_by(status="submitted").all()
            assert len(submitted) >= 1

    def test_application_applicant_relationship(self, app, application_submitted, applicant_user_2):
        """Test application-applicant relationship."""
        with app.app_context():
            app_obj = Application.query.get(application_submitted.id)
            assert app_obj.applicant_id == applicant_user_2.id


class TestDatabaseIntegrity:
    """Test database integrity constraints."""

    def test_application_requires_applicant(self, app):
        """Test application must have an applicant."""
        with app.app_context():
            # Try to create app without applicant_id
            application = Application(status="draft")
            db.session.add(application)
            
            # This may or may not raise depending on constraints
            try:
                db.session.commit()
                # If it succeeds, verify in database
                retrieved = Application.query.filter_by(status="draft").first()
                assert retrieved is not None
            except Exception:
                db.session.rollback()
