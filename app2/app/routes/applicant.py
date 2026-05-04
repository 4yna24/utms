"""Applicant API shell routes."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy.exc import IntegrityError
from werkzeug.utils import secure_filename

from .. import db
from ..config import APPLICATION_REQUIRED_DOCUMENT_SLOTS, APPLICATION_SUBMISSION_PERIOD_OPEN
from ..models import Application, ApplicationDocument
from .common import role_required

applicant_api_bp = Blueprint("applicant_api", __name__, url_prefix="/api/applicant")


@applicant_api_bp.route("/track-application", methods=["GET"])
@role_required("applicant")
def track_application():
    applicant_id = session.get("user_id")
    application = Application.query.filter_by(applicant_id=applicant_id).first()
    if application:
        return jsonify({"tab": "Track Application", "status": application.status})
    else:
        return jsonify({"tab": "Track Application", "status": "No application found"})


@applicant_api_bp.route("/submit-documents", methods=["GET"])
@role_required("applicant")
def submit_documents():
    applicant_id = session.get("user_id")
    application = Application.query.filter_by(applicant_id=applicant_id).first()
    return render_template(
        "applicant_submit.html",
        submission_open=APPLICATION_SUBMISSION_PERIOD_OPEN,
        document_slots=APPLICATION_REQUIRED_DOCUMENT_SLOTS,
        application=application,
    )


def _get_application_form_data() -> dict[str, str]:
    return {
        "full_name": (request.form.get("full_name") or "").strip(),
        "student_number": (request.form.get("student_number") or "").strip(),
        "source_university": (request.form.get("source_university") or "").strip(),
        "target_department": (request.form.get("target_department") or "").strip(),
        "current_gpa": (request.form.get("current_gpa") or "").strip(),
    }


def _validate_required_fields(form_data: dict[str, str]) -> bool:
    return all(bool(value) for value in form_data.values())


def _is_pdf_filename(filename: str) -> bool:
    return filename.lower().endswith(".pdf")


@applicant_api_bp.route("/submit-documents", methods=["POST"])
@role_required("applicant")
def create_application():
    if not APPLICATION_SUBMISSION_PERIOD_OPEN:
        flash("Application submission period is currently closed.")
        return redirect(url_for("applicant_api.submit_documents"))

    applicant_id = session.get("user_id")
    existing_application = Application.query.filter_by(applicant_id=applicant_id).first()
    if existing_application is not None:
        flash("You already have an application.")
        return redirect(url_for("applicant_api.submit_documents"))

    form_data = _get_application_form_data()
    if not _validate_required_fields(form_data):
        flash("All application fields are required.")
        return redirect(url_for("applicant_api.submit_documents"))

    uploaded_files: list[tuple[int, str, object]] = []
    for slot in APPLICATION_REQUIRED_DOCUMENT_SLOTS:
        file_item = request.files.get(f"document_{slot}")
        if file_item is None or file_item.filename == "":
            continue
        if not _is_pdf_filename(file_item.filename):
            flash(f"Document #{slot} must be a PDF file.")
            return redirect(url_for("applicant_api.submit_documents"))
        safe_original_name = secure_filename(file_item.filename)
        uploaded_files.append((slot, safe_original_name, file_item))

    try:
        application = Application(applicant_id=applicant_id, status="submitted", **form_data)
        db.session.add(application)
        db.session.flush()

        upload_root = Path(current_app.config["APPLICATION_UPLOAD_FOLDER"])
        upload_root.mkdir(parents=True, exist_ok=True)

        for slot, safe_original_name, file_item in uploaded_files:
            stored_name = f"application_{application.id}_document_{slot}_{safe_original_name}"
            full_path = upload_root / stored_name
            file_item.save(full_path)
            db.session.add(
                ApplicationDocument(
                    application_id=application.id,
                    document_slot=slot,
                    original_name=safe_original_name,
                    stored_name=stored_name,
                    file_path=str(full_path),
                )
            )

        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Could not create application due to a data conflict.")
        return redirect(url_for("applicant_api.submit_documents"))
    except OSError:
        db.session.rollback()
        flash("Could not store uploaded files.")
        return redirect(url_for("applicant_api.submit_documents"))

    flash("Application created successfully.")
    return redirect(url_for("applicant_api.submit_documents"))
