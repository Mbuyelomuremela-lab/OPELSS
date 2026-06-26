from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from app.models.visitor import Visitor
from app.models.lab import Lab


def export_visitors_excel(province_id=None, lab_id=None, category=None, date_from=None, date_to=None):
    query = Visitor.query.join(Lab)
    if lab_id:
        query = query.filter(Visitor.lab_id == lab_id)
    if province_id:
        query = query.filter(Lab.province_id == province_id)
    if category:
        query = query.filter(Visitor.category == category)
    if date_from:
        query = query.filter(Visitor.visit_date >= date_from)
    if date_to:
        query = query.filter(Visitor.visit_date <= date_to)

    visitors = query.order_by(Visitor.visit_date.desc()).all()
    workbook = Workbook()
    raw = workbook.active
    raw.title = "Visitors"
    raw.append(["Visitor Name", "Category", "Student Number", "Cellphone Number", "Purpose", "Visit Date", "Lab", "Province"])

    for visitor in visitors:
        raw.append([
            visitor.visitor_name,
            visitor.category,
            visitor.student_number or "",
            visitor.cellphone_number or "",
            visitor.purpose,
            visitor.visit_date.strftime("%Y-%m-%d"),
            visitor.lab.name if visitor.lab else "",
            visitor.lab.province.name if visitor.lab and visitor.lab.province else "",
        ])

    summary = workbook.create_sheet(title="Summary")
    summary["A1"] = "Visitor Export Summary"
    summary["A1"].font = Font(bold=True)
    summary["A2"] = "Total Visitors"
    summary["B2"] = len(visitors)
    summary["A2"].alignment = Alignment(horizontal="left")
    summary["B2"].alignment = Alignment(horizontal="center")

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer
