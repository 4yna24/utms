"""Dean routes — thin HTTP layer."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from ..classes import DeanOffice
from ..config import AVAILABLE_FACULTIES
from .common import role_required

dean_api_bp = Blueprint("dean_api", __name__, url_prefix="/api/dean")


def _get_service() -> DeanOffice:
    """Get DeanOffice instance for current user."""
    return DeanOffice(
        user_id=session.get("user_id", 0),
        email=session.get("user_email", ""),
        role="dean"
    )


@dean_api_bp.route("/check-applicants", methods=["GET"])
@role_required("dean")
def check_applicants():
    """Show pending applicants."""
    service = _get_service()
    applications = service.get_pending_applicants()
    return render_template(
        "dean_check_applicants.html",
        applications=applications,
        available_faculties=AVAILABLE_FACULTIES,
    )


@dean_api_bp.route("/forward-to-ygk/<int:application_id>", methods=["POST"])
@role_required("dean")
def forward_to_ygk(application_id):
    """Forward application to YGK."""
    faculty = (request.form.get("faculty") or "").strip()
    service = _get_service()
    
    result = service.forward_to_ygk(application_id, faculty)
    
    if result.success:
        flash("Application forwarded to YGK successfully.", "success")
    else:
        flash(result.error_msg, "error")
    
    return redirect(url_for("dean_api.check_applicants"))


@dean_api_bp.route("/forward-all-to-ygk", methods=["POST"])
@role_required("dean")
def forward_all_to_ygk():
    """Forward all pending to YGK."""
    service = _get_service()
    
    result = service.forward_all_to_ygk()
    
    if result.success:
        flash("All applications forwarded to YGK successfully.", "success")
    else:
        flash(result.error_msg, "error")
    
    return redirect(url_for("dean_api.check_applicants"))
