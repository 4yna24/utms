from flask import Blueprint
from .views import DashboardView


def create_dashboard_blueprint(role_name, role_slug):
    dash_bp = Blueprint(f'{role_slug}_dashboard', __name__)
    dash_bp.add_url_rule(
        '/',
        view_func=DashboardView.as_view('index', role_name=role_name, role_slug=role_slug),
    )
    return dash_bp