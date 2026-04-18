from flask import render_template, request, redirect, url_for, session, flash
from flask.views import MethodView
from app.models import User
from app import db

class RegisterView(MethodView):
    def get(self):
        return render_template('register.html')

    def post(self):
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(email=email).first():
            flash("Email already exists")
            return redirect(url_for('auth.register'))

        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))

class LoginView(MethodView):
    def get(self):
        return render_template('login.html')

    def post(self):
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            # CREATE THE SESSION
            session['user_id'] = user.id
            session['user_email'] = user.email
            return redirect(url_for('dashboard.index'))
        
        flash("Invalid email or password")
        return redirect(url_for('auth.login'))

# Logic to logout
class LogoutView(MethodView):
    def get(self):
        session.clear()
        return redirect(url_for('auth.login'))