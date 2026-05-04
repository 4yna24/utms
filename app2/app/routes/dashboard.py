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


@dashboard_bp.route("/", methods=["GET"])
@login_required
def index():
    """Render dashboard tabs based on authenticated user role."""
    role_slug = session.get("user_role")
    role_name = next((item["name"] for item in ROLE_DEFINITIONS if item["slug"] == role_slug), role_slug)
    applicant_application = None
    oidb_applications = []

    if role_slug == "applicant":
        applicant_application = Application.query.options(selectinload(Application.documents)).filter_by(
            applicant_id=session.get("user_id")
        ).first()

    if role_slug == "oidb":
        oidb_applications = (
            Application.query.options(
                selectinload(Application.documents),
                selectinload(Application.applicant),
            )
            .order_by(Application.created_at.desc())
            .all()
        )

    return render_template(
        "dashboard.html",
        email=session.get("user_email"),
        role_name=role_name,
        role_slug=role_slug,
        tabs=PHASE1_TABS.get(role_slug, []),
        applicant_application=applicant_application,
        oidb_applications=oidb_applications,
        available_programs=AVAILABLE_PROGRAMS,
        available_semesters=AVAILABLE_SEMESTERS,
        document_slots=APPLICATION_DOCUMENT_SLOTS,
        cancellation_allowed=APPLICATION_CANCELLATION_ALLOWED,
        resubmission_allowed=APPLICATION_RESUBMISSION_ALLOWED,
        tracker_steps=APPLICATION_TRACKER_STEPS,
        status_step=APPLICATION_STATUS_STEP,
    )
