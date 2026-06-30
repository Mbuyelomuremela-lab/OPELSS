from app.extensions import db
from app.utils import sast_now, sast_today


class Announcement(db.Model):
    __tablename__ = "announcements"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    poster_filename = db.Column(db.String(255), nullable=True)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=sast_now)
    expiry_date = db.Column(db.Date, nullable=False, default=sast_today)

    creator = db.relationship("User", back_populates="announcements_created")

    def is_active(self):
        return self.expiry_date >= sast_today()

    def __repr__(self):
        return f"<Announcement {self.title}>"
