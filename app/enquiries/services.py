from datetime import datetime
from app.extensions import db
from app.models.enquiry import Enquiry


def generate_tracking_number():
    year = datetime.utcnow().year
    count = Enquiry.query.filter(Enquiry.created_at >= datetime(year, 1, 1)).count() + 1
    return f"ENQ-{year}-{count:06d}"


def create_enquiry(student_name: str, student_number: str, category: str, description: str, lab_id: int):
    tracking_number = generate_tracking_number()
    enquiry = Enquiry(
        tracking_number=tracking_number,
        student_name=student_name.strip(),
        student_number=student_number.strip(),
        category=category.strip(),
        description=description.strip(),
        lab_id=lab_id,
    )
    db.session.add(enquiry)
    db.session.commit()
    return enquiry


def update_enquiry_status(enquiry: Enquiry, status: str, resolution_note: str = None, escalated: bool = False):
    enquiry.status = status
    enquiry.resolution_note = resolution_note
    enquiry.escalated = escalated or (status == "Escalated")
    db.session.commit()
    return enquiry
