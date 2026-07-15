from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from app.models.programme import Programme
from app.models.lab import Lab
from app.models.user import User
from app.extensions import db


def create_programme(
    title: str,
    objective: str,
    target_audience: str,
    attendance_count: int,
    activities_done: str,
    date,
    start_time,
    end_time,
    lab_id: int,
    created_by: int,
    facilitator_ids: list[int],
):
    programme = Programme(
        title=title.strip(),
        objective=objective.strip(),
        target_audience=target_audience.strip(),
        attendance_count=attendance_count,
        activities_done=activities_done.strip(),
        date=date,
        start_time=start_time,
        end_time=end_time,
        lab_id=lab_id,
        created_by=created_by,
        facilitators=User.query.filter(User.id.in_(facilitator_ids)).all(),
    )
    db.session.add(programme)
    db.session.commit()
    return programme


def export_programmes_excel(province_id=None, lab_id=None, date_from=None, date_to=None, facilitator_id=None):
    query = Programme.query.join(Lab)
    if lab_id:
        query = query.filter(Programme.lab_id == lab_id)
    if province_id:
        query = query.filter(Lab.province_id == province_id)
    if date_from:
        query = query.filter(Programme.date >= date_from)
    if date_to:
        query = query.filter(Programme.date <= date_to)
    if facilitator_id:
        query = query.filter(Programme.facilitators.any(User.id == facilitator_id))

    programmes = query.order_by(Programme.date.desc()).all()

    workbook = Workbook()
    raw = workbook.active
    raw.title = "Programmes"
    raw.append([
        "Title", "Objective", "Target Audience", "Attendance Count",
        "Activities Done", "Date", "Start", "End", "Lab", "Province", "Facilitated By",
    ])
    for programme in programmes:
        raw.append([
            programme.title,
            programme.objective,
            programme.target_audience,
            programme.attendance_count,
            programme.activities_done,
            programme.date.strftime("%Y-%m-%d"),
            programme.start_time.strftime("%H:%M"),
            programme.end_time.strftime("%H:%M"),
            programme.lab.name if programme.lab else "",
            programme.lab.province.name if programme.lab and programme.lab.province else "",
            ", ".join(user.full_name for user in programme.facilitators),
        ])

    summary = workbook.create_sheet(title="Summary")
    summary["A1"] = "Programme Export Summary"
    summary["A1"].font = Font(bold=True)
    summary["A2"] = "Total Programmes"
    summary["B2"] = len(programmes)
    summary["A2"].alignment = Alignment(horizontal="left")
    summary["B2"].alignment = Alignment(horizontal="center")

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    return buffer
