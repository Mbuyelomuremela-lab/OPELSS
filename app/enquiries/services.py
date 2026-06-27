from datetime import datetime
from app.extensions import db
from app.models.enquiry import Enquiry


def generate_tracking_number():
    year = datetime.utcnow().year
    count = Enquiry.query.filter(Enquiry.created_at >= datetime(year, 1, 1)).count() + 1
    return f"ENQ-{year}-{count:06d}"


def create_enquiry(student_name: str, student_number: str, category: str, description: str,
                   lab_id: int, escalation_reason: str):
    now = datetime.utcnow()
    enquiry = Enquiry(
        tracking_number=generate_tracking_number(),
        student_name=student_name.strip(),
        student_number=student_number.strip(),
        category=category.strip(),
        description=description.strip(),
        lab_id=lab_id,
        escalation_reason=escalation_reason.strip(),
        status="Open",
        escalated=True,
        escalated_at=now,
    )
    db.session.add(enquiry)
    db.session.commit()
    return enquiry


def assign_enquiry(enquiry: Enquiry, assigned_to: int, assigned_by: int):
    enquiry.assigned_to = assigned_to
    enquiry.assigned_by = assigned_by
    enquiry.status = "Assigned"
    enquiry.assigned_at = datetime.utcnow()
    db.session.commit()
    return enquiry


def start_progress(enquiry: Enquiry):
    enquiry.status = "In Progress"
    enquiry.in_progress_at = datetime.utcnow()
    db.session.commit()
    return enquiry


def resolve_enquiry(enquiry: Enquiry, resolution_note: str):
    enquiry.status = "Resolved"
    enquiry.resolution_note = resolution_note.strip()
    enquiry.resolved_at = datetime.utcnow()
    db.session.commit()
    return enquiry


def mark_not_resolved(enquiry: Enquiry, not_resolved_reason: str):
    enquiry.status = "Not Resolved"
    enquiry.not_resolved_reason = not_resolved_reason.strip()
    enquiry.resolved_at = datetime.utcnow()
    db.session.commit()
    return enquiry


def close_enquiry(enquiry: Enquiry, closed_by: int):
    enquiry.status = "Closed"
    enquiry.closed_by = closed_by
    enquiry.closed_at = datetime.utcnow()
    db.session.commit()
    return enquiry


def reassign_enquiry(enquiry: Enquiry, assigned_to: int, assigned_by: int):
    enquiry.assigned_to = assigned_to
    enquiry.assigned_by = assigned_by
    enquiry.status = "Assigned"
    enquiry.assigned_at = datetime.utcnow()
    enquiry.not_resolved_reason = None
    db.session.commit()
    return enquiry
