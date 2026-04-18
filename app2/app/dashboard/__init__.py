from flask import Blueprint
from flask import Blueprint
from .routes import DashboardView  # Assuming you named the class in routes.py or views.py

# 1. Define the Blueprint
# 'dashboard' is the name of the blueprint (used for url_for)
# __name__ helps Flask locate the templates folder relative to this file
dash_bp = Blueprint('dashboard', __name__)

# 2. Register the Class-based view
# We map the '/' of this blueprint to the DashboardView class
dash_bp.add_url_rule('/', view_func=DashboardView.as_view('index'))