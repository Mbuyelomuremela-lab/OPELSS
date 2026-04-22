from io import BytesIO
from datetime import datetime, date, time
import os
from flask import current_app, url_for
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Image, SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from app.extensions import db
from app.models.attendance import AttendanceLog, AttendanceAudit
from app.models.user import User
from app.models.lab import Lab


def record_clock_in(user: User, lab: Lab, latitude: float, longitude: float):
    today = date.today()
    log = AttendanceLog.query.filter_by(user_id=user.id, date=today).first()
    if log and log.clock_in_time:
        return None, "You have already clocked in today."

    if not log:
        log = AttendanceLog(user_id=user.id, lab_id=lab.id, date=today)
        db.session.add(log)

    log.clock_in_time = datetime.now().time()
    log.login_latitude = latitude
    log.login_longitude = longitude
    db.session.commit()
    return log, None


def record_clock_out(user: User, lab: Lab, latitude: float, longitude: float, early_departure_reason: str = None):
    today = date.today()
    log = AttendanceLog.query.filter_by(user_id=user.id, date=today).first()
    if not log or not log.clock_in_time:
        return None, "You must clock in before clocking out."
    if log.clock_out_time:
        return None, "You have already clocked out for today."

    log.clock_out_time = datetime.now().time()
    log.logout_latitude = latitude
    log.logout_longitude = longitude
    if log.clock_out_time < time(16, 0) and not early_departure_reason:
        return None, "Provide an early departure reason if you leave before 16:00."
    log.early_departure_reason = early_departure_reason
    db.session.commit()
    return log, None


def audit_attendance(attendance: AttendanceLog, user_id: int, old_values: dict, new_values: dict):
    audit = AttendanceAudit(
        attendance_id=attendance.id,
        changed_by=user_id,
        old_values=old_values,
        new_values=new_values,
    )
    db.session.add(audit)
    db.session.commit()
    return audit


def generate_timesheet_pdf(user: User, month: int, year: int):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=inch, rightMargin=inch, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    story = []

    logo_path = os.path.join(current_app.static_folder, 'images', 'unisa.png')
    logo = Image(logo_path, width=1.2*inch, height=0.6*inch)
    logo.hAlign = 'LEFT'

    # 2. Add the logo to the story first so it appears at the top
    story.append(logo)
    story.append(Paragraph("CEDU: OAU E-Learning Lab", styles["Title"]))
    story.append(Paragraph("Trainee Monthly Timesheet", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Full Name: {user.full_name}", styles["Normal"]))
    story.append(Paragraph(f"Staff Number: {user.staff_number or 'N/A'}", styles["Normal"]))
    story.append(Paragraph(f"Role: {user.role}", styles["Normal"]))
    story.append(Paragraph(f"Month/Year: {month}/{year}", styles["Normal"]))
    story.append(Spacer(1, 12))

    logs = AttendanceLog.query.filter(
        AttendanceLog.user_id == user.id,
        db.extract("month", AttendanceLog.date) == month,
        db.extract("year", AttendanceLog.date) == year,
    ).order_by(AttendanceLog.date).all()

    data = [["Date", "Clock In", "Clock Out", "Hours", "Early Departure"]]
    total_hours = 0.0
    wrapped_style = styles["BodyText"]
    for log in logs:
        in_time = log.clock_in_time.strftime("%H:%M") if log.clock_in_time else ""
        out_time = log.clock_out_time.strftime("%H:%M") if log.clock_out_time else ""
        hours = 0.0
        if log.clock_in_time and log.clock_out_time:
            delta = datetime.combine(date.min, log.clock_out_time) - datetime.combine(date.min, log.clock_in_time)
            hours = round(delta.seconds / 3600, 2)
            total_hours += hours
        reason_text = log.early_departure_reason or "-"
        data.append([log.date.strftime("%Y-%m-%d"), in_time, out_time, f"{hours:.2f}", Paragraph(reason_text, wrapped_style)])

    table = Table(data, hAlign="LEFT", colWidths=[1.2 * inch, 0.95 * inch, 0.95 * inch, 0.8 * inch, 2.9 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0D3B66")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (3, -1), "CENTER"),
        ("ALIGN", (4, 0), (4, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("LEFTPADDING", (4, 1), (4, -1), 6),
        ("RIGHTPADDING", (4, 1), (4, -1), 6),
    ]))

    story.append(table)
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Total Hours: {total_hours:.2f}", styles["Heading3"]))
    story.append(Spacer(1, 24))
    story.append(Paragraph("___________________________", styles["Normal"]))
    story.append(Paragraph("Trainee Signature", styles["Normal"]))
    story.append(Spacer(1, 24))
    story.append(Paragraph("___________________________", styles["Normal"]))
    story.append(Paragraph("Centre Manager Signature", styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer
