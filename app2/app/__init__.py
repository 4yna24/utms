from pathlib import Path

from flask import Flask, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

from .config import APPLICATION_UPLOAD_SUBDIR, ROLE_DEFINITIONS

db = SQLAlchemy()


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


def _ensure_application_new_columns():
    with db.engine.begin() as conn:
        table_exists = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='application'")
        ).fetchone()
        if not table_exists:
            return

        columns = conn.execute(text('PRAGMA table_info("application")')).fetchall()
        column_names = {col[1] for col in columns}

        additions = {
            "id_number": 'VARCHAR(64) NOT NULL DEFAULT ""',
            "target_program": 'VARCHAR(120) NOT NULL DEFAULT ""',
            "target_semester": 'VARCHAR(32) NOT NULL DEFAULT ""',
            "is_currently_enrolled": "BOOLEAN NOT NULL DEFAULT 0",
            "oidb_notes": "TEXT",
        }
        for col_name, col_def in additions.items():
            if col_name not in column_names:
                conn.execute(text(f'ALTER TABLE "application" ADD COLUMN {col_name} {col_def}'))

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-key-123"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["APPLICATION_UPLOAD_FOLDER"] = str(Path(app.instance_path) / APPLICATION_UPLOAD_SUBDIR)

    db.init_app(app)
    from .database import init_database_interfaces

    init_database_interfaces(app)
    from .routes import register_blueprints

    register_blueprints(app)

    @app.route("/")
    def home():
        return render_template("index.html", roles=ROLE_DEFINITIONS)

    @app.route("/portals/<role_slug>/")
    def role_entry(role_slug):
        # Redirect role entries to separated auth portals.
        if role_slug == "applicant":
            return redirect(url_for("auth.applicant_login"))
        return redirect(url_for("auth.staff_login", role=role_slug))

    with app.app_context():
        Path(app.config["APPLICATION_UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
        db.create_all()
        _ensure_user_role_column()
        _ensure_application_new_columns()

    return app