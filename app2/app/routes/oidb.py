"""OIDB API shell routes."""

from __future__ import annotations

from flask import Blueprint, jsonify

from .common import role_required

oidb_api_bp = Blueprint("oidb_api", __name__, url_prefix="/api/oidb")


@oidb_api_bp.route("/check-documents", methods=["GET"])
@role_required("oidb")
def check_documents():
    return jsonify({"tab": "Check Documents", "status": "Phase 1 shell"})


@oidb_api_bp.route("/create-waitlist-table", methods=["GET"])
@role_required("oidb")
def create_waitlist_table():
    return jsonify({"tab": "Create Waitlist Table", "status": "Phase 1 shell"})
