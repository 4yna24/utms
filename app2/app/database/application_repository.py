"""Application data repository - handles all Application model operations."""

from __future__ import annotations

from sqlalchemy.orm import selectinload

from .. import db
from ..core import OperationResult, ErrorCode
from ..models import Application, ApplicationDocument


class ApplicationRepository:
    """Data access layer for Application operations."""

    @staticmethod
    def find_by_applicant_id(applicant_id: int) -> OperationResult:
        """Find application by applicant ID."""
        try:
            app = Application.query.filter_by(applicant_id=applicant_id).first()
            if app:
                return OperationResult.ok(data=app)
            return OperationResult.ok(data=None)
        except Exception as exc:
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to find application: {str(exc)}"
            )

    @staticmethod
    def find_by_id(application_id: int) -> OperationResult:
        """Find application by ID."""
        try:
            app = Application.query.get(application_id)
            if app:
                return OperationResult.ok(data=app)
            return OperationResult.ok(data=None)
        except Exception as exc:
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to find application: {str(exc)}"
            )

    @staticmethod
    def create(applicant_id: int, **kwargs) -> OperationResult:
        """Create new application."""
        try:
            app = Application(applicant_id=applicant_id, **kwargs)
            db.session.add(app)
            db.session.flush()
            return OperationResult.ok(data=app)
        except Exception as exc:
            db.session.rollback()
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to create application: {str(exc)}"
            )

    @staticmethod
    def update_status(application_id: int, status: str) -> OperationResult:
        """Update application status."""
        try:
            app = Application.query.get(application_id)
            if not app:
                return OperationResult.error(
                    ErrorCode.APPLICATION_NOT_FOUND,
                    f"Application {application_id} not found."
                )
            app.status = status
            db.session.commit()
            return OperationResult.ok(data=app)
        except Exception as exc:
            db.session.rollback()
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to update status: {str(exc)}"
            )

    @staticmethod
    def update(application: Application) -> OperationResult:
        """Update entire application object."""
        try:
            db.session.merge(application)
            db.session.commit()
            return OperationResult.ok(data=application)
        except Exception as exc:
            db.session.rollback()
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to update application: {str(exc)}"
            )

    @staticmethod
    def commit() -> OperationResult:
        """Commit pending changes."""
        try:
            db.session.commit()
            return OperationResult.ok()
        except Exception as exc:
            db.session.rollback()
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to commit changes: {str(exc)}"
            )

    @staticmethod
    def rollback() -> OperationResult:
        """Rollback pending changes."""
        try:
            db.session.rollback()
            return OperationResult.ok()
        except Exception as exc:
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to rollback: {str(exc)}"
            )

    @staticmethod
    def get_pending_for_dean() -> OperationResult:
        """Get applications pending dean review."""
        try:
            apps = (
                Application.query.options(
                    selectinload(Application.documents),
                    selectinload(Application.applicant)
                )
                .filter(Application.status.in_(["forwarded_to_dean", "forwarded_to_ygk"]))
                .order_by(Application.created_at.desc())
                .all()
            )
            return OperationResult.ok(data=apps)
        except Exception as exc:
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to fetch pending applications: {str(exc)}"
            )

    @staticmethod
    def get_pending_for_oidb() -> OperationResult:
        """Get applications pending OIDB review."""
        try:
            apps = (
                Application.query.options(
                    selectinload(Application.documents),
                    selectinload(Application.applicant)
                )
                .order_by(Application.created_at.desc())
                .all()
            )
            return OperationResult.ok(data=apps)
        except Exception as exc:
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to fetch pending applications: {str(exc)}"
            )

    @staticmethod
    def get_pending_for_ydyo() -> OperationResult:
        """Get applications pending YDYO review."""
        try:
            apps = (
                Application.query.options(
                    selectinload(Application.documents),
                    selectinload(Application.applicant)
                )
                .filter_by(status="forwarded_to_ydyo")
                .order_by(Application.created_at.desc())
                .all()
            )
            return OperationResult.ok(data=apps)
        except Exception as exc:
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to fetch pending applications: {str(exc)}"
            )

    @staticmethod
    def delete_documents(application_id: int) -> OperationResult:
        """Delete all documents for an application."""
        try:
            docs = ApplicationDocument.query.filter_by(application_id=application_id).all()
            for doc in docs:
                db.session.delete(doc)
            return OperationResult.ok()
        except Exception as exc:
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to delete documents: {str(exc)}"
            )

    @staticmethod
    def get_by_status(status: str) -> OperationResult:
        """Get all applications with a specific status."""
        try:
            apps = Application.query.filter_by(status=status).all()
            return OperationResult.ok(data=apps)
        except Exception as exc:
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to fetch applications: {str(exc)}"
            )
