"""YGK API shell routes."""

from __future__ import annotations

from flask import Blueprint, jsonify

from .common import role_required

ygk_api_bp = Blueprint("ygk_api", __name__, url_prefix="/api/ygk")


@ygk_api_bp.route("/check-applicants", methods=["GET"])
@role_required("ygk")
def check_applicants():
    return jsonify({"tab": "Check Applicants", "status": "Phase 1 shell"})


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
