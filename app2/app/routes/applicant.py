"""Applicant API shell routes."""

from __future__ import annotations

from flask import Blueprint, jsonify

from .common import role_required

applicant_api_bp = Blueprint("applicant_api", __name__, url_prefix="/api/applicant")


@applicant_api_bp.route("/track-application", methods=["GET"])
@role_required("applicant")
def track_application():
    return jsonify({"tab": "Track Application", "status": "Phase 1 shell"})


@applicant_api_bp.route("/submit-documents", methods=["GET"])
@role_required("applicant")
def submit_documents():
    return jsonify({"tab": "Submit Documents", "status": "Phase 1 shell"})
