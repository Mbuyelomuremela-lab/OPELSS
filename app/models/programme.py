from app.extensions import db
from app.utils import sast_now


class Programme(db.Model):
    __tablename__ = "programmes"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    objective = db.Column(db.Text, nullable=False)
    target_audience = db.Column(db.String(200), nullable=False)
    attendance_count = db.Column(db.Integer, nullable=False, default=0)
    activities_done = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    lab_id = db.Column(db.Integer, db.ForeignKey("labs.id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=sast_now)

    lab = db.relationship("Lab", back_populates="programmes")
    creator = db.relationship("User", back_populates="programmes_created")

    def __repr__(self):
        return f"<Programme {self.title} on {self.date}>"
