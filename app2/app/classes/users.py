"""Role-oriented domain user classes for Phase 1 shell."""

from __future__ import annotations

from abc import ABC
from typing import Any

from .interfaces import IDocumentHandler, IReviewer


class User(ABC):
    """Abstract system user."""

    def __init__(self, user_id: int, email: str, role: str) -> None:
        self.user_id = user_id
        self.email = email
        self.role = role

    def login(self) -> bool:
        """User login state transition placeholder."""
        return True

    def logout(self) -> bool:
        """User logout state transition placeholder."""
        return True

    def get_id(self) -> int:
        """Return unique identifier."""
        return self.user_id


class Applicant(User, IDocumentHandler):
    """Applicant business role shell."""

    def upload(self, payload: dict[str, Any]) -> bool:
        return bool(payload)

    def validate(self, document_id: int) -> bool:
        return document_id > 0

    def retrieve(self, applicant_id: int) -> list[dict[str, Any]]:
        return [{"applicant_id": applicant_id, "state": "shell"}]

    def submit_document(self, payload: dict[str, Any]) -> bool:
        return self.upload(payload)

    def track_document(self) -> dict[str, str]:
        return {"status": "Phase 1 shell"}

    def cancel_application(self) -> bool:
        return True

    def resubmit_documents(self) -> bool:
        return True


class DeanOffice(User, IReviewer):
    """Dean office reviewer shell."""

    def get_pending_applicants(self) -> list[dict[str, Any]]:
        return []

    def update_applicant_status(self, applicant_id: int, status: str) -> bool:
        return applicant_id > 0 and bool(status)

    def receive_documents(self) -> list[dict[str, Any]]:
        return []

    def forward_documents(self) -> bool:
        return True


class YGK(User, IReviewer):
    """YGK reviewer shell."""

    def get_pending_applicants(self) -> list[dict[str, Any]]:
        return []

    def update_applicant_status(self, applicant_id: int, status: str) -> bool:
        return applicant_id > 0 and bool(status)

    def create_intibak_table(self) -> bool:
        return True

    def edit_course_match(self) -> bool:
        return True

    def save_intibak_table(self) -> bool:
        return True


class Oidb(User, IReviewer, IDocumentHandler):
    """OIDB role shell."""

    def get_pending_applicants(self) -> list[dict[str, Any]]:
        return []

    def update_applicant_status(self, applicant_id: int, status: str) -> bool:
        return applicant_id > 0 and bool(status)

    def upload(self, payload: dict[str, Any]) -> bool:
        return bool(payload)

    def validate(self, document_id: int) -> bool:
        return document_id > 0

    def retrieve(self, applicant_id: int) -> list[dict[str, Any]]:
        return [{"applicant_id": applicant_id, "state": "shell"}]

    def retrieve_documents(self) -> list[dict[str, Any]]:
        return []

    def edit_documents(self) -> bool:
        return True

    def create_waitlist_table(self) -> bool:
        return True


class Ydyo(User, IReviewer):
    """YDYO role shell."""

    def get_pending_applicants(self) -> list[dict[str, Any]]:
        return []

    def update_applicant_status(self, applicant_id: int, status: str) -> bool:
        return applicant_id > 0 and bool(status)

    def retrieve_applications(self) -> list[dict[str, Any]]:
        return []

    def set_prepschool_status(self) -> bool:
        return True
