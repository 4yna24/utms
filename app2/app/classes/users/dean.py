"""Dean office role class."""

from __future__ import annotations

from ...core import OperationResult, ErrorCode
from ...database import get_application_repository
from ..interfaces import IReviewer
from .base import User


class DeanOffice(User, IReviewer):
    """Dean office reviewer."""

    def get_pending_applicants(self) -> list:
        """Get pending applications for dean review."""
        app_repo = get_application_repository()
        result = app_repo.get_pending_for_dean()
        if result.success:
            return result.data or []
        return []

    def update_applicant_status(self, application_id: int, status: str) -> OperationResult:
        """Update application status. Returns OperationResult."""
        app_repo = get_application_repository()
        return app_repo.update_status(application_id, status)

    def forward_to_ygk(self, application_id: int, faculty: str) -> OperationResult:
        """Forward application to YGK. Returns OperationResult."""
        app_repo = get_application_repository()

        if not faculty or not faculty.strip():
            return OperationResult.error(
                ErrorCode.VALIDATION_FAILED,
                "A faculty must be selected before forwarding."
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
            if app.status != "forwarded_to_dean":
                return OperationResult.error(
                    ErrorCode.INVALID_STATUS_TRANSITION,
                    f"Cannot forward application in status '{app.status}'."
                )

            # Update application
            app.forwarded_faculty = faculty
            app.status = "forwarded_to_ygk"

            # Commit via repository
            commit_result = app_repo.update(app)
            return commit_result
        except Exception as exc:
            app_repo.rollback()
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to forward application: {str(exc)}"
            )

    def return_application(self, application_id: int, target: str, notes: str) -> OperationResult:
        """Return application to a previous stage with a reason note."""
        _target_status = {"applicant": "returned", "oidb": "submitted", "ydyo": "forwarded_to_ydyo"}
        if target not in _target_status:
            return OperationResult.error(
                ErrorCode.VALIDATION_FAILED,
                f"Invalid return target: '{target}'."
            )
        if not notes or not notes.strip():
            return OperationResult.error(
                ErrorCode.VALIDATION_FAILED,
                "A reason must be provided when returning an application."
            )

        app_repo = get_application_repository()
        result = app_repo.find_by_id(application_id)
        if not result.success:
            return result
        app = result.data
        if app is None:
            return OperationResult.error(
                ErrorCode.APPLICATION_NOT_FOUND,
                f"Application {application_id} not found."
            )
        if app.status != "forwarded_to_dean":
            return OperationResult.error(
                ErrorCode.INVALID_STATUS_TRANSITION,
                f"Cannot return application in status '{app.status}'."
            )

        app.dean_notes = notes.strip()
        app.status = _target_status[target]
        return app_repo.update(app)

    def forward_all_to_ygk(self) -> OperationResult:
        """Forward all pending applications to YGK. Returns OperationResult."""
        return OperationResult.error(
            ErrorCode.UNKNOWN_ERROR,
            "Auto-forward to YGK is not yet implemented."
        )
