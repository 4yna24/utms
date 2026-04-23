"""Role-aware dashboard blueprint."""

from __future__ import annotations

from flask import Blueprint, render_template, session

from ..config import PHASE1_TABS, ROLE_DEFINITIONS

from .common import login_required

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")


@dashboard_bp.route("/", methods=["GET"])
@login_required
def index():
    """Render dashboard tabs based on authenticated user role."""
    role_slug = session.get("user_role")
    role_name = next((item["name"] for item in ROLE_DEFINITIONS if item["slug"] == role_slug), role_slug)

    return render_template(
        "dashboard.html",
        email=session.get("user_email"),
        role_name=role_name,
        role_slug=role_slug,
        tabs=PHASE1_TABS.get(role_slug, []),
    )
