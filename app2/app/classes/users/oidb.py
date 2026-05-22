"""OIDB role class."""

from __future__ import annotations

from typing import Any

from ...core import OperationResult, ErrorCode
from ...database import get_application_repository
from ...models import ApplicationDocument
from ..interfaces import IReviewer, IDocumentHandler
from .base import User


class Oidb(User, IReviewer, IDocumentHandler):
    """OIDB role."""

    def get_pending_applicants(self) -> list:
        """Get pending applications."""
        app_repo = get_application_repository()
        result = app_repo.get_pending_for_oidb()
        if result.success:
            return result.data or []
        return []

    def update_applicant_status(self, application_id: int, status: str) -> OperationResult:
        """Update application status. Returns OperationResult."""
        app_repo = get_application_repository()
        return app_repo.update_status(application_id, status)

    def forward_to_ydyo(self, application_id: int) -> OperationResult:
        """Forward application to YDYO. Returns OperationResult."""
        app_repo = get_application_repository()

        try:
            # Get application
            result = app_repo.find_by_id(application_id)
            if not result.success:
                return result
            if result.data is None:
                return OperationResult.error(
                    ErrorCode.APPLICATION_NOT_FOUND,
                    f"Application {application_id} not found."
                )

            app = result.data
            if app.status not in ("submitted", "returned"):
                return OperationResult.error(
                    ErrorCode.INVALID_STATUS_TRANSITION,
                    f"Cannot forward from status '{app.status}'."
                )

            # Update and commit
            app.status = "forwarded_to_ydyo"
            commit_result = app_repo.update(app)
            return commit_result
        except Exception as exc:
            app_repo.rollback()
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to forward application: {str(exc)}"
            )

    def forward_all_to_ydyo(self) -> OperationResult:
        """Forward all submitted applications to YDYO. Returns OperationResult."""
        from ... import db

        app_repo = get_application_repository()

        try:
            # Get all submitted applications
            result = app_repo.get_by_status("submitted")
            if not result.success:
                return result

            apps = result.data or []
            count = len(apps)

            # Update all
            for app in apps:
                app.status = "forwarded_to_ydyo"
                db.session.merge(app)

            # Commit all changes
            commit_result = app_repo.commit()
            if commit_result.success:
                commit_result.data = {"forwarded_count": count}
            return commit_result
        except Exception as exc:
            app_repo.rollback()
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to forward applications: {str(exc)}"
            )

    def return_application(self, application_id: int, notes: str) -> OperationResult:
        """Return application to applicant. Returns OperationResult."""
        app_repo = get_application_repository()

        if not notes or not notes.strip():
            return OperationResult.error(
                ErrorCode.MISSING_REQUIRED_FIELDS,
                "A reason is required when returning an application."
            )

        try:
            # Get application
            result = app_repo.find_by_id(application_id)
            if not result.success:
                return result
            if result.data is None:
                return OperationResult.error(
                    ErrorCode.APPLICATION_NOT_FOUND,
                    f"Application {application_id} not found."
                )

            app = result.data
            if app.status != "submitted":
                return OperationResult.error(
                    ErrorCode.INVALID_STATUS_TRANSITION,
                    "Cannot return this application."
                )

            # Update and commit
            app.status = "returned"
            app.oidb_notes = notes
            commit_result = app_repo.update(app)
            return commit_result
        except Exception as exc:
            app_repo.rollback()
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to return application: {str(exc)}"
            )

    def get_document(self, doc_id: int) -> OperationResult:
        """Get document. Returns OperationResult."""
        try:
            doc = ApplicationDocument.query.get(doc_id)
            if not doc:
                return OperationResult.error(
                    ErrorCode.DOCUMENT_NOT_FOUND,
                    f"Document {doc_id} not found."
                )
            return OperationResult.ok(data=doc)
        except Exception as exc:
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to retrieve document: {str(exc)}"
            )

    def upload(self, payload: dict[str, Any]) -> OperationResult:
        """Upload document. Returns OperationResult."""
        if not payload:
            return OperationResult.error(
                ErrorCode.VALIDATION_FAILED,
                "Payload cannot be empty."
            )
        return OperationResult.ok(data=payload)

    def validate(self, document_id: int) -> OperationResult:
        """Validate document. Returns OperationResult."""
        if document_id <= 0:
            return OperationResult.error(
                ErrorCode.VALIDATION_FAILED,
                "Document ID must be positive."
            )
        return OperationResult.ok()

    def retrieve(self, applicant_id: int) -> OperationResult:
        """Retrieve applicant documents. Returns OperationResult."""
        return OperationResult.ok(data=self.get_pending_applicants())
