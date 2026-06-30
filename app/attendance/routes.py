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
    logs = AttendanceLog.query.filter_by(user_id=current_user.id).order_by(AttendanceLog.date.desc()).limit(15).all()

    return render_template(
        "attendance/overview.html",
        clock_in_form=clock_in_form,
        clock_out_form=clock_out_form,
        logs=logs,
        assigned_lab=current_user.assigned_lab,
        today=today,
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
