from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

db = SQLAlchemy()

ROLE_PORTALS = [
    {'name': 'Applicant', 'slug': 'applicant'},
    {'name': 'OIDB', 'slug': 'oidb'},
    {'name': 'Dean', 'slug': 'dean'},
    {'name': 'YGK', 'slug': 'ygk'},
    {'name': 'YDYO', 'slug': 'ydyo'},
]


def _ensure_user_role_column():
    # Keep old SQLite files compatible with the new role-based user model.
    with db.engine.begin() as conn:
        table_exists = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        ).fetchone()

        if not table_exists:
            return

        columns = conn.execute(text('PRAGMA table_info("user")')).fetchall()
        column_names = {col[1] for col in columns}

        if 'role' not in column_names:
            conn.execute(
                text('ALTER TABLE "user" ADD COLUMN role VARCHAR(32) NOT NULL DEFAULT "applicant"')
            )

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'dev-key-123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///project.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    from app.database import init_database_interfaces
    init_database_interfaces(app)

    from app.auth import create_auth_blueprint
    from app.dashboard import create_dashboard_blueprint

    @app.route('/')
    def home():
        return render_template('index.html', roles=ROLE_PORTALS)

    for role in ROLE_PORTALS:
        auth_bp = create_auth_blueprint(role['name'], role['slug'])
        dash_bp = create_dashboard_blueprint(role['name'], role['slug'])

        app.register_blueprint(auth_bp, url_prefix=f"/{role['slug']}/auth")
        app.register_blueprint(dash_bp, url_prefix=f"/{role['slug']}/dashboard")

        def role_entry(role_slug=role['slug']):
            # Central role entry: dashboard will redirect to login if session is invalid.
            return redirect(url_for(f'{role_slug}_dashboard.index'))

        app.add_url_rule(f"/{role['slug']}/", endpoint=f"{role['slug']}_entry", view_func=role_entry)

    with app.app_context():
        db.create_all()
        _ensure_user_role_column()

    return app