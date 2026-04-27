"""Application and document database models."""

from __future__ import annotations

from datetime import datetime

from .. import db


class Application(db.Model):
    """Transfer application submitted by an applicant."""

    __table_args__ = (db.UniqueConstraint("applicant_id", name="uq_application_applicant_id"),)

    id = db.Column(db.Integer, primary_key=True)
    applicant_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    full_name = db.Column(db.String(120), nullable=False)
    student_number = db.Column(db.String(32), nullable=False)
    source_university = db.Column(db.String(120), nullable=False)
    target_department = db.Column(db.String(120), nullable=False)
    current_gpa = db.Column(db.String(16), nullable=False)
    status = db.Column(db.String(32), nullable=False, default="submitted")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    applicant = db.relationship("User", back_populates="application")
    documents = db.relationship(
        "ApplicationDocument",
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="ApplicationDocument.document_slot",
    )


class ApplicationDocument(db.Model):
    """Uploaded document metadata for an application."""

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

    application = db.relationship("Application", back_populates="documents")