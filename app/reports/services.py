from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from app.models.attendance import AttendanceLog
from app.models.asset import Asset
from app.models.visitor import Visitor
from app.models.programme import Programme
from app.models.lab import Lab
from app.models.province import Province


def parse_filter_ids(raw_values):
    if not raw_values:
        return []

    normalized = []
    values = raw_values if isinstance(raw_values, (list, tuple)) else [raw_values]
    for value in values:
        if value is None:
            continue
        for item in str(value).split(","):
            item = item.strip()
            if not item:
                continue
            if item.lower() == "all":
                return []
            try:
                normalized.append(int(item))
            except ValueError:
                continue
    return list(dict.fromkeys(normalized))


def get_report_rows(report_type, province_ids=None, lab_ids=None, start_date=None, end_date=None):
    province_ids = parse_filter_ids(province_ids)
    lab_ids = parse_filter_ids(lab_ids)

    if report_type == "attendance":
        query = AttendanceLog.query.join(Lab)
        if lab_ids:
            query = query.filter(AttendanceLog.lab_id.in_(lab_ids))
        if province_ids:
            query = query.filter(Lab.province_id.in_(province_ids))
        if start_date:
            query = query.filter(AttendanceLog.date >= start_date)
        if end_date:
            query = query.filter(AttendanceLog.date <= end_date)

        columns = ["Trainee", "Lab", "Province", "Date", "Clock In", "Clock Out", "Early Departure Reason"]
        rows = []
        for log in query.order_by(AttendanceLog.date).all():
            rows.append([
                log.user.full_name,
                log.lab.name,
                log.lab.province.name,
                log.date.strftime("%Y-%m-%d"),
                log.clock_in_time.strftime("%H:%M") if log.clock_in_time else "",
                log.clock_out_time.strftime("%H:%M") if log.clock_out_time else "",
                log.early_departure_reason or "",
            ])
        return {"columns": columns, "rows": rows}

    if report_type == "assets":
        query = Asset.query.join(Lab)
        if lab_ids:
            query = query.filter(Asset.lab_id.in_(lab_ids))
        if province_ids:
            query = query.filter(Lab.province_id.in_(province_ids))

        columns = ["Asset Name", "Category", "Serial Number", "Status", "Lab", "Province"]
        rows = []
        for asset in query.order_by(Asset.asset_name).all():
            rows.append([
                asset.asset_name,
                asset.category,
                asset.serial_number,
                asset.status,
                asset.lab.name,
                asset.lab.province.name,
            ])
        return {"columns": columns, "rows": rows}

    if report_type == "visitors":
        query = Visitor.query.join(Lab)
        if lab_ids:
            query = query.filter(Visitor.lab_id.in_(lab_ids))
        if province_ids:
            query = query.filter(Lab.province_id.in_(province_ids))
        if start_date:
            query = query.filter(Visitor.visit_date >= start_date)
        if end_date:
            query = query.filter(Visitor.visit_date <= end_date)

        columns = ["Visitor Name", "Category", "Purpose", "Visit Date", "Lab", "Province"]
        rows = []
        for visitor in query.order_by(Visitor.visit_date).all():
            rows.append([
                visitor.visitor_name,
                visitor.category,
                visitor.purpose,
                visitor.visit_date.strftime("%Y-%m-%d"),
                visitor.lab.name,
                visitor.lab.province.name,
            ])
        return {"columns": columns, "rows": rows}

    if report_type == "programmes":
        query = Programme.query.join(Lab)
        if lab_ids:
            query = query.filter(Programme.lab_id.in_(lab_ids))
        if province_ids:
            query = query.filter(Lab.province_id.in_(province_ids))
        if start_date:
            query = query.filter(Programme.date >= start_date)
        if end_date:
            query = query.filter(Programme.date <= end_date)

        columns = ["Title", "Objective", "Target Audience", "Attendance Count", "Activities Done", "Date", "Start", "End", "Lab", "Province", "Facilitated By"]
        rows = []
        for programme in query.order_by(Programme.date).all():
            rows.append([
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
                ", ".join(user.full_name for user in programme.facilitators),
            ])
        return {"columns": columns, "rows": rows}

    if report_type == "labs":
        query = Lab.query.join(Province)
        if lab_ids:
            query = query.filter(Lab.id.in_(lab_ids))
        if province_ids:
            query = query.filter(Lab.province_id.in_(province_ids))

        columns = ["Lab Name", "Province", "Latitude", "Longitude", "Radius Meters"]
        rows = []
        for lab in query.order_by(Lab.name).all():
            rows.append([
                lab.name,
                lab.province.name,
                lab.latitude,
                lab.longitude,
                lab.radius_meters,
            ])
        return {"columns": columns, "rows": rows}

    if report_type == "provinces":
        query = Province.query
        if province_ids:
            query = query.filter(Province.id.in_(province_ids))

        columns = ["Province Name", "Lab Count"]
        rows = []
        for province in query.order_by(Province.name).all():
            rows.append([province.name, len(province.labs)])
        return {"columns": columns, "rows": rows}

    raise ValueError("Invalid report type")


def export_report_excel(report_type, province_ids=None, lab_ids=None, start_date=None, end_date=None):
    workbook = Workbook()
    raw = workbook.active
    raw.title = "Raw Data"

    report_data = get_report_rows(report_type, province_ids=province_ids, lab_ids=lab_ids, start_date=start_date, end_date=end_date)
    raw.append(report_data["columns"])
    for row in report_data["rows"]:
        raw.append(row)

    summary = workbook.create_sheet(title="Summary")
    summary["A1"] = f"{report_type.capitalize()} report"
    summary["A1"].font = Font(bold=True)
    summary["A2"] = "Generated By"
    summary["B2"] = "OPELSS"
    summary["A3"] = "Rows"
    summary["B3"] = len(report_data["rows"])
    summary["A2"].alignment = Alignment(horizontal="left")
    summary["B2"].alignment = Alignment(horizontal="center")
    summary["A3"].alignment = Alignment(horizontal="left")
    summary["B3"].alignment = Alignment(horizontal="center")

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer
