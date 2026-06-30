from app.extensions import db
from app.utils import sast_now


class ActivityLog(db.Model):
    __tablename__ = "activity_logs"

    id = db.Column(db.Integer, primary_key=True)
    # Link to the actor, plus a snapshot of who they were so the trail
    # survives the user later being deleted.
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    actor_name = db.Column(db.String(120), nullable=False)
    actor_role = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(20), nullable=False)        # created / updated / deleted
    entity_type = db.Column(db.String(50), nullable=False)   # asset / enquiry / lab
    entity_id = db.Column(db.Integer, nullable=True)
    # Human label of the affected record, kept so the log stays readable
    # even after that record is deleted.
    entity_label = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=sast_now, nullable=False)

    def __repr__(self):
        return f"<ActivityLog {self.actor_name} {self.action} {self.entity_type} {self.entity_id}>"
