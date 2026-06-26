from flask_login import current_user
from app.extensions import db
from app.models.activity_log import ActivityLog


def log_activity(action, entity_type, entity_label=None, entity_id=None):
    """Record an auditable action by the current user.

    Commits its own row so it can be called after the entity operation has
    already been committed (i.e. only once the action is known to have
    succeeded). For deletes, capture ``entity_label`` before deleting.
    """
    entry = ActivityLog(
        user_id=getattr(current_user, "id", None),
        actor_name=getattr(current_user, "full_name", "Unknown"),
        actor_role=getattr(current_user, "role", "Unknown"),
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        entity_label=(entity_label[:255] if entity_label else None),
    )
    db.session.add(entry)
    db.session.commit()
    return entry
