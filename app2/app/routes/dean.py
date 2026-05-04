"""Dean API shell routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template

from .common import role_required

from .. import db
from ..models import Application

dean_api_bp = Blueprint("dean_api", __name__, url_prefix="/api/dean")


@dean_api_bp.route("/check-applicants", methods=["GET"])
@role_required("dean")
def check_applicants():
    applications = Application.query.filter_by(status="forwarded_to_dean").all()
    return render_template("dean_check_applicants.html", applications=applications)


@dean_api_bp.route("/forward-to-ygk/<int:application_id>", methods=["POST"])
@role_required("dean")
def forward_to_ygk(application_id):
    application = Application.query.get(application_id)
    if not application or application.status != "forwarded_to_dean":
        return jsonify({"error": "Invalid application"}), 400
    application.status = "forwarded_to_ygk"
    db.session.commit()
    return jsonify({"message": "Application forwarded to YGK"})
