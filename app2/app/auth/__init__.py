from flask import Blueprint
from .views import RegisterView, LoginView, LogoutView


def create_auth_blueprint(role_name, role_slug):
    auth_bp = Blueprint(f'{role_slug}_auth', __name__)

    auth_bp.add_url_rule(
        '/register',
        view_func=RegisterView.as_view('register', role_name=role_name, role_slug=role_slug),
    )
    auth_bp.add_url_rule(
        '/login',
        view_func=LoginView.as_view('login', role_name=role_name, role_slug=role_slug),
    )
    auth_bp.add_url_rule(
        '/logout',
        view_func=LogoutView.as_view('logout', role_name=role_name, role_slug=role_slug),
    )

    return auth_bp