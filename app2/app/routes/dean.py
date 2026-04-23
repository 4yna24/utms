"""Dean API shell routes."""

from __future__ import annotations

from flask import Blueprint, jsonify

from .common import role_required

dean_api_bp = Blueprint("dean_api", __name__, url_prefix="/api/dean")


@dean_api_bp.route("/check-applicants", methods=["GET"])
@role_required("dean")
def check_applicants():
    return jsonify(
        {
            "tab": "Check Applicants",
            "manual_forward_button": "placeholder",
            "auto_forward_button": "placeholder",
            "status": "Phase 1 shell",
        }
    )
