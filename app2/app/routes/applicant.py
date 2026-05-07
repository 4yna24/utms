"""Applicant blueprint — HTTP wiring only."""

from __future__ import annotations

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for

from ..classes.users import Applicant
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
from ..models import Application
from .common import role_required

applicant_api_bp = Blueprint("applicant_api", __name__, url_prefix="/api/applicant")


@applicant_api_bp.route("/track-application", methods=["GET"])
@role_required("applicant")
def track_application():
    from flask import jsonify
    application = Application.query.filter_by(applicant_id=session.get("user_id")).first()
    status = application.status if application else "No application found"
    return jsonify({"tab": "Track Application", "status": status})


@applicant_api_bp.route("/submit-documents", methods=["GET"])
@role_required("applicant")
def submit_documents():
    application = Application.query.filter_by(applicant_id=session.get("user_id")).first()
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


@applicant_api_bp.route("/submit-documents", methods=["POST"])
@role_required("applicant")
def create_application():
    if not APPLICATION_SUBMISSION_PERIOD_OPEN:
        flash("Application submission period is currently closed.")
        return redirect(url_for("applicant_api.submit_documents"))

    form_data = Applicant.parse_form_data(request.form)
    valid, msg = Applicant.validate_form_data(form_data)
    if not valid:
        flash(msg)
        return redirect(url_for("applicant_api.submit_documents"))

    applicant = Applicant(session["user_id"], session.get("user_email", ""), "applicant")
    success, msg = applicant.submit(
        form_data,
        current_app.config["APPLICATION_UPLOAD_FOLDER"],
        request.files,
        APPLICATION_DOCUMENT_SLOTS,
    )
    if not success:
        flash(msg)
        return redirect(url_for("applicant_api.submit_documents"))

    flash("Application submitted successfully.", "success")
    return redirect(url_for("dashboard.index"))


@applicant_api_bp.route("/resubmit-application", methods=["POST"])
@role_required("applicant")
def resubmit_application():
    if not APPLICATION_RESUBMISSION_ALLOWED:
        flash("Resubmission is not currently allowed.")
        return redirect(url_for("dashboard.index"))

    application = Application.query.filter_by(applicant_id=session.get("user_id")).first()
    if not application or application.status != "returned":
        flash("Cannot resubmit this application.")
        return redirect(url_for("dashboard.index"))

    form_data = Applicant.parse_form_data(request.form)
    valid, msg = Applicant.validate_form_data(form_data)
    if not valid:
        flash(msg)
        return redirect(url_for("dashboard.index"))

    applicant = Applicant(session["user_id"], session.get("user_email", ""), "applicant")
    success, msg = applicant.resubmit(
        application,
        form_data,
        current_app.config["APPLICATION_UPLOAD_FOLDER"],
        request.files,
        APPLICATION_DOCUMENT_SLOTS,
    )
    if not success:
        flash(msg)
        return redirect(url_for("dashboard.index"))

    flash("Application resubmitted successfully.", "success")
    return redirect(url_for("dashboard.index"))


@applicant_api_bp.route("/cancel-application", methods=["POST"])
@role_required("applicant")
def cancel_application():
    if not APPLICATION_CANCELLATION_ALLOWED:
        flash("Cancellation is not currently allowed.")
        return redirect(url_for("dashboard.index"))

    application = Application.query.filter_by(applicant_id=session.get("user_id")).first()
    if not application or application.status not in ("submitted",):
        flash("Cannot cancel this application.")
        return redirect(url_for("dashboard.index"))

    applicant = Applicant(session["user_id"], session.get("user_email", ""), "applicant")
    applicant.cancel(application)
    flash("Application cancelled.", "success")
    return redirect(url_for("dashboard.index"))
