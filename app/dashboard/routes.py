from flask import render_template, abort
from flask_login import login_required, current_user
from app.dashboard import dashboard_bp
from app.utils import sast_today
from app.extensions import db
from app.models.lab import Lab
from app.models.province import Province
from app.models.user import User
from app.models.asset import Asset
from app.models.visitor import Visitor
from app.models.enquiry import Enquiry
from app.models.programme import Programme
from app.models.attendance import AttendanceLog


@dashboard_bp.route("/")
@login_required
def home():
    if current_user.role in ["Admin", "HQ Trainee"]:
        lab_count = Lab.query.count()
        province_count = Province.query.count()
        user_count = User.query.count()
        asset_count = Asset.query.count()
        visitor_count = Visitor.query.count()
        enquiry_count = Enquiry.query.count()
        programme_count = Programme.query.count()
        escalated_count = Enquiry.query.filter(
            Enquiry.status.in_(["Open", "Assigned", "In Progress", "Not Resolved"])
        ).count()

        return render_template(
            "dashboard/admin_hq_dashboard.html",
            lab_count=lab_count,
            province_count=province_count,
            user_count=user_count,
            asset_count=asset_count,
            visitor_count=visitor_count,
            enquiry_count=enquiry_count,
            programme_count=programme_count,
            escalated_count=escalated_count,
        )

    if current_user.role == "Lab Trainee":
        lab = current_user.assigned_lab
        if not lab:
            abort(403)

        today = sast_today()
        monthly_attendance = AttendanceLog.query.filter(
            AttendanceLog.user_id == current_user.id,
            db.extract("month", AttendanceLog.date) == today.month,
            db.extract("year", AttendanceLog.date) == today.year,
        ).count()
        assets_count = Asset.query.filter_by(lab_id=lab.id).count()
        visitors_count = Visitor.query.filter_by(lab_id=lab.id).count()
        enquiries_count = Enquiry.query.filter_by(lab_id=lab.id).count()
        programmes_count = Programme.query.filter_by(lab_id=lab.id).count()

        return render_template(
            "dashboard/lab_dashboard.html",
            lab=lab,
            monthly_attendance=monthly_attendance,
            assets_count=assets_count,
            visitors_count=visitors_count,
            enquiries_count=enquiries_count,
            programmes_count=programmes_count,
        )

    abort(403)
