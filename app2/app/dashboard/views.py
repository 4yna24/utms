from flask import render_template, session, redirect, url_for
from flask.views import MethodView


class DashboardView(MethodView):
    def __init__(self, role_name, role_slug):
        self.role_name = role_name
        self.role_slug = role_slug
        self.auth_blueprint = f'{role_slug}_auth'
        self.dashboard_blueprint = f'{role_slug}_dashboard'

    def auth_endpoint(self, endpoint_name):
        return f'{self.auth_blueprint}.{endpoint_name}'

    def dashboard_endpoint(self, endpoint_name='index'):
        return f'{self.dashboard_blueprint}.{endpoint_name}'

    def get(self):
        if 'user_id' not in session or session.get('user_role') != self.role_slug:
            return redirect(url_for(self.auth_endpoint('login')))

        user_email = session.get('user_email')
        return render_template(
            'dashboard.html',
            email=user_email,
            role_name=self.role_name,
            role_slug=self.role_slug,
            login_endpoint=self.auth_endpoint('login'),
            register_endpoint=self.auth_endpoint('register'),
            logout_endpoint=self.auth_endpoint('logout'),
            dashboard_endpoint=self.dashboard_endpoint('index'),
        )
