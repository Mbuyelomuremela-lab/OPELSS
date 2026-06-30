from app.extensions import db
from app.utils import sast_now


class AttendanceLog(db.Model):
    __tablename__ = "attendance_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    lab_id = db.Column(db.Integer, db.ForeignKey("labs.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    clock_in_time = db.Column(db.Time, nullable=True)
    clock_out_time = db.Column(db.Time, nullable=True)
    login_latitude = db.Column(db.Float, nullable=True)
    login_longitude = db.Column(db.Float, nullable=True)
    logout_latitude = db.Column(db.Float, nullable=True)
    logout_longitude = db.Column(db.Float, nullable=True)
    early_departure_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=sast_now)

    user = db.relationship("User", back_populates="attendance_logs")
    lab = db.relationship("Lab", back_populates="attendance_logs")
    audits = db.relationship("AttendanceAudit", back_populates="attendance_log", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AttendanceLog {self.user.full_name} {self.date}>"


class AttendanceAudit(db.Model):
    __tablename__ = "attendance_audits"

    id = db.Column(db.Integer, primary_key=True)
    attendance_id = db.Column(db.Integer, db.ForeignKey("attendance_logs.id"), nullable=False)
    changed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    old_values = db.Column(db.JSON, nullable=True)
    new_values = db.Column(db.JSON, nullable=True)
    timestamp = db.Column(db.DateTime, default=sast_now)

    attendance_log = db.relationship("AttendanceLog", back_populates="audits")

    def __repr__(self):
        return f"<AttendanceAudit {self.attendance_id} by {self.changed_by}>"
