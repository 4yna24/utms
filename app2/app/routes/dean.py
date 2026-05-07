"""Dean routes — thin HTTP layer over DeanOffice class."""

from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, session, url_for

from ..classes import DeanOffice
from .common import role_required

dean_api_bp = Blueprint("dean_api", __name__, url_prefix="/api/dean")


def _svc() -> DeanOffice:
    return DeanOffice(session["user_id"], session["user_email"], "dean")


@dean_api_bp.route("/check-applicants", methods=["GET"])
@role_required("dean")
def check_applicants():
    return render_template("dean_check_applicants.html", applications=_svc().get_pending_applicants())


@dean_api_bp.route("/forward-to-ygk/<int:application_id>", methods=["POST"])
@role_required("dean")
def forward_to_ygk(application_id):
    ok, msg = _svc().forward_to_ygk(application_id)
    flash(msg, "success" if ok else "error")
    return redirect(url_for("dean_api.check_applicants"))


@dean_api_bp.route("/forward-all-to-ygk", methods=["POST"])
@role_required("dean")
def forward_all_to_ygk():
    count = _svc().forward_all_to_ygk()
    flash(f"Forwarded {count} application(s) to YGK.", "success")
    return redirect(url_for("dean_api.check_applicants"))
