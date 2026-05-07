"""Role-aware dashboard blueprint."""

from __future__ import annotations

from flask import Blueprint, render_template, session
from sqlalchemy.orm import selectinload

from ..config import (
    APPLICATION_CANCELLATION_ALLOWED,
    APPLICATION_DOCUMENT_SLOTS,
    APPLICATION_RESUBMISSION_ALLOWED,
    APPLICATION_STATUS_STEP,
    APPLICATION_TRACKER_STEPS,
    AVAILABLE_PROGRAMS,
    AVAILABLE_SEMESTERS,
    PHASE1_TABS,
    ROLE_DEFINITIONS,
)
from ..models import Application
from .common import login_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


def _get_role_data(role_slug: str, user_id: int, email: str) -> dict:
    if role_slug == "applicant":
        app = (
            Application.query
            .options(selectinload(Application.documents))
            .filter_by(applicant_id=user_id)
            .first()
        )
        return {"applicant_application": app}

    if role_slug == "oidb":
        from ..classes import Oidb
        return {"oidb_applications": Oidb(user_id, email, "oidb").get_pending_applicants()}

    if role_slug == "dean":
        from ..classes import DeanOffice
        return {"dean_applications": DeanOffice(user_id, email, "dean").get_pending_applicants()}

    return {}


@dashboard_bp.route("/", methods=["GET"])
@login_required
def index():
    role_slug = session.get("user_role")
    user_id = session.get("user_id")
    email = session.get("user_email")
    role_name = next((r["name"] for r in ROLE_DEFINITIONS if r["slug"] == role_slug), role_slug)

    return render_template(
        "dashboard.html",
        email=email,
        role_name=role_name,
        role_slug=role_slug,
        tabs=PHASE1_TABS.get(role_slug, []),
        available_programs=AVAILABLE_PROGRAMS,
        available_semesters=AVAILABLE_SEMESTERS,
        document_slots=APPLICATION_DOCUMENT_SLOTS,
        cancellation_allowed=APPLICATION_CANCELLATION_ALLOWED,
        resubmission_allowed=APPLICATION_RESUBMISSION_ALLOWED,
        tracker_steps=APPLICATION_TRACKER_STEPS,
        status_step=APPLICATION_STATUS_STEP,
        **_get_role_data(role_slug, user_id, email),
    )
