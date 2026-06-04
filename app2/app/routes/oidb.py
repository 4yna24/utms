"""OIDB routes — thin HTTP layer."""

from __future__ import annotations

from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, session, url_for

from ..classes import Oidb
from .common import role_required

oidb_api_bp = Blueprint("oidb_api", __name__, url_prefix="/api/oidb")


def _get_service() -> Oidb:
    """Get Oidb instance for current user."""
    return Oidb(
        user_id=session.get("user_id", 0),
        email=session.get("user_email", ""),
        role="oidb"
    )


@oidb_api_bp.route("/check-documents", methods=["GET"])
@role_required("oidb")
def check_documents():
    """Show pending documents."""
    service = _get_service()
    return render_template("oidb_check_documents.html", applications=service.get_pending_applicants())


@oidb_api_bp.route("/create-waitlist-table", methods=["GET"])
@role_required("oidb")
def create_waitlist_table():
    """Placeholder for waitlist table creation."""
    from flask import jsonify
    return jsonify({"tab": "Create Waitlist Table", "status": "Phase 1 shell"})


@oidb_api_bp.route("/forward-to-ydyo/<int:application_id>", methods=["POST"])
@role_required("oidb")
def forward_to_ydyo(application_id):
    """Forward document to YDYO."""
    service = _get_service()
    
    result = service.forward_to_ydyo(application_id)
    
    if result.success:
        flash("Application forwarded to YDYO successfully.", "success")
    else:
        flash(result.error_msg, "error")
    
    return redirect(url_for("dashboard.index", tab="check-documents"))


@oidb_api_bp.route("/forward-all-to-ydyo", methods=["POST"])
@role_required("oidb")
def forward_all_to_ydyo():
    """Forward all documents to YDYO (no document checking)."""
    service = _get_service()
    result = service.forward_all_to_ydyo()
    if result.success:
        flash("All applications forwarded to YDYO successfully.", "success")
    else:
        flash(result.error_msg, "error")
    return redirect(url_for("dashboard.index", tab="check-documents"))


@oidb_api_bp.route("/run-doc-checker", methods=["POST"])
@role_required("oidb")
def run_doc_checker():
    """Run document checker on all submitted applications. Does not forward."""
    service = _get_service()
    result = service.run_doc_checker_all()
    if result.success:
        data = result.data or {}
        passed = data.get("passed", 0)
        flagged = data.get("flagged", 0)
        flash(
            f"Document check complete: {passed} passed, {flagged} have errors.",
            "success" if flagged == 0 else "warning",
        )
    else:
        flash(result.error_msg, "error")
    return redirect(url_for("dashboard.index", tab="check-documents"))


@oidb_api_bp.route("/auto-forward-checked", methods=["POST"])
@role_required("oidb")
def auto_forward_checked():
    """Forward all submitted applications where doc checker already passed."""
    service = _get_service()
    result = service.auto_forward_checked()
    if result.success:
        data = result.data or {}
        forwarded = data.get("forwarded", 0)
        skipped = data.get("skipped", 0)
        flash(
            f"Auto-forward complete: {forwarded} forwarded to YDYO, "
            f"{skipped} skipped (not checked or have errors).",
            "success" if skipped == 0 else "warning",
        )
    else:
        flash(result.error_msg, "error")
    return redirect(url_for("dashboard.index", tab="check-documents"))


@oidb_api_bp.route("/auto-check-and-forward", methods=["POST"])
@role_required("oidb")
def auto_check_and_forward():
    """Run document checker on all submitted applications and forward those that pass."""
    service = _get_service()
    result = service.auto_check_and_forward_all()
    if result.success:
        data = result.data or {}
        forwarded = data.get("forwarded", 0)
        flagged = data.get("flagged", 0)
        flash(
            f"Auto-check complete: {forwarded} forwarded to YDYO, "
            f"{flagged} flagged with errors (require manual review).",
            "success" if flagged == 0 else "warning",
        )
    else:
        flash(result.error_msg, "error")
    return redirect(url_for("dashboard.index", tab="check-documents"))


@oidb_api_bp.route("/return-application/<int:application_id>", methods=["POST"])
@role_required("oidb")
def return_application(application_id):
    """Return application for corrections."""
    notes = (request.form.get("oidb_notes") or "").strip()
    service = _get_service()
    
    result = service.return_application(application_id, notes)
    
    if result.success:
        flash("Application returned successfully.", "success")
    else:
        flash(result.error_msg, "error")
    
    return redirect(url_for("dashboard.index", tab="check-documents"))


@oidb_api_bp.route("/cancel-forward-to-ydyo/<int:application_id>", methods=["POST"])
@role_required("oidb")
def cancel_forward_to_ydyo(application_id):
    """Cancel the forward-to-YDYO decision, reverting the application to submitted."""
    service = _get_service()
    result = service.cancel_forward_to_ydyo(application_id)
    if result.success:
        flash("Forward to YDYO cancelled. Application reverted to submitted status.", "success")
    else:
        flash(result.error_msg, "error")
    return redirect(url_for("dashboard.index", tab="check-documents"))


@oidb_api_bp.route("/view-document/<int:doc_id>", methods=["GET"])
@role_required("oidb")
def view_document(doc_id):
    """View application document."""
    service = _get_service()
    
    result = service.get_document(doc_id)
    if not result.success or not result.data:
        abort(404)
    
    doc = result.data
    return send_file(doc.file_path, mimetype="application/pdf", as_attachment=False)
