"""Role-aware dashboard blueprint."""

from __future__ import annotations

import math
import re

from flask import Blueprint, render_template, request, session
from sqlalchemy.orm import selectinload

from ..config import (
    APPLICATION_CANCELLATION_ALLOWED,
    APPLICATION_DOCUMENT_SLOTS,
    APPLICATION_RESUBMISSION_ALLOWED,
    APPLICATION_STATUS_STEP,
    APPLICATION_SUBMISSION_PERIOD_OPEN,
    APPLICATION_TRACKER_STEPS,
    AVAILABLE_FACULTIES,
    AVAILABLE_PROGRAMS,
    AVAILABLE_SEMESTERS,
    PHASE1_TABS,
    ROLE_DEFINITIONS,
)
from ..models import ApplicationORM
from .common import login_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

_PER_PAGE = 10


def _slugify(title: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')


def _build_pagination(total: int, page: int, per_page: int) -> dict:
    total_pages = max(1, math.ceil(total / per_page))
    page = max(1, min(page, total_pages))
    return {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "has_prev": page > 1,
        "has_next": page < total_pages,
    }


def _status_counts(apps: list, statuses: list[str]) -> dict:
    counts = {"total": len(apps)}
    for s in statuses:
        counts[s] = sum(1 for a in apps if a.status == s)
    return counts


def _get_tab_data(role_slug: str, tab_slug: str, page: int, user_id: int, email: str) -> dict:
    """Return template context for one tab, with pagination where applicable."""
    per_page = _PER_PAGE
    offset = (page - 1) * per_page

    if role_slug == "oidb" and tab_slug == "check-documents":
        from ..classes import Oidb
        apps = Oidb(user_id, email, "oidb").get_pending_applicants()
        return {
            "oidb_applications": apps[offset:offset + per_page],
            "document_slots": APPLICATION_DOCUMENT_SLOTS,
            "pagination": _build_pagination(len(apps), page, per_page),
            "status_counts": _status_counts(apps, ["submitted", "forwarded_to_ydyo", "returned"]),
        }

    if role_slug == "dean" and tab_slug == "receive-forward-applications":
        from ..classes import DeanOffice
        apps = DeanOffice(user_id, email, "dean").get_pending_applicants()
        return {
            "dean_applications": apps[offset:offset + per_page],
            "available_faculties": AVAILABLE_FACULTIES,
            "pagination": _build_pagination(len(apps), page, per_page),
            "status_counts": _status_counts(apps, ["forwarded_to_dean", "forwarded_to_ygk"]),
        }

    if role_slug == "ydyo" and tab_slug == "set-prep-school-status":
        from ..classes import Ydyo
        apps = Ydyo(user_id, email, "ydyo").get_applications()
        return {
            "ydyo_applications": apps[offset:offset + per_page],
            "pagination": _build_pagination(len(apps), page, per_page),
            "status_counts": _status_counts(apps, ["forwarded_to_ydyo"]),
        }

    if role_slug == "applicant" and tab_slug == "track-application":
        app = (
            ApplicationORM.query
            .options(selectinload(ApplicationORM.documents))
            .filter_by(applicant_id=user_id)
            .first()
        )
        return {
            "applicant_application": app,
            "tracker_steps": APPLICATION_TRACKER_STEPS,
            "status_step": APPLICATION_STATUS_STEP,
            "cancellation_allowed": APPLICATION_CANCELLATION_ALLOWED,
            "resubmission_allowed": APPLICATION_RESUBMISSION_ALLOWED,
        }

    if role_slug == "applicant" and tab_slug == "submit-application":
        app = (
            ApplicationORM.query
            .options(selectinload(ApplicationORM.documents))
            .filter_by(applicant_id=user_id)
            .first()
        )
        return {
            "applicant_application": app,
            "period_open": APPLICATION_SUBMISSION_PERIOD_OPEN,
            "available_programs": AVAILABLE_PROGRAMS,
            "available_semesters": AVAILABLE_SEMESTERS,
            "document_slots": APPLICATION_DOCUMENT_SLOTS,
            "resubmission_allowed": APPLICATION_RESUBMISSION_ALLOWED,
        }

    if role_slug == "admin":
        from ..classes import Admin
        admin = Admin(user_id, email, "admin")
        if tab_slug == "user-management":
            return {"admin_users": admin.list_users().data or []}
        if tab_slug == "config":
            return {"admin_config": admin.get_config_summary()}
        if tab_slug == "database":
            return {
                "admin_applications": admin.get_all_applications().data or [],
                "admin_backups": admin.list_backups().data or [],
            }

    return {}


def _enrich_tabs(tabs: list) -> list:
    return [{**t, "slug": _slugify(t["title"])} for t in tabs]


@dashboard_bp.route("/", methods=["GET"])
@login_required
def index():
    role_slug = session.get("user_role")
    email = session.get("user_email")
    _ROLE_DISPLAY = {**{r["slug"]: r["name"] for r in ROLE_DEFINITIONS}, "admin": "Administrator"}
    role_name = _ROLE_DISPLAY.get(role_slug, role_slug)

    return render_template(
        "dashboard.html",
        email=email,
        role_name=role_name,
        role_slug=role_slug,
        tabs=_enrich_tabs(PHASE1_TABS.get(role_slug, [])),
        # Static config kept available for any inline use
        available_programs=AVAILABLE_PROGRAMS,
        available_semesters=AVAILABLE_SEMESTERS,
        available_faculties=AVAILABLE_FACULTIES,
        document_slots=APPLICATION_DOCUMENT_SLOTS,
        cancellation_allowed=APPLICATION_CANCELLATION_ALLOWED,
        resubmission_allowed=APPLICATION_RESUBMISSION_ALLOWED,
        tracker_steps=APPLICATION_TRACKER_STEPS,
        status_step=APPLICATION_STATUS_STEP,
    )


@dashboard_bp.route("/tab/<tab_slug>", methods=["GET"])
@login_required
def tab_content(tab_slug: str):
    """Render a single tab panel as an HTML fragment (lazy-load target)."""
    role_slug = session.get("user_role")
    user_id = session.get("user_id")
    email = session.get("user_email")
    page = max(1, request.args.get("page", 1, type=int))

    tabs = _enrich_tabs(PHASE1_TABS.get(role_slug, []))
    tab = next((t for t in tabs if t["slug"] == tab_slug), None)
    if not tab:
        return "<p class='subline'>Tab not found.</p>", 404
    if not tab.get("partial"):
        return "<p class='subline'>This section will be available in a future phase.</p>"

    data = _get_tab_data(role_slug, tab_slug, page, user_id, email)
    return render_template(tab["partial"], **data)
