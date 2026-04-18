from flask import render_template, session, redirect, url_for
from flask.views import MethodView

class DashboardView(MethodView):
    def get(self):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        # Get the email we stored in the session earlier
        user_email = session.get('user_email')
        return render_template('dashboard.html', email=user_email)