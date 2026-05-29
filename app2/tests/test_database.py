"""Database model and repository tests."""

import pytest

from app import db
from app.models import ApplicationORM, UserORM
from app.database.application_repository import ApplicationRepository


class TestUserModel:
    def test_create_user(self, app):
        from werkzeug.security import generate_password_hash
        user = UserORM(
            email="new@test.com",
            role="applicant",
            password_hash=generate_password_hash("secret"),
        )
        db.session.add(user)
        db.session.commit()

        retrieved = UserORM.query.filter_by(email="new@test.com").first()
        assert retrieved is not None
        assert retrieved.role == "applicant"

    def test_password_check(self, app, applicant_user):
        assert applicant_user.check_password("test")
        assert not applicant_user.check_password("wrong")

    def test_unique_email_role_constraint(self, app, applicant_user):
        from werkzeug.security import generate_password_hash
        duplicate = UserORM(
            email=applicant_user.email,
            role=applicant_user.role,
            password_hash=generate_password_hash("x"),
        )
        db.session.add(duplicate)
        with pytest.raises(Exception):
            db.session.commit()
        db.session.rollback()

    def test_same_email_different_role_allowed(self, app, applicant_user):
        from werkzeug.security import generate_password_hash
        dean = UserORM(
            email=applicant_user.email,
            role="dean",
            password_hash=generate_password_hash("x"),
        )
        db.session.add(dean)
        db.session.commit()
        assert UserORM.query.filter_by(email=applicant_user.email, role="dean").first() is not None

    def test_query_by_role(self, app, applicant_user, dean_user):
        applicants = UserORM.query.filter_by(role="applicant").all()
        assert len(applicants) >= 1
        deans = UserORM.query.filter_by(role="dean").all()
        assert len(deans) >= 1


class TestApplicationModel:
    def test_create_application(self, app, applicant_user):
        app_obj = ApplicationORM(
            applicant_id=applicant_user.id,
            status="submitted",
            full_name="Test User",
            id_number="123",
            current_gpa="3.5",
        )
        db.session.add(app_obj)
        db.session.commit()
        retrieved = ApplicationORM.query.filter_by(applicant_id=applicant_user.id).first()
        assert retrieved is not None
        assert retrieved.status == "submitted"

    def test_status_update(self, app, application_submitted):
        app_obj = ApplicationORM.query.get(application_submitted.id)
        app_obj.status = "forwarded_to_ydyo"
        db.session.commit()
        assert ApplicationORM.query.get(application_submitted.id).status == "forwarded_to_ydyo"

    def test_oidb_notes_stored(self, app, application_submitted):
        app_obj = ApplicationORM.query.get(application_submitted.id)
        app_obj.status = "returned"
        app_obj.oidb_notes = "Missing transcript"
        db.session.commit()
        refreshed = ApplicationORM.query.get(application_submitted.id)
        assert refreshed.oidb_notes == "Missing transcript"

    def test_applicant_relationship(self, app, application_submitted, applicant_user):
        app_obj = ApplicationORM.query.get(application_submitted.id)
        assert app_obj.applicant_id == applicant_user.id
        assert app_obj.applicant is not None
        assert app_obj.applicant.email == applicant_user.email


class TestApplicationRepository:
    def test_find_by_id_found(self, app, application_submitted):
        result = ApplicationRepository.find_by_id(application_submitted.id)
        assert result.success
        assert result.data is not None
        assert result.data.id == application_submitted.id

    def test_find_by_id_not_found(self, app):
        result = ApplicationRepository.find_by_id(99999)
        # Repository returns ok(data=None) when not found
        assert result.success
        assert result.data is None

    def test_find_by_applicant_id(self, app, application_submitted, applicant_user):
        result = ApplicationRepository.find_by_applicant_id(applicant_user.id)
        assert result.success
        assert result.data is not None

    def test_get_by_status(self, app, application_submitted, application_forwarded_to_ydyo):
        result = ApplicationRepository.get_by_status("submitted")
        assert result.success
        ids = [a.id for a in result.data]
        assert application_submitted.id in ids
        assert application_forwarded_to_ydyo.id not in ids

    def test_update_status(self, app, application_submitted):
        result = ApplicationRepository.update_status(application_submitted.id, "returned")
        assert result.success
        assert ApplicationORM.query.get(application_submitted.id).status == "returned"

    def test_get_pending_for_oidb(self, app, application_submitted):
        result = ApplicationRepository.get_pending_for_oidb()
        assert result.success
        assert any(a.id == application_submitted.id for a in result.data)

    def test_get_pending_for_ydyo(self, app, application_forwarded_to_ydyo, application_submitted):
        result = ApplicationRepository.get_pending_for_ydyo()
        assert result.success
        ids = [a.id for a in result.data]
        assert application_forwarded_to_ydyo.id in ids
        assert application_submitted.id not in ids  # submitted is not yet at YDYO
