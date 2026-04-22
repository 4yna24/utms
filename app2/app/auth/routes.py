from flask import render_template, request, redirect, url_for, session, flash
from flask.views import MethodView
from app.models import User
from app import db


class RoleView(MethodView):
    def __init__(self, role_name, role_slug):
        self.role_name = role_name
        self.role_slug = role_slug
        self.auth_blueprint = f'{role_slug}_auth'
        self.dashboard_blueprint = f'{role_slug}_dashboard'

    def auth_endpoint(self, endpoint_name):
        return f'{self.auth_blueprint}.{endpoint_name}'

    def dashboard_endpoint(self, endpoint_name='index'):
        return f'{self.dashboard_blueprint}.{endpoint_name}'

    def template_context(self):
        return {
            'role_name': self.role_name,
            'role_slug': self.role_slug,
            'login_endpoint': self.auth_endpoint('login'),
            'register_endpoint': self.auth_endpoint('register'),
            'logout_endpoint': self.auth_endpoint('logout'),
            'dashboard_endpoint': self.dashboard_endpoint('index'),
        }


class RegisterView(RoleView):
    def get(self):
        return render_template('register.html', **self.template_context())

    def post(self):
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email, role=self.role_slug).first():
            flash(f"Email already exists for {self.role_name}")
            return redirect(url_for(self.auth_endpoint('register')))

        user = User(email=email, role=self.role_slug)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for(self.auth_endpoint('login')))


class LoginView(RoleView):
    def get(self):
        return render_template('login.html', **self.template_context())

    def post(self):
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email, role=self.role_slug).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['user_role'] = self.role_slug
            return redirect(url_for(self.dashboard_endpoint('index')))
        
        flash(f"Invalid email or password for {self.role_name}")
        return redirect(url_for(self.auth_endpoint('login')))


class LogoutView(RoleView):
    def get(self):
        session.clear()
        return redirect(url_for(self.auth_endpoint('login')))