"""OIDB routes — thin HTTP layer over Oidb class."""

from __future__ import annotations

from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, session, url_for

from ..classes import Oidb
from .common import role_required

oidb_api_bp = Blueprint("oidb_api", __name__, url_prefix="/api/oidb")


def _svc() -> Oidb:
    return Oidb(session["user_id"], session["user_email"], "oidb")


@oidb_api_bp.route("/check-documents", methods=["GET"])
@role_required("oidb")
def check_documents():
    return render_template("oidb_check_documents.html", applications=_svc().get_pending_applicants())


@oidb_api_bp.route("/create-waitlist-table", methods=["GET"])
@role_required("oidb")
def create_waitlist_table():
    from flask import jsonify
    return jsonify({"tab": "Create Waitlist Table", "status": "Phase 1 shell"})


@oidb_api_bp.route("/forward-to-ydyo/<int:application_id>", methods=["POST"])
@role_required("oidb")
def forward_to_ydyo(application_id):
    ok, msg = _svc().forward_to_ydyo(application_id)
    flash(msg, "success" if ok else "error")
    return redirect(url_for("oidb_api.check_documents"))


@oidb_api_bp.route("/forward-all-to-ydyo", methods=["POST"])
@role_required("oidb")
def forward_all_to_ydyo():
    count = _svc().forward_all_to_ydyo()
    flash(f"Forwarded {count} application(s) to YDYO.", "success")
    return redirect(url_for("oidb_api.check_documents"))


@oidb_api_bp.route("/return-application/<int:application_id>", methods=["POST"])
@role_required("oidb")
def return_application(application_id):
    notes = (request.form.get("oidb_notes") or "").strip()
    ok, msg = _svc().return_application(application_id, notes)
    flash(msg, "success" if ok else "error")
    return redirect(url_for("oidb_api.check_documents"))


@oidb_api_bp.route("/view-document/<int:doc_id>", methods=["GET"])
@role_required("oidb")
def view_document(doc_id):
    doc = _svc().get_document(doc_id)
    if not doc:
        abort(404)
    return send_file(doc.file_path, mimetype="application/pdf", as_attachment=False)
