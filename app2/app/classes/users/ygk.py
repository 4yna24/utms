"""YGK role class."""

from __future__ import annotations

from ...core import OperationResult, ErrorCode
from ..interfaces import IReviewer
from .base import User


class YGK(User, IReviewer):
    """YGK reviewer."""

    def get_pending_applicants(self) -> list:
        """Get pending applications for YGK review."""
        return []

    def update_applicant_status(self, applicant_id: int, status: str) -> OperationResult:
        """Update applicant status. Returns OperationResult."""
        if applicant_id <= 0 or not status:
            return OperationResult.error(
                ErrorCode.VALIDATION_FAILED,
                "Invalid applicant ID or status."
            )
        return OperationResult.ok()

    def create_intibak_table(self) -> OperationResult:
        """Create intibak table. Returns OperationResult."""
        return OperationResult.ok()

    def edit_course_match(self) -> OperationResult:
        """Edit course match. Returns OperationResult."""
        return OperationResult.ok()

    def save_intibak_table(self) -> OperationResult:
        """Save intibak table. Returns OperationResult."""
        return OperationResult.ok()
