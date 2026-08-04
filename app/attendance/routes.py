import calendar
from datetime import date

from flask import render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from app.attendance import attendance_bp
from app.attendance.forms import ClockInForm, ClockOutForm
from app.attendance.services import record_clock_in, record_clock_out, generate_timesheet_pdf
from app.models.attendance import AttendanceLog
from app.utils import lab_trainee_required, sast_today
from app.extensions import db


@attendance_bp.route("/")
@login_required
@lab_trainee_required
def overview():
    if not current_user.assigned_lab:
        flash("You are not assigned to a lab yet.", "danger")
        return redirect(url_for("dashboard.home"))

    clock_in_form = ClockInForm()
    clock_out_form = ClockOutForm()
    today = sast_today()

    # Selected month/year drives both the table and the export. Default: current month.
    month = request.args.get("month", type=int) or today.month
    year = request.args.get("year", type=int) or today.year
    if not 1 <= month <= 12:
        month, year = today.month, today.year

    # Show only the selected month's records (half-open range works for Date or DateTime).
    period_start = date(year, month, 1)
    period_end = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    logs = (
        AttendanceLog.query.filter_by(user_id=current_user.id)
        .filter(AttendanceLog.date >= period_start, AttendanceLog.date < period_end)
        .order_by(AttendanceLog.date.desc())
        .all()
    )

    # Last 12 months (most recent first) for the month picker.
    periods = []
    m, y = today.month, today.year
    for _ in range(12):
        periods.append({"month": m, "year": y, "label": f"{calendar.month_name[m]} {y}"})
        m -= 1
        if m == 0:
            m, y = 12, y - 1

    return render_template(
        "attendance/overview.html",
        clock_in_form=clock_in_form,
        clock_out_form=clock_out_form,
        logs=logs,
        assigned_lab=current_user.assigned_lab,
        today=today,
        periods=periods,
        selected_month=month,
        selected_year=year,
        period_label=f"{calendar.month_name[month]} {year}",
    )


@attendance_bp.route("/clock-in", methods=["POST"])
@login_required
@lab_trainee_required
def clock_in():
    form = ClockInForm()
    if form.validate_on_submit():
        latitude = float(form.latitude.data or 0)
        longitude = float(form.longitude.data or 0)
        log, error = record_clock_in(current_user, current_user.assigned_lab, latitude, longitude)
        if error:
            flash(error, "danger")
        else:
            flash("Clocked in successfully.", "success")
    else:
        flash("Geolocation values are required to clock in.", "danger")
    return redirect(url_for("attendance.overview"))


@attendance_bp.route("/clock-out", methods=["POST"])
@login_required
@lab_trainee_required
def clock_out():
    form = ClockOutForm()
    if form.validate_on_submit():
        latitude = float(form.latitude.data or 0)
        longitude = float(form.longitude.data or 0)
        log, error = record_clock_out(
            current_user,
            current_user.assigned_lab,
            latitude,
            longitude,
            form.early_departure_reason.data,
        )
        if error:
            flash(error, "danger")
        else:
            flash("Clocked out successfully.", "success")
    else:
        flash("Unable to process your clock-out request.", "danger")
    return redirect(url_for("attendance.overview"))


@attendance_bp.route("/export-timesheet")
@login_required
@lab_trainee_required
def export_timesheet():
    today = sast_today()
    month = int(request.args.get("month", today.month))
    year = int(request.args.get("year", today.year))
    buffer = generate_timesheet_pdf(current_user, month, year)
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"timesheet_{current_user.full_name.replace(' ', '_')}_{year}_{month}.pdf",
        mimetype="application/pdf",
    )
