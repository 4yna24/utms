"""Core domain entities for business layer shell."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Application:
    """Transfer application aggregate root."""

    application_id: int
    submission_date: datetime
    status: str
    student_id: int
    target_id: int


@dataclass(slots=True)
class Document:
    """Document metadata and status."""

    document_id: int
    applicant_id: int
    filename: str
    status: str


@dataclass(slots=True)
class IntibakTable:
    """Course equivalency table container."""

    table_id: int
    applicant_id: int
    state: str
