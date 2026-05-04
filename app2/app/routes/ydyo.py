"""YDYO API shell routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template

from .common import role_required

from .. import db
from ..models import Application

ydyo_api_bp = Blueprint("ydyo_api", __name__, url_prefix="/api/ydyo")


@ydyo_api_bp.route("/retrieve-applicants", methods=["GET"])
@role_required("ydyo")
def retrieve_applicants():
    applications = Application.query.filter_by(status="forwarded_to_ydyo").all()
    return render_template("ydyo_retrieve_applicants.html", applications=applications)


@ydyo_api_bp.route("/set-prep-school-status", methods=["GET"])
@role_required("ydyo")
def set_prep_school_status():
    return jsonify({"tab": "Set Prep School Status", "status": "Phase 1 shell"})


@ydyo_api_bp.route("/check-applicants", methods=["GET"])
@role_required("ydyo")
def check_applicants():
    applications = Application.query.filter_by(status="forwarded_to_ydyo").all()
    return render_template("ydyo_check_applicants.html", applications=applications)


@ydyo_api_bp.route("/forward-to-dean/<int:application_id>", methods=["POST"])
@role_required("ydyo")
def forward_to_dean(application_id):
    application = Application.query.get(application_id)
    if not application or application.status != "forwarded_to_ydyo":
        return jsonify({"error": "Invalid application"}), 400
    application.status = "forwarded_to_dean"
    db.session.commit()
    return jsonify({"message": "Application forwarded to Dean"})
