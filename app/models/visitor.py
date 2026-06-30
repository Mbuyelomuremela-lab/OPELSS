from app.extensions import db
from app.utils import sast_today


class Visitor(db.Model):
    __tablename__ = "visitors"

    id = db.Column(db.Integer, primary_key=True)
    visitor_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    student_number = db.Column(db.String(8))
    cellphone_number = db.Column(db.String(20))
    purpose = db.Column(db.Text, nullable=False)
    visit_date = db.Column(db.Date, nullable=False, default=sast_today)
    lab_id = db.Column(db.Integer, db.ForeignKey("labs.id"), nullable=False)

    lab = db.relationship("Lab", back_populates="visitors")

    def __repr__(self):
        return f"<Visitor {self.visitor_name} on {self.visit_date}>"
