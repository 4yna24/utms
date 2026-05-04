"""Applicant API shell routes."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from .. import db
from ..config import (
    APPLICATION_CANCELLATION_ALLOWED,
    APPLICATION_DOCUMENT_SLOTS,
    APPLICATION_RESUBMISSION_ALLOWED,
    APPLICATION_SUBMISSION_PERIOD_OPEN,
    APPLICATION_TRACKER_STEPS,
    APPLICATION_STATUS_STEP,
    AVAILABLE_PROGRAMS,
    AVAILABLE_SEMESTERS,
)
from ..models import Application, ApplicationDocument
from .common import role_required

applicant_api_bp = Blueprint("applicant_api", __name__, url_prefix="/api/applicant")


@applicant_api_bp.route("/track-application", methods=["GET"])
@role_required("applicant")
def track_application():
    from flask import jsonify
    applicant_id = session.get("user_id")
    application = Application.query.filter_by(applicant_id=applicant_id).first()
    if application:
        return jsonify({"tab": "Track Application", "status": application.status})
    return jsonify({"tab": "Track Application", "status": "No application found"})


@applicant_api_bp.route("/submit-documents", methods=["GET"])
@role_required("applicant")
def submit_documents():
    applicant_id = session.get("user_id")
    application = Application.query.filter_by(applicant_id=applicant_id).first()
    return render_template(
        "applicant_submit.html",
        submission_open=APPLICATION_SUBMISSION_PERIOD_OPEN,
        document_slots=APPLICATION_DOCUMENT_SLOTS,
        available_programs=AVAILABLE_PROGRAMS,
        available_semesters=AVAILABLE_SEMESTERS,
        application=application,
        cancellation_allowed=APPLICATION_CANCELLATION_ALLOWED,
        resubmission_allowed=APPLICATION_RESUBMISSION_ALLOWED,
        tracker_steps=APPLICATION_TRACKER_STEPS,
        status_step=APPLICATION_STATUS_STEP,
    )


def _get_application_form_data() -> dict:
    is_enrolled = bool(request.form.get("is_currently_enrolled"))
    id_number = (request.form.get("id_number") or "").strip()
    target_program = (request.form.get("target_program") or "").strip()
    return {
        "full_name": (request.form.get("full_name") or "").strip(),
        "id_number": id_number,
        "student_number": id_number,
        "target_program": target_program,
        "target_department": target_program,
        "target_semester": (request.form.get("target_semester") or "").strip(),
        "current_gpa": (request.form.get("current_gpa") or "").strip(),
        "source_university": (request.form.get("source_university") or "").strip() if is_enrolled else "",
        "is_currently_enrolled": is_enrolled,
    }


def _validate_application_data(form_data: dict) -> tuple[bool, str]:
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


def _is_pdf_filename(filename: str) -> bool:
    return filename.lower().endswith(".pdf")


def _save_documents(application_id: int, upload_root: Path) -> list[ApplicationDocument]:
    docs = []
    for slot_def in APPLICATION_DOCUMENT_SLOTS:
        slot = slot_def["slot"]
        label = slot_def["label"]
        file_item = request.files.get(f"document_{slot}")
        if file_item is None or file_item.filename == "":
            raise ValueError(f"{label} is required.")
        if not _is_pdf_filename(file_item.filename):
            raise ValueError(f"{label} must be a PDF file.")
        safe_name = secure_filename(file_item.filename)
        stored_name = f"application_{application_id}_document_{slot}_{safe_name}"
        full_path = upload_root / stored_name
        file_item.save(full_path)
        docs.append(ApplicationDocument(
            application_id=application_id,
            document_slot=slot,
            original_name=safe_name,
            stored_name=stored_name,
            file_path=str(full_path),
        ))
    return docs


@applicant_api_bp.route("/submit-documents", methods=["POST"])
@role_required("applicant")
def create_application():
    if not APPLICATION_SUBMISSION_PERIOD_OPEN:
        flash("Application submission period is currently closed.")
        return redirect(url_for("applicant_api.submit_documents"))

    applicant_id = session.get("user_id")
    existing = Application.query.filter_by(applicant_id=applicant_id).first()
    if existing is not None:
        flash("You already have an application.")
        return redirect(url_for("applicant_api.submit_documents"))

    form_data = _get_application_form_data()
    valid, error_msg = _validate_application_data(form_data)
    if not valid:
        flash(error_msg)
        return redirect(url_for("applicant_api.submit_documents"))

    try:
        application = Application(applicant_id=applicant_id, status="submitted", **form_data)
        db.session.add(application)
        db.session.flush()

        upload_root = Path(current_app.config["APPLICATION_UPLOAD_FOLDER"])
        upload_root.mkdir(parents=True, exist_ok=True)

        for doc in _save_documents(application.id, upload_root):
            db.session.add(doc)

        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc))
        return redirect(url_for("applicant_api.submit_documents"))
    except IntegrityError:
        db.session.rollback()
        flash("Could not create application due to a data conflict.")
        return redirect(url_for("applicant_api.submit_documents"))
    except OSError:
        db.session.rollback()
        flash("Could not store uploaded files.")
        return redirect(url_for("applicant_api.submit_documents"))

    flash("Application submitted successfully.", "success")
    return redirect(url_for("dashboard.index"))


@applicant_api_bp.route("/resubmit-application", methods=["POST"])
@role_required("applicant")
def resubmit_application():
    if not APPLICATION_RESUBMISSION_ALLOWED:
        flash("Resubmission is not currently allowed.")
        return redirect(url_for("dashboard.index"))

    applicant_id = session.get("user_id")
    application = Application.query.filter_by(applicant_id=applicant_id).first()
    if not application or application.status != "returned":
        flash("Cannot resubmit this application.")
        return redirect(url_for("dashboard.index"))

    form_data = _get_application_form_data()
    valid, error_msg = _validate_application_data(form_data)
    if not valid:
        flash(error_msg)
        return redirect(url_for("dashboard.index"))

    try:
        for field, value in form_data.items():
            setattr(application, field, value)
        application.status = "submitted"
        application.oidb_notes = None

        # Delete old documents and save new ones
        for old_doc in list(application.documents):
            db.session.delete(old_doc)
        db.session.flush()

        upload_root = Path(current_app.config["APPLICATION_UPLOAD_FOLDER"])
        upload_root.mkdir(parents=True, exist_ok=True)

        for doc in _save_documents(application.id, upload_root):
            db.session.add(doc)

        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        flash(str(exc))
        return redirect(url_for("dashboard.index"))
    except OSError:
        db.session.rollback()
        flash("Could not store uploaded files.")
        return redirect(url_for("dashboard.index"))

    flash("Application resubmitted successfully.", "success")
    return redirect(url_for("dashboard.index"))


@applicant_api_bp.route("/cancel-application", methods=["POST"])
@role_required("applicant")
def cancel_application():
    if not APPLICATION_CANCELLATION_ALLOWED:
        flash("Cancellation is not currently allowed.")
        return redirect(url_for("dashboard.index"))

    applicant_id = session.get("user_id")
    application = Application.query.filter_by(applicant_id=applicant_id).first()
    if not application or application.status not in ("submitted",):
        flash("Cannot cancel this application.")
        return redirect(url_for("dashboard.index"))

    application.status = "cancelled"
    db.session.commit()
    flash("Application cancelled.", "success")
    return redirect(url_for("dashboard.index"))
