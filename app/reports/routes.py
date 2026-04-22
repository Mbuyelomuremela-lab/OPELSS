from datetime import date
from flask import render_template, request, send_file, abort
from flask_login import login_required, current_user
from app.reports import reports_bp
from app.reports.services import export_report_excel
from app.models.lab import Lab
from app.models.province import Province


@reports_bp.route("/")
@login_required
def index():
    if current_user.role not in ["Admin", "HQ Trainee"]:
        abort(403)

    labs = Lab.query.order_by(Lab.name).all()
    provinces = Province.query.order_by(Province.name).all()
    return render_template("reports/index.html", labs=labs, provinces=provinces)


@reports_bp.route("/export/<report_type>")
@login_required
def export(report_type):
    if current_user.role not in ["Admin", "HQ Trainee"]:
        abort(403)

    province_id = request.args.get("province_id", type=int)
    lab_id = request.args.get("lab_id", type=int)
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    start_date = date.fromisoformat(start_date) if start_date else None
    end_date = date.fromisoformat(end_date) if end_date else None

    buffer = export_report_excel(report_type, province_id=province_id, lab_id=lab_id, start_date=start_date, end_date=end_date)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{report_type}_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
