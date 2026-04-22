from app.models.programme import Programme
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
    )
    db.session.add(programme)
    db.session.commit()
    return programme
