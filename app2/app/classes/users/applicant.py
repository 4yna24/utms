"""Applicant role class."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from ...core import OperationResult, ErrorCode
from ...database import get_application_repository
from ...models import ApplicationDocumentORM
from ..interfaces import IDocumentHandler
from .base import User


class Applicant(User, IDocumentHandler):
    """Applicant business role."""

    # --- IDocumentHandler interface ---

    def upload(self, payload: dict[str, Any]) -> OperationResult:
        """Upload documents. Returns OperationResult with upload status."""
        if not payload:
            return OperationResult.error(
                ErrorCode.VALIDATION_FAILED,
                "Payload cannot be empty."
            )
        return OperationResult.ok(data=payload)

    def validate(self, document_id: int) -> OperationResult:
        """Validate document ID. Returns OperationResult."""
        if document_id <= 0:
            return OperationResult.error(
                ErrorCode.VALIDATION_FAILED,
                "Document ID must be positive."
            )
        return OperationResult.ok()

    def retrieve(self, applicant_id: int) -> OperationResult:
        """Retrieve applicant documents. Returns OperationResult with document list."""
        # TODO: Implement document retrieval from database
        return OperationResult.ok(data=[])

    # --- Form helpers (static — no Flask context needed) ---

    @staticmethod
    def parse_form_data(form) -> dict:
        """Parse and normalize form data for application submission."""
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
            "source_university": (form.get("source_university") or "").strip(),
            "is_currently_enrolled": True,
        }

    @staticmethod
    def validate_form_data(form_data: dict) -> OperationResult:
        """Validate application form data. Returns OperationResult."""
        required = [
            "full_name",
            "id_number",
            "target_program",
            "target_semester",
            "current_gpa",
            "source_university",
        ]
        if not all(bool(form_data.get(k)) for k in required):
            return OperationResult.error(
                ErrorCode.MISSING_REQUIRED_FIELDS,
                "All required fields must be filled."
            )
        try:
            gpa = float(form_data["current_gpa"])
            if not (0.0 <= gpa <= 4.0):
                return OperationResult.error(
                    ErrorCode.GPA_OUT_OF_RANGE,
                    "GPA must be between 0.00 and 4.00."
                )
        except ValueError:
            return OperationResult.error(
                ErrorCode.VALIDATION_FAILED,
                "GPA must be a valid number (e.g. 3.50)."
            )
        return OperationResult.ok()

    # --- Document saving ---

    def save_documents(self, application_id: int, upload_root, files, document_slots) -> list:
        """Save uploaded documents to disk. Returns list of ApplicationDocument objects."""
        docs = []
        for slot_def in document_slots:
            slot = slot_def["slot"]
            label = slot_def["label"]
            file_item = files.get(f"document_{slot}")
            if file_item is None or file_item.filename == "":
                continue
            if not file_item.filename.lower().endswith(".pdf"):
                raise ValueError(f"{label} must be a PDF file.")
            safe_name = secure_filename(file_item.filename)
            stored_name = f"application_{application_id}_document_{slot}_{safe_name}"
            full_path = Path(upload_root) / stored_name
            file_item.save(full_path)
            docs.append(ApplicationDocumentORM(
                application_id=application_id,
                document_slot=slot,
                original_name=safe_name,
                stored_name=stored_name,
                file_path=str(full_path),
            ))
        return docs

    # --- Application lifecycle ---

    def submit(
        self, form_data: dict, upload_root, files, document_slots
    ) -> OperationResult:
        """Submit new application. Returns OperationResult with created Application."""
        app_repo = get_application_repository()

        # Check if applicant already has an application
        result = app_repo.find_by_applicant_id(self.user_id)
        if not result.success:
            return result
        if result.data is not None:
            return OperationResult.error(
                ErrorCode.APPLICATION_EXISTS,
                "You already have an application."
            )

        try:
            # Create application
            create_result = app_repo.create(
                applicant_id=self.user_id,
                status="submitted",
                **form_data
            )
            if not create_result.success:
                return create_result

            application = create_result.data
            root = Path(upload_root)
            root.mkdir(parents=True, exist_ok=True)

            # Save documents and add to repository
            docs = self.save_documents(
                application.id, root, files, document_slots
            )
            add_docs_result = app_repo.add_documents(docs)
            if not add_docs_result.success:
                app_repo.rollback()
                return add_docs_result

            # Commit all changes
            commit_result = app_repo.commit()
            if not commit_result.success:
                return commit_result

            return OperationResult.ok(data=application)
        except ValueError as exc:
            app_repo.rollback()
            return OperationResult.error(
                ErrorCode.INVALID_FILE_FORMAT,
                str(exc)
            )
        except OSError:
            app_repo.rollback()
            return OperationResult.error(
                ErrorCode.FILE_NOT_SAVED,
                "Could not store uploaded files."
            )
        except Exception as exc:
            app_repo.rollback()
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Submission failed: {str(exc)}"
            )

    def resubmit(
        self, application, form_data: dict, upload_root, files, document_slots
    ) -> OperationResult:
        """Resubmit application. Returns OperationResult."""
        app_repo = get_application_repository()

        try:
            # Update application fields
            for field, value in form_data.items():
                setattr(application, field, value)
            application.status = "submitted"
            application.oidb_notes = None

            # Delete old documents
            old_docs = list(application.documents)
            for old_doc in old_docs:
                del_result = app_repo.delete_document(old_doc)
                if not del_result.success:
                    app_repo.rollback()
                    return del_result

            # Save new documents
            root = Path(upload_root)
            root.mkdir(parents=True, exist_ok=True)
            docs = self.save_documents(
                application.id, root, files, document_slots
            )
            add_docs_result = app_repo.add_documents(docs)
            if not add_docs_result.success:
                app_repo.rollback()
                return add_docs_result

            # Commit all changes
            commit_result = app_repo.commit()
            if not commit_result.success:
                return commit_result

            return OperationResult.ok(data=application)
        except ValueError as exc:
            app_repo.rollback()
            return OperationResult.error(
                ErrorCode.INVALID_FILE_FORMAT,
                str(exc)
            )
        except OSError:
            app_repo.rollback()
            return OperationResult.error(
                ErrorCode.FILE_NOT_SAVED,
                "Could not store uploaded files."
            )
        except Exception as exc:
            app_repo.rollback()
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Resubmission failed: {str(exc)}"
            )

    def cancel(self, application) -> OperationResult:
        """Cancel application. Returns OperationResult."""
        app_repo = get_application_repository()

        try:
            application.status = "cancelled"
            commit_result = app_repo.commit()
            if not commit_result.success:
                return commit_result
            return OperationResult.ok(data=application)
        except Exception as exc:
            app_repo.rollback()
            return OperationResult.error(
                ErrorCode.DB_ERROR,
                f"Failed to cancel application: {str(exc)}"
            )
