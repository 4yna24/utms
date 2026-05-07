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

    # --- IDocumentHandler interface ---

    def upload(self, payload: dict[str, Any]) -> bool:
        return bool(payload)

    def validate(self, document_id: int) -> bool:
        return document_id > 0

    def retrieve(self, applicant_id: int) -> list:
        return []

    # --- Form helpers (static — no Flask context needed) ---

    @staticmethod
    def parse_form_data(form) -> dict:
        is_enrolled = bool(form.get("is_currently_enrolled"))
        id_number = (form.get("id_number") or "").strip()
        target_program = (form.get("target_program") or "").strip()
        return {
            "full_name": (form.get("full_name") or "").strip(),
            "id_number": id_number,
            "student_number": id_number,
            "target_program": target_program,
            "target_department": target_program,
            "target_semester": (form.get("target_semester") or "").strip(),
            "current_gpa": (form.get("current_gpa") or "").strip(),
            "source_university": (form.get("source_university") or "").strip() if is_enrolled else "",
            "is_currently_enrolled": is_enrolled,
        }

    @staticmethod
    def validate_form_data(form_data: dict) -> tuple[bool, str]:
        required = ["full_name", "id_number", "target_program", "target_semester", "current_gpa"]
        if not all(bool(form_data.get(k)) for k in required):
            return False, "All required fields must be filled."
        try:
            gpa = float(form_data["current_gpa"])
            if not (0.0 <= gpa <= 4.0):
                return False, "GPA must be between 0.00 and 4.00."
        except ValueError:
            return False, "GPA must be a valid number (e.g. 3.50)."
        return True, ""

    # --- Document saving ---

    def save_documents(self, application_id: int, upload_root, files, document_slots) -> list:
        from pathlib import Path
        from werkzeug.utils import secure_filename
        from ..models import ApplicationDocument

        docs = []
        for slot_def in document_slots:
            slot = slot_def["slot"]
            label = slot_def["label"]
            file_item = files.get(f"document_{slot}")
            if file_item is None or file_item.filename == "":
                raise ValueError(f"{label} is required.")
            if not file_item.filename.lower().endswith(".pdf"):
                raise ValueError(f"{label} must be a PDF file.")
            safe_name = secure_filename(file_item.filename)
            stored_name = f"application_{application_id}_document_{slot}_{safe_name}"
            full_path = Path(upload_root) / stored_name
            file_item.save(full_path)
            docs.append(ApplicationDocument(
                application_id=application_id,
                document_slot=slot,
                original_name=safe_name,
                stored_name=stored_name,
                file_path=str(full_path),
            ))
        return docs

    # --- Application lifecycle ---

    def submit(self, form_data: dict, upload_root, files, document_slots) -> tuple[bool, str]:
        from pathlib import Path
        from sqlalchemy.exc import IntegrityError
        from .. import db
        from ..models import Application

        if Application.query.filter_by(applicant_id=self.user_id).first() is not None:
            return False, "You already have an application."
        try:
            application = Application(applicant_id=self.user_id, status="submitted", **form_data)
            db.session.add(application)
            db.session.flush()
            root = Path(upload_root)
            root.mkdir(parents=True, exist_ok=True)
            for doc in self.save_documents(application.id, root, files, document_slots):
                db.session.add(doc)
            db.session.commit()
        except ValueError as exc:
            db.session.rollback()
            return False, str(exc)
        except IntegrityError:
            db.session.rollback()
            return False, "Could not create application due to a data conflict."
        except OSError:
            db.session.rollback()
            return False, "Could not store uploaded files."
        return True, ""

    def resubmit(self, application, form_data: dict, upload_root, files, document_slots) -> tuple[bool, str]:
        from pathlib import Path
        from .. import db

        try:
            for field, value in form_data.items():
                setattr(application, field, value)
            application.status = "submitted"
            application.oidb_notes = None
            for old_doc in list(application.documents):
                db.session.delete(old_doc)
            db.session.flush()
            root = Path(upload_root)
            root.mkdir(parents=True, exist_ok=True)
            for doc in self.save_documents(application.id, root, files, document_slots):
                db.session.add(doc)
            db.session.commit()
        except ValueError as exc:
            db.session.rollback()
            return False, str(exc)
        except OSError:
            db.session.rollback()
            return False, "Could not store uploaded files."
        return True, ""

    def cancel(self, application) -> tuple[bool, str]:
        from .. import db

        application.status = "cancelled"
        db.session.commit()
        return True, ""


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
