"""YGK API shell routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template

from .common import role_required

from .. import db
from ..models import Application

ygk_api_bp = Blueprint("ygk_api", __name__, url_prefix="/api/ygk")


@ygk_api_bp.route("/check-applicants", methods=["GET"])
@role_required("ygk")
def check_applicants():
    applications = Application.query.filter_by(status="forwarded_to_ygk").all()
    return render_template("ygk_check_applicants.html", applications=applications)


@ygk_api_bp.route("/intibak-table", methods=["GET"])
@role_required("ygk")
def intibak_table():
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
    application = Application.query.get(application_id)
    if not application or application.status != "forwarded_to_ygk":
        return jsonify({"error": "Invalid application"}), 400
    application.status = "approved"
    db.session.commit()
    return jsonify({"message": "Application approved"})
