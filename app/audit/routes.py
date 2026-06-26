from datetime import datetime
from flask import render_template, request
from flask_login import login_required
from app.audit import audit_bp
from app.models.activity_log import ActivityLog
from app.models.user import User
from app.utils import role_required

ACTIONS = ["created", "updated", "deleted"]
ENTITY_TYPES = ["asset", "enquiry", "lab"]


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


@audit_bp.route("/")
@login_required
@role_required("Admin")
def index():
    action = request.args.get("action") or None
    entity_type = request.args.get("entity_type") or None
    user_id = request.args.get("user_id", type=int)
    date_from = _parse_date(request.args.get("date_from"))
    date_to = _parse_date(request.args.get("date_to"))
    page = request.args.get("page", 1, type=int)

    query = ActivityLog.query
    if action:
        query = query.filter(ActivityLog.action == action)
    if entity_type:
        query = query.filter(ActivityLog.entity_type == entity_type)
    if user_id:
        query = query.filter(ActivityLog.user_id == user_id)
    if date_from:
        query = query.filter(ActivityLog.timestamp >= datetime.combine(date_from, datetime.min.time()))
    if date_to:
        query = query.filter(ActivityLog.timestamp <= datetime.combine(date_to, datetime.max.time()))

    pagination = query.order_by(ActivityLog.timestamp.desc()).paginate(
        page=page, per_page=25, error_out=False
    )

    users = User.query.order_by(User.full_name).all()

    return render_template(
        "audit/index.html",
        logs=pagination.items,
        pagination=pagination,
        users=users,
        actions=ACTIONS,
        entity_types=ENTITY_TYPES,
        selected_action=action,
        selected_entity_type=entity_type,
        selected_user_id=user_id,
        selected_date_from=request.args.get("date_from") or "",
        selected_date_to=request.args.get("date_to") or "",
    )
