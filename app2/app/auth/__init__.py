from flask import Blueprint
auth_bp = Blueprint('auth', __name__)
from . import routes
# Then add your rules here
from .routes import RegisterView, LoginView, LogoutView
auth_bp.add_url_rule('/register', view_func=RegisterView.as_view('register'))
auth_bp.add_url_rule('/login', view_func=LoginView.as_view('login'))
auth_bp.add_url_rule('/logout', view_func=LogoutView.as_view('logout'))