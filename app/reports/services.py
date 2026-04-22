from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from app.models.attendance import AttendanceLog
from app.models.asset import Asset
from app.models.visitor import Visitor
from app.models.programme import Programme
from app.models.lab import Lab
from app.models.province import Province
from app.models.enquiry import Enquiry


def export_report_excel(report_type, province_id=None, lab_id=None, start_date=None, end_date=None):
    workbook = Workbook()
    raw = workbook.active
    raw.title = "Raw Data"

    if report_type == "attendance":
        query = AttendanceLog.query.join(Lab)
        if lab_id:
            query = query.filter(AttendanceLog.lab_id == lab_id)
        if province_id:
            query = query.filter(Lab.province_id == province_id)
        if start_date:
            query = query.filter(AttendanceLog.date >= start_date)
        if end_date:
            query = query.filter(AttendanceLog.date <= end_date)

        raw.append(["Trainee", "Lab", "Province", "Date", "Clock In", "Clock Out", "Early Departure Reason"])
        for log in query.order_by(AttendanceLog.date).all():
            raw.append([
                log.user.full_name,
                log.lab.name,
                log.lab.province.name,
                log.date.strftime("%Y-%m-%d"),
                log.clock_in_time.strftime("%H:%M") if log.clock_in_time else "",
                log.clock_out_time.strftime("%H:%M") if log.clock_out_time else "",
                log.early_departure_reason or "",
            ])

    elif report_type == "assets":
        query = Asset.query.join(Lab)
        if lab_id:
            query = query.filter(Asset.lab_id == lab_id)
        if province_id:
            query = query.filter(Lab.province_id == province_id)
        raw.append(["Asset Name", "Category", "Serial Number", "Status", "Lab", "Province"])
        for asset in query.order_by(Asset.asset_name).all():
            raw.append([
                asset.asset_name,
                asset.category,
                asset.serial_number,
                asset.status,
                asset.lab.name,
                asset.lab.province.name,
            ])

    elif report_type == "visitors":
        query = Visitor.query.join(Lab)
        if lab_id:
            query = query.filter(Visitor.lab_id == lab_id)
        if province_id:
            query = query.filter(Lab.province_id == province_id)
        if start_date:
            query = query.filter(Visitor.visit_date >= start_date)
        if end_date:
            query = query.filter(Visitor.visit_date <= end_date)
        raw.append(["Visitor Name", "Category", "Purpose", "Visit Date", "Lab", "Province"])
        for visitor in query.order_by(Visitor.visit_date).all():
            raw.append([
                visitor.visitor_name,
                visitor.category,
                visitor.purpose,
                visitor.visit_date.strftime("%Y-%m-%d"),
                visitor.lab.name,
                visitor.lab.province.name,
            ])

    elif report_type == "programmes":
        query = Programme.query.join(Lab)
        if lab_id:
            query = query.filter(Programme.lab_id == lab_id)
        if province_id:
            query = query.filter(Lab.province_id == province_id)
        if start_date:
            query = query.filter(Programme.date >= start_date)
        if end_date:
            query = query.filter(Programme.date <= end_date)
        raw.append(["Title", "Objective", "Target Audience", "Attendance Count", "Activities Done", "Date", "Start", "End", "Lab", "Province"])
        for programme in query.order_by(Programme.date).all():
            raw.append([
                programme.title,
                programme.objective,
                programme.target_audience,
                programme.attendance_count,
                programme.activities_done,
                programme.date.strftime("%Y-%m-%d"),
                programme.start_time.strftime("%H:%M"),
                programme.end_time.strftime("%H:%M"),
                programme.lab.name,
                programme.lab.province.name,
            ])

    elif report_type == "labs":
        query = Lab.query.join(Province)
        if province_id:
            query = query.filter(Lab.province_id == province_id)
        raw.append(["Lab Name", "Province", "Latitude", "Longitude", "Radius Meters"])
        for lab in query.order_by(Lab.name).all():
            raw.append([
                lab.name,
                lab.province.name,
                lab.latitude,
                lab.longitude,
                lab.radius_meters,
            ])

    elif report_type == "provinces":
        raw.append(["Province Name", "Lab Count"])
        for province in Province.query.order_by(Province.name).all():
            raw.append([province.name, len(province.labs)])

    else:
        raise ValueError("Invalid report type")

    summary = workbook.create_sheet(title="Summary")
    summary["A1"] = f"{report_type.capitalize()} report"
    summary["A1"].font = Font(bold=True)
    summary["A2"] = "Generated By"
    summary["B2"] = "OPELSS"
    summary["A3"] = "Rows"
    summary["B3"] = len(raw._cells) - 1
    summary["A2"].alignment = Alignment(horizontal="left")
    summary["B2"].alignment = Alignment(horizontal="center")
    summary["A3"].alignment = Alignment(horizontal="left")
    summary["B3"].alignment = Alignment(horizontal="center")

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer
