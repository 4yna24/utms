"""Application and document database models."""

from __future__ import annotations

from datetime import datetime

from .. import db


class ApplicationORM(db.Model):
    """Transfer application submitted by an applicant."""

    __tablename__ = "application"
    __table_args__ = (db.UniqueConstraint("applicant_id", name="uq_application_applicant_id"),)

    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)

    # Personal info
    full_name = db.Column(db.String(120), nullable=False)
    id_number = db.Column(db.String(64), nullable=False, default="")
    # Legacy — kept for backward compat; mirrors id_number on new submissions
    student_number = db.Column(db.String(32), nullable=False, default="")

    source_university = db.Column(db.String(120), nullable=False, default="")
    is_currently_enrolled = db.Column(db.Boolean, nullable=False, default=True)

    # Target program
    target_program = db.Column(db.String(120), nullable=False, default="")
    # Legacy — kept for backward compat; mirrors target_program on new submissions
    target_department = db.Column(db.String(120), nullable=False, default="")
    target_semester = db.Column(db.String(32), nullable=False, default="")

    current_gpa = db.Column(db.String(16), nullable=False)

    # Workflow
    status = db.Column(db.String(32), nullable=False, default="submitted")
    oidb_notes = db.Column(db.Text, nullable=True)
    # Set by YDYO: "eligible" = no internal test needed, "needs_test" = must take internal English test
    prep_school_status = db.Column(db.String(32), nullable=True)
    # Set by Dean when forwarding to departmental YGK
    forwarded_faculty = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Audit trail — auto-set by the before_flush listener in app/__init__.py
    last_edited_by_id = db.Column(db.Integer, nullable=True)
    last_edited_at = db.Column(db.DateTime, nullable=True)

    applicant = db.relationship("UserORM", back_populates="application")
    documents = db.relationship(
        "ApplicationDocumentORM",
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="ApplicationDocumentORM.document_slot",
    )


class ApplicationDocumentORM(db.Model):
    """Uploaded document metadata for an application."""

    __tablename__ = "application_document"
    __table_args__ = (
        db.UniqueConstraint("application_id", "document_slot", name="uq_application_document_slot"),
    )

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("application.id"), nullable=False, index=True)
    document_slot = db.Column(db.Integer, nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    application = db.relationship("ApplicationORM", back_populates="documents")
