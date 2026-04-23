"""Abstract interfaces for shared domain behaviors."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IReviewer(ABC):
    """Shared applicant review behaviors across reviewer roles."""

    @abstractmethod
    def get_pending_applicants(self) -> list[dict[str, Any]]:
        """Return pending applicants for the reviewer."""

    @abstractmethod
    def update_applicant_status(self, applicant_id: int, status: str) -> bool:
        """Update applicant review status."""


class IDocumentHandler(ABC):
    """Shared document handling behaviors."""

    @abstractmethod
    def upload(self, payload: dict[str, Any]) -> bool:
        """Handle document upload action."""

    @abstractmethod
    def validate(self, document_id: int) -> bool:
        """Validate uploaded document."""

    @abstractmethod
    def retrieve(self, applicant_id: int) -> list[dict[str, Any]]:
        """Retrieve documents for applicant."""
