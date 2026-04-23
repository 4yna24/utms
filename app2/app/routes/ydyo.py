"""YDYO API shell routes."""

from __future__ import annotations

from flask import Blueprint, jsonify

from .common import role_required

ydyo_api_bp = Blueprint("ydyo_api", __name__, url_prefix="/api/ydyo")


@ydyo_api_bp.route("/retrieve-applicants", methods=["GET"])
@role_required("ydyo")
def retrieve_applicants():
    return jsonify({"tab": "Retrieve Applicants", "status": "Phase 1 shell"})


@ydyo_api_bp.route("/set-prep-school-status", methods=["GET"])
@role_required("ydyo")
def set_prep_school_status():
    return jsonify({"tab": "Set Prep School Status", "status": "Phase 1 shell"})
