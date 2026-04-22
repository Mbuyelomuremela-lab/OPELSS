from datetime import datetime
from app.extensions import db


class Enquiry(db.Model):
    __tablename__ = "enquiries"

    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(30), unique=True, nullable=False)
    student_name = db.Column(db.String(120), nullable=False)
    student_number = db.Column(db.String(60), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Open")
    resolution_note = db.Column(db.Text, nullable=True)
    lab_id = db.Column(db.Integer, db.ForeignKey("labs.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    escalated = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    lab = db.relationship("Lab", back_populates="enquiries")

    def __repr__(self):
        return f"<Enquiry {self.tracking_number} {self.status}>"
