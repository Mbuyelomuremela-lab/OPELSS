from datetime import date
from flask import render_template, request, send_file, abort
from flask_login import login_required, current_user
from app.permissions import HQ_ROLES
from app.reports import reports_bp
from app.reports.services import export_report_excel, get_report_rows, parse_filter_ids
from app.models.lab import Lab
from app.models.province import Province


@reports_bp.route("/")
@login_required
def index():
    if current_user.role not in HQ_ROLES:
        abort(403)

    report_type = request.args.get("report_type") or "attendance"
    province_ids = parse_filter_ids(request.args.getlist("province_id"))
    lab_ids = parse_filter_ids(request.args.getlist("lab_id"))
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    start_date = date.fromisoformat(start_date) if start_date else None
    end_date = date.fromisoformat(end_date) if end_date else None

    labs = Lab.query.order_by(Lab.name).all()
    provinces = Province.query.order_by(Province.name).all()

    try:
        report_data = get_report_rows(report_type, province_ids=province_ids, lab_ids=lab_ids, start_date=start_date, end_date=end_date)
    except ValueError:
        report_data = {"columns": [], "rows": []}

    return render_template(
        "reports/index.html",
        labs=labs,
        provinces=provinces,
        report_type=report_type,
        province_ids=province_ids,
        lab_ids=lab_ids,
        start_date=start_date,
        end_date=end_date,
        report_data=report_data,
    )


@reports_bp.route("/export/<report_type>")
@login_required
def export(report_type):
    if current_user.role not in HQ_ROLES:
        abort(403)

    province_ids = parse_filter_ids(request.args.getlist("province_ids")) or parse_filter_ids(request.args.get("province_id"))
    lab_ids = parse_filter_ids(request.args.getlist("lab_ids")) or parse_filter_ids(request.args.get("lab_id"))
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    start_date = date.fromisoformat(start_date) if start_date else None
    end_date = date.fromisoformat(end_date) if end_date else None

    buffer = export_report_excel(report_type, province_ids=province_ids, lab_ids=lab_ids, start_date=start_date, end_date=end_date)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{report_type}_report.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
