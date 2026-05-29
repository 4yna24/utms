"""Flask CLI management commands."""

from __future__ import annotations

from datetime import datetime, timedelta

import click


def register_commands(app) -> None:
    """Attach CLI commands to the Flask app."""

    @app.cli.command("init-admin")
    @click.option("--email", default="admin@admin", show_default=True)
    @click.option("--password", default="admin", show_default=True)
    def init_admin(email: str, password: str) -> None:
        """Create the default admin account if it does not already exist."""
        from . import db
        from .models import UserORM

        existing = UserORM.query.filter_by(email=email, role="admin").first()
        if existing:
            click.echo(f"Admin '{email}' already exists — skipping.")
            return
        user = UserORM(email=email, role="admin")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Admin account created: {email}")

    @app.cli.command("seed-db")
    @click.confirmation_option(prompt="This wipes ALL data and reseeds. Continue?")
    def seed_db() -> None:
        """Wipe the database and load synthetic test data."""
        from . import db
        from .models import ApplicationDocumentORM, ApplicationORM, UserORM

        # Wipe in FK-safe order
        db.session.query(ApplicationDocumentORM).delete()
        db.session.query(ApplicationORM).delete()
        db.session.query(UserORM).delete()
        db.session.commit()
        click.echo("Tables cleared.")

        # --- Staff & admin ---
        staff_accounts = [
            ("admin@admin", "admin", "admin"),
            ("oidb@test",   "test",  "oidb"),
            ("dean@test",   "test",  "dean"),
            ("ygk@test",    "test",  "ygk"),
            ("ydyo@test",   "test",  "ydyo"),
        ]
        for email, pwd, role in staff_accounts:
            u = UserORM(email=email, role=role)
            u.set_password(pwd)
            db.session.add(u)
        db.session.flush()

        # --- Applicants with one application each across every status ---
        _PROGRAMS     = ["Computer Engineering", "Software Engineering", "Electrical and Electronics Engineering"]
        _SEMESTERS    = ["2025–2026 / Fall", "2025–2026 / Spring"]
        _UNIVERSITIES = ["Bosphorus University", "METU", "Ankara University", "Hacettepe University"]

        scenarios = [
            # (email,                status,              oidb_notes,                          forwarded_faculty)
            ("applicant1@test", "submitted",            None,                                None),
            ("applicant2@test", "forwarded_to_oidb",    None,                                None),
            ("applicant3@test", "forwarded_to_dean",    None,                                None),
            ("applicant4@test", "forwarded_to_ydyo",    None,                                None),
            ("applicant5@test", "forwarded_to_ygk",     None,                                "Faculty of Engineering"),
            ("applicant6@test", "returned",             "Missing official transcript.",       None),
            ("applicant7@test", "cancelled",            None,                                None),
        ]

        for i, (email, status, notes, faculty) in enumerate(scenarios):
            u = UserORM(email=email, role="applicant")
            u.set_password("test")
            db.session.add(u)
            db.session.flush()

            gpa = round(min(4.0, 2.40 + i * 0.25), 2)
            prog = _PROGRAMS[i % len(_PROGRAMS)]
            app_obj = ApplicationORM(
                applicant_id=u.id,
                full_name=f"Test Applicant {i + 1}",
                id_number=f"1234567{i:03d}",
                student_number=f"1234567{i:03d}",
                source_university=_UNIVERSITIES[i % len(_UNIVERSITIES)],
                is_currently_enrolled=True,
                target_program=prog,
                target_department=prog,
                target_semester=_SEMESTERS[i % len(_SEMESTERS)],
                current_gpa=str(gpa),
                status=status,
                oidb_notes=notes,
                forwarded_faculty=faculty,
                created_at=datetime.utcnow() - timedelta(days=len(scenarios) - i),
            )
            db.session.add(app_obj)

        db.session.commit()
        click.echo("Seed complete.")
        click.echo("  Staff  : admin@admin/admin  oidb@test/test  dean@test/test  ygk@test/test  ydyo@test/test")
        click.echo("  Applicants: applicant1@test … applicant7@test  (password: test)")
        click.echo("  Statuses  : submitted → forwarded_to_oidb → forwarded_to_dean → forwarded_to_ydyo → forwarded_to_ygk → returned → cancelled")
