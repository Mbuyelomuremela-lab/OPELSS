from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    staff_number = db.Column(db.String(8), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    assigned_lab_id = db.Column(db.Integer, db.ForeignKey("labs.id"), nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=False)

    assigned_lab = db.relationship("Lab", back_populates="users")
    attendance_logs = db.relationship("AttendanceLog", back_populates="user", cascade="all, delete-orphan")
    assets_created = db.relationship("Asset", back_populates="creator", foreign_keys="Asset.created_by")
    programmes_created = db.relationship("Programme", back_populates="creator", foreign_keys="Programme.created_by")
    announcements_created = db.relationship("Announcement", back_populates="creator", foreign_keys="Announcement.created_by")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def is_active(self):
        return self.active

    def __repr__(self):
        return f"<User {self.full_name} ({self.role})>"
