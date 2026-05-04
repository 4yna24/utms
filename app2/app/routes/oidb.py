"""OIDB API shell routes."""

from __future__ import annotations

from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for
from sqlalchemy.orm import selectinload

from .. import db
from ..models import Application, ApplicationDocument
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
    from flask import jsonify
    return jsonify({"tab": "Create Waitlist Table", "status": "Phase 1 shell"})


@oidb_api_bp.route("/forward-to-ydyo/<int:application_id>", methods=["POST"])
@role_required("oidb")
def forward_to_ydyo(application_id):
    application = Application.query.get(application_id)
    if not application or application.status not in ("submitted", "returned"):
        flash("Cannot forward this application.")
        return redirect(url_for("oidb_api.check_documents"))
    application.status = "forwarded_to_ydyo"
    db.session.commit()
    flash(f"Application #{application_id} forwarded to YDYO.", "success")
    return redirect(url_for("oidb_api.check_documents"))


@oidb_api_bp.route("/forward-all-to-ydyo", methods=["POST"])
@role_required("oidb")
def forward_all_to_ydyo():
    apps = Application.query.filter_by(status="submitted").all()
    count = len(apps)
    for app in apps:
        app.status = "forwarded_to_ydyo"
    db.session.commit()
    flash(f"Forwarded {count} application(s) to YDYO.", "success")
    return redirect(url_for("oidb_api.check_documents"))


@oidb_api_bp.route("/return-application/<int:application_id>", methods=["POST"])
@role_required("oidb")
def return_application(application_id):
    application = Application.query.get(application_id)
    if not application or application.status not in ("submitted",):
        flash("Cannot return this application.")
        return redirect(url_for("oidb_api.check_documents"))
    notes = (request.form.get("oidb_notes") or "").strip()
    if not notes:
        flash("A reason is required when returning an application.")
        return redirect(url_for("oidb_api.check_documents"))
    application.status = "returned"
    application.oidb_notes = notes
    db.session.commit()
    flash(f"Application #{application_id} returned to applicant.", "success")
    return redirect(url_for("oidb_api.check_documents"))


@oidb_api_bp.route("/view-document/<int:doc_id>", methods=["GET"])
@role_required("oidb")
def view_document(doc_id):
    doc = ApplicationDocument.query.get(doc_id)
    if not doc:
        abort(404)
    return send_file(doc.file_path, mimetype="application/pdf", as_attachment=False)
