"""Role-oriented domain user classes."""

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

    def get_id(self) -> int:
        return self.user_id


class Applicant(User, IDocumentHandler):
    """Applicant business role."""

    def upload(self, payload: dict[str, Any]) -> bool:
        return bool(payload)

    def validate(self, document_id: int) -> bool:
        return document_id > 0

    def retrieve(self, applicant_id: int) -> list:
        return []

    def submit_document(self, payload: dict[str, Any]) -> bool:
        return self.upload(payload)

    def cancel_application(self) -> bool:
        return True

    def resubmit_documents(self) -> bool:
        return True


class DeanOffice(User, IReviewer):
    """Dean office reviewer."""

    def get_pending_applicants(self) -> list:
        from ..models import Application
        from sqlalchemy.orm import selectinload
        return (
            Application.query
            .options(selectinload(Application.documents), selectinload(Application.applicant))
            .filter(Application.status.in_(["forwarded_to_dean", "forwarded_to_ygk"]))
            .order_by(Application.created_at.desc())
            .all()
        )

    def update_applicant_status(self, application_id: int, status: str) -> bool:
        from .. import db
        from ..models import Application
        app = Application.query.get(application_id)
        if not app:
            return False
        app.status = status
        db.session.commit()
        return True

    def forward_to_ygk(self, application_id: int) -> tuple[bool, str]:
        from .. import db
        from ..models import Application
        app = Application.query.get(application_id)
        if not app or app.status != "forwarded_to_dean":
            return False, "Cannot forward this application."
        app.status = "forwarded_to_ygk"
        db.session.commit()
        return True, f"Application #{application_id} forwarded to YGK."

    def forward_all_to_ygk(self) -> int:
        from .. import db
        from ..models import Application
        apps = Application.query.filter_by(status="forwarded_to_dean").all()
        count = len(apps)
        for a in apps:
            a.status = "forwarded_to_ygk"
        db.session.commit()
        return count


class YGK(User, IReviewer):
    """YGK reviewer."""

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
    """OIDB role."""

    def get_pending_applicants(self) -> list:
        from ..models import Application
        from sqlalchemy.orm import selectinload
        return (
            Application.query
            .options(selectinload(Application.documents), selectinload(Application.applicant))
            .order_by(Application.created_at.desc())
            .all()
        )

    def update_applicant_status(self, application_id: int, status: str) -> bool:
        from .. import db
        from ..models import Application
        app = Application.query.get(application_id)
        if not app:
            return False
        app.status = status
        db.session.commit()
        return True

    def forward_to_ydyo(self, application_id: int) -> tuple[bool, str]:
        from .. import db
        from ..models import Application
        app = Application.query.get(application_id)
        if not app or app.status not in ("submitted", "returned"):
            return False, "Cannot forward this application."
        app.status = "forwarded_to_ydyo"
        db.session.commit()
        return True, f"Application #{application_id} forwarded to YDYO."

    def forward_all_to_ydyo(self) -> int:
        from .. import db
        from ..models import Application
        apps = Application.query.filter_by(status="submitted").all()
        count = len(apps)
        for a in apps:
            a.status = "forwarded_to_ydyo"
        db.session.commit()
        return count

    def return_application(self, application_id: int, notes: str) -> tuple[bool, str]:
        from .. import db
        from ..models import Application
        app = Application.query.get(application_id)
        if not app or app.status not in ("submitted",):
            return False, "Cannot return this application."
        if not notes.strip():
            return False, "A reason is required when returning an application."
        app.status = "returned"
        app.oidb_notes = notes
        db.session.commit()
        return True, f"Application #{application_id} returned to applicant."

    def get_document(self, doc_id: int):
        from ..models import ApplicationDocument
        return ApplicationDocument.query.get(doc_id)

    def upload(self, payload: dict[str, Any]) -> bool:
        return bool(payload)

    def validate(self, document_id: int) -> bool:
        return document_id > 0

    def retrieve(self, applicant_id: int) -> list:
        return self.get_pending_applicants()


class Ydyo(User, IReviewer):
    """YDYO role."""

    def get_pending_applicants(self) -> list[dict[str, Any]]:
        return []

    def update_applicant_status(self, applicant_id: int, status: str) -> bool:
        return applicant_id > 0 and bool(status)

    def retrieve_applications(self) -> list[dict[str, Any]]:
        return []

    def set_prepschool_status(self) -> bool:
        return True
