"""OIDB API shell routes."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template
from sqlalchemy.orm import selectinload

from .. import db
from ..models import Application
from .common import role_required

oidb_api_bp = Blueprint("oidb_api", __name__, url_prefix="/api/oidb")


@oidb_api_bp.route("/check-documents", methods=["GET"])
@role_required("oidb")
def check_documents():
    applications = (
        Application.query.options(
            selectinload(Application.documents),
            selectinload(Application.applicant),
        )
        .order_by(Application.created_at.desc())
        .all()
    )
    return render_template("oidb_check_documents.html", applications=applications)


@oidb_api_bp.route("/create-waitlist-table", methods=["GET"])
@role_required("oidb")
def create_waitlist_table():
    return jsonify({"tab": "Create Waitlist Table", "status": "Phase 1 shell"})


@oidb_api_bp.route("/forward-to-ydyo/<int:application_id>", methods=["POST"])
@role_required("oidb")
def forward_to_ydyo(application_id):
    application = Application.query.get(application_id)
    if not application or application.status != "submitted":
        return jsonify({"error": "Invalid application"}), 400
    application.status = "forwarded_to_ydyo"
    db.session.commit()
    return jsonify({"message": "Application forwarded to YDYO"})
