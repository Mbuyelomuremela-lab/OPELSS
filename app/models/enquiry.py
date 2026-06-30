from app.extensions import db
from app.utils import sast_now


class Enquiry(db.Model):
    __tablename__ = "enquiries"

    id = db.Column(db.Integer, primary_key=True)
    tracking_number = db.Column(db.String(30), unique=True, nullable=False)
    student_name = db.Column(db.String(120), nullable=False)
    student_number = db.Column(db.String(60), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    # Statuses: Open | Assigned | In Progress | Resolved | Not Resolved | Closed
    status = db.Column(db.String(50), nullable=False, default="Open")
    escalation_reason = db.Column(db.Text, nullable=True)
    resolution_note = db.Column(db.Text, nullable=True)
    not_resolved_reason = db.Column(db.Text, nullable=True)
    lab_id = db.Column(db.Integer, db.ForeignKey("labs.id"), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    assigned_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    closed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    escalated = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=sast_now)
    escalated_at = db.Column(db.DateTime, nullable=True)
    assigned_at = db.Column(db.DateTime, nullable=True)
    in_progress_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    closed_at = db.Column(db.DateTime, nullable=True)

    lab = db.relationship("Lab", back_populates="enquiries")
    assignee = db.relationship("User", foreign_keys=[assigned_to], backref="assigned_enquiries")
    assigner = db.relationship("User", foreign_keys=[assigned_by])
    closer = db.relationship("User", foreign_keys=[closed_by])

    def __repr__(self):
        return f"<Enquiry {self.tracking_number} {self.status}>"
