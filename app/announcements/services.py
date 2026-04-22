from app.extensions import db
from app.models.announcement import Announcement


def create_announcement(title: str, message: str, expiry_date, created_by: int, poster_filename: str = None):
    announcement = Announcement(
        title=title.strip(),
        message=message.strip(),
        expiry_date=expiry_date,
        created_by=created_by,
        poster_filename=poster_filename,
    )
    db.session.add(announcement)
    db.session.commit()
    return announcement
