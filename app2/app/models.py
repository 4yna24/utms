from . import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __table_args__ = (
        db.UniqueConstraint('email', 'role', name='uq_user_email_role'),
    )

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(32), nullable=False, index=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)