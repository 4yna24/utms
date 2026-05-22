"""YGK routes — thin HTTP layer."""

from __future__ import annotations

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from ..classes import YGK
from ..database import get_application_repository
from .common import role_required

ygk_api_bp = Blueprint("ygk_api", __name__, url_prefix="/api/ygk")


def _get_service() -> YGK:
    """Get YGK instance for current user."""
    return YGK(
        user_id=session.get("user_id", 0),
        email=session.get("user_email", ""),
        role="ygk"
    )


@ygk_api_bp.route("/check-applicants", methods=["GET"])
@role_required("ygk")
def check_applicants():
    """Show applications to check."""
    app_repo = get_application_repository()
    result = app_repo.get_by_status("forwarded_to_ygk")
    
    applications = result.data if result.success else []
    
    return render_template("ygk_check_applicants.html", applications=applications)


@ygk_api_bp.route("/intibak-table", methods=["GET"])
@role_required("ygk")
def intibak_table():
    """View Intibak table."""
    return jsonify(
        {
            "tab": "Intibak Table",
            "view_mode": "placeholder",
            "edit_mode": "placeholder",
            "status": "Phase 1 shell",
        }
    )


@ygk_api_bp.route("/approve/<int:application_id>", methods=["POST"])
@role_required("ygk")
def approve_application(application_id):
    """Approve application."""
    service = _get_service()
    
    result = service.update_applicant_status(application_id, "approved")
    
    if result.success:
        flash("Application approved successfully.", "success")
        return redirect(url_for("ygk_api.check_applicants"))
    else:
        flash(result.error_msg, "error")
        return redirect(url_for("ygk_api.check_applicants"))
