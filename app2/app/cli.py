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
        import json as _json
        from . import db
        from .models import ApplicationDocumentORM, ApplicationORM, UserORM

        # Wipe in FK-safe order
        db.session.query(ApplicationDocumentORM).delete()
        db.session.query(ApplicationORM).delete()
        db.session.query(UserORM).delete()
        db.session.commit()
        click.echo("Tables cleared.")

        # --- Staff & admin ---
        # (email, password, role, department)
        staff_accounts = [
            ("admin@admin", "admin", "admin", None),
            ("oidb@test",   "test",  "oidb",  None),
            ("dean@test",   "test",  "dean",  None),
            ("ygk@test",    "test",  "ygk",   "computer_engineering"),
            ("ydyo@test",   "test",  "ydyo",  None),
        ]
        for email, pwd, role, dept in staff_accounts:
            u = UserORM(email=email, role=role, department=dept)
            u.set_password(pwd)
            db.session.add(u)
        db.session.flush()

        _PROGRAMS     = ["Computer Engineering", "Software Engineering", "Electrical and Electronics Engineering"]
        _SEMESTERS    = ["2025–2026 / Fall", "2025–2026 / Spring"]
        _UNIVERSITIES = ["Bosphorus University", "METU", "Ankara University", "Hacettepe University"]

        # Pre-built checker error payloads for mock "already auto-checked" applicants
        _ERRORS_GPA_LOW = _json.dumps([
            {"type": "field", "field": "current_gpa", "reason": "GPA 1.85 is below the minimum required 2.00.", "slot": None},
        ])
        _ERRORS_DOCS = _json.dumps([
            {"type": "document", "slot": 2, "reason": "Transcript is missing.", "field": None},
            {"type": "document", "slot": 3, "reason": "YKS Score Report is missing.", "field": None},
        ])
        _ERRORS_ID_AND_DOC = _json.dumps([
            {"type": "field", "field": "id_number", "reason": "ID number must contain only digits.", "slot": None},
            {"type": "document", "slot": 1, "reason": "Student Certificate is missing.", "field": None},
        ])

        # Schema:
        # (email, status, current_gpa, oidb_notes, dean_notes, forwarded_faculty,
        #  estimated_gpa, oysm_points, doc_checker_status, doc_checker_errors)
        scenarios = [
            # Freshly submitted — not yet auto-checked
            ("applicant1@test",  "submitted",          "3.20", None,                                       None,                                                    None,                     None,   None,    "needs_manual_check", None),
            # Submitted with low GPA — pre-populated checker errors
            ("applicant2@test",  "submitted",          "1.85", None,                                       None,                                                    None,                     None,   None,    "auto_checked",       _ERRORS_GPA_LOW),
            # Submitted with missing docs — pre-populated checker errors
            ("applicant3@test",  "submitted",          "2.90", None,                                       None,                                                    None,                     None,   "362.50", "auto_checked",       _ERRORS_DOCS),
            # Forwarded to YDYO — auto-checked, passed
            ("applicant4@test",  "forwarded_to_ydyo",  "3.10", None,                                       None,                                                    None,                     None,   "418.00", "auto_checked",       "[]"),
            # Forwarded to YDYO — auto-checked, invalid ID + missing student cert
            ("applicant5@test",  "forwarded_to_ydyo",  "3.45", None,                                       None,                                                    None,                     None,   "385.75", "auto_checked",       _ERRORS_ID_AND_DOC),
            # Forwarded to Dean — auto-checked OK; estimated GPA set
            ("applicant6@test",  "forwarded_to_dean",  "3.70", None,                                       None,                                                    None,                     "3.55", "452.00", "auto_checked",       "[]"),
            # Forwarded to YGK — full pipeline complete (department key used so ygk@test can see it)
            ("applicant7@test",  "forwarded_to_ygk",   "3.85", None,                                       None,                                                    "computer_engineering",   "3.60", "487.50", "auto_checked",       "[]"),
            # Returned by OIDB with notes — applicant must resubmit
            ("applicant8@test",  "returned",           "2.50", "Official transcript missing notary stamp.", None,                                                    None,                     None,   None,    "needs_manual_check", None),
            # Cancelled
            ("applicant9@test",  "cancelled",          "2.75", None,                                       None,                                                    None,                     None,   None,    "needs_manual_check", None),
            # Returned by Dean to applicant — dean_notes explain why
            ("applicant10@test", "returned",           "3.05", None,                                       "Please provide a notarised copy of your diploma.",       None,                     None,   "395.00", "auto_checked",       "[]"),
            # Returned by Dean to OIDB — re-enters OIDB queue as submitted; dean_notes shown in OIDB panel
            ("applicant11@test", "submitted",          "3.30", None,                                       "Transcript verification required before forwarding.",    None,                     None,   "428.50", "auto_checked",       "[]"),
            # Returned by Dean to YDYO — re-enters YDYO queue; dean_notes shown in YDYO panel
            ("applicant12@test", "forwarded_to_ydyo",  "3.55", None,                                       "English proficiency document needs re-evaluation.",      None,                     None,   "441.00", "auto_checked",       "[]"),
        ]

        for i, (email, status, gpa, oidb_notes, dean_notes, faculty, est_gpa, oysm, checker_status, checker_errors) in enumerate(scenarios):
            u = UserORM(email=email, role="applicant")
            u.set_password("test")
            db.session.add(u)
            db.session.flush()

            prog = _PROGRAMS[i % len(_PROGRAMS)]
            app_obj = ApplicationORM(
                applicant_id=u.id,
                full_name=f"Test Applicant {i + 1}",
                id_number=f"1234567{i:03d}" if email != "applicant5@test" else "TC-INVALID-XYZ",
                student_number=f"1234567{i:03d}",
                source_university=_UNIVERSITIES[i % len(_UNIVERSITIES)],
                is_currently_enrolled=True,
                target_program=prog,
                target_department=prog,
                target_semester=_SEMESTERS[i % len(_SEMESTERS)],
                current_gpa=gpa,
                estimated_gpa=est_gpa,
                oysm_points=oysm,
                status=status,
                oidb_notes=oidb_notes,
                dean_notes=dean_notes,
                forwarded_faculty=faculty,
                doc_checker_status=checker_status,
                doc_checker_errors=checker_errors,
                created_at=datetime.utcnow() - timedelta(days=len(scenarios) - i),
            )
            db.session.add(app_obj)

        db.session.commit()
        click.echo("Seed complete.")
        click.echo("  Staff  : admin@admin/admin  oidb@test/test  dean@test/test  ygk@test/test(dept:computer_engineering)  ydyo@test/test")
        click.echo("  Applicants: applicant1@test … applicant12@test  (password: test)")
        click.echo("  Scenarios:")
        click.echo("    applicant1:  submitted, needs_manual_check")
        click.echo("    applicant2:  submitted, auto_checked — GPA too low")
        click.echo("    applicant3:  submitted, auto_checked — missing transcript + YKS report")
        click.echo("    applicant4:  forwarded_to_ydyo, auto_checked OK")
        click.echo("    applicant5:  forwarded_to_ydyo, auto_checked — invalid ID + missing student cert")
        click.echo("    applicant6:  forwarded_to_dean, auto_checked OK, estimated_gpa set")
        click.echo("    applicant7:  forwarded_to_ygk, full pipeline complete")
        click.echo("    applicant8:  returned by OIDB with oidb_notes")
        click.echo("    applicant9:  cancelled")
        click.echo("    applicant10: returned by Dean to applicant (dean_notes set)")
        click.echo("    applicant11: returned by Dean to OIDB — re-entered as submitted (dean_notes set)")
        click.echo("    applicant12: returned by Dean to YDYO — re-entered as forwarded_to_ydyo (dean_notes set)")
