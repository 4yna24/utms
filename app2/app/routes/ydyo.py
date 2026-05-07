"""YDYO routes — thin HTTP layer over Ydyo class."""

from __future__ import annotations

from flask import Blueprint, abort, flash, redirect, render_template, request, session, send_file, url_for

from ..classes.users import Ydyo
from .common import role_required

ydyo_api_bp = Blueprint("ydyo_api", __name__, url_prefix="/api/ydyo")


def _svc() -> Ydyo:
    return Ydyo(session["user_id"], session["user_email"], "ydyo")


@ydyo_api_bp.route("/check-documents", methods=["GET"])
@role_required("ydyo")
def check_documents():
    return render_template("ydyo_check_documents.html", applications=_svc().get_applications())


@ydyo_api_bp.route("/mark-and-forward/<int:application_id>", methods=["POST"])
@role_required("ydyo")
def mark_and_forward(application_id):
    prep_status = (request.form.get("prep_status") or "").strip()
    ok, msg = _svc().mark_and_forward(application_id, prep_status)
    flash(msg, "success" if ok else "error")
    return redirect(url_for("ydyo_api.check_documents"))


@ydyo_api_bp.route("/forward-all-to-dean", methods=["POST"])
@role_required("ydyo")
def forward_all_to_dean():
    ok, msg = _svc().forward_all_to_dean()
    flash(msg, "success" if ok else "error")
    return redirect(url_for("ydyo_api.check_documents"))


@ydyo_api_bp.route("/view-document/<int:doc_id>", methods=["GET"])
@role_required("ydyo")
def view_document(doc_id):
    doc = _svc().get_document(doc_id)
    if not doc:
        abort(404)
    return send_file(doc.file_path, mimetype="application/pdf", as_attachment=False)
