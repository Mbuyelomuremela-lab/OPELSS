from datetime import datetime
from flask import render_template, redirect, url_for, flash, request, abort, jsonify, send_file
from flask_login import login_required, current_user
from app.permissions import HQ_ROLES
from app.programmes import programmes_bp
from app.programmes.forms import ProgrammeForm
from app.programmes.services import create_programme, export_programmes_excel
from app.models.programme import Programme
from app.models.lab import Lab
from app.models.province import Province
from app.models.user import User
from app.extensions import db


def _set_facilitator_choices(form):
    users = User.query.filter_by(active=True).order_by(User.full_name).all()
    form.facilitators.choices = [(user.id, user.full_name) for user in users]


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


@programmes_bp.route("/")
@login_required
def index():
    date_from = _parse_date(request.args.get("date_from"))
    date_to = _parse_date(request.args.get("date_to"))
    lab_filter = request.args.get("lab_id", type=int)
    province_filter = request.args.get("province_id", type=int)
    facilitator_filter = request.args.get("facilitator_id", type=int)

    query = Programme.query.join(Lab)

    if current_user.role == "Lab Trainee":
        if not current_user.assigned_lab:
            flash("Your lab has not been assigned yet.", "warning")
            return redirect(url_for("dashboard.home"))
        query = query.filter(Programme.lab_id == current_user.assigned_lab_id)
    else:
        if lab_filter:
            query = query.filter(Programme.lab_id == lab_filter)
        if province_filter:
            query = query.filter(Lab.province_id == province_filter)

    if date_from:
        query = query.filter(Programme.date >= date_from)
    if date_to:
        query = query.filter(Programme.date <= date_to)
    if facilitator_filter:
        query = query.filter(Programme.facilitators.any(User.id == facilitator_filter))

    programmes = query.order_by(Programme.date.desc()).all()

    labs = Lab.query.order_by(Lab.name).all()
    provinces = Province.query.order_by(Province.name).all()
    facilitators = User.query.filter_by(active=True).order_by(User.full_name).all()

    form = ProgrammeForm()
    form.lab_id.choices = [(lab.id, f"{lab.name} ({lab.province.name})") for lab in labs]
    _set_facilitator_choices(form)
    if current_user.role == "Lab Trainee":
        form.lab_id.data = current_user.assigned_lab_id

    return render_template(
        "programmes/index.html",
        programmes=programmes,
        form=form,
        labs=labs,
        provinces=provinces,
        facilitators=facilitators,
        selected_date_from=request.args.get("date_from") or "",
        selected_date_to=request.args.get("date_to") or "",
        selected_lab_id=lab_filter,
        selected_province_id=province_filter,
        selected_facilitator_id=facilitator_filter,
    )


@programmes_bp.route("/export")
@login_required
def export():
    if current_user.role not in HQ_ROLES:
        abort(403)
    province_id = request.args.get("province_id", type=int)
    lab_id = request.args.get("lab_id", type=int)
    facilitator_id = request.args.get("facilitator_id", type=int)
    date_from = _parse_date(request.args.get("date_from"))
    date_to = _parse_date(request.args.get("date_to"))
    buffer = export_programmes_excel(
        province_id=province_id,
        lab_id=lab_id,
        date_from=date_from,
        date_to=date_to,
        facilitator_id=facilitator_id,
    )
    return send_file(
        buffer,
        as_attachment=True,
        download_name="programmes_export.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@programmes_bp.route("/create", methods=["POST"])
@login_required
def create():
    payload = request.get_json() if request.is_json else None
    form = ProgrammeForm(data=payload) if payload else ProgrammeForm()
    labs = Lab.query.order_by(Lab.name).all()
    form.lab_id.choices = [(lab.id, f"{lab.name} ({lab.province.name})") for lab in labs]
    _set_facilitator_choices(form)
    if form.validate_on_submit():
        if current_user.role == "Lab Trainee" and form.lab_id.data != current_user.assigned_lab_id:
            abort(403)
        programme = create_programme(
            title=form.title.data,
            objective=form.objective.data,
            target_audience=form.target_audience.data,
            attendance_count=form.attendance_count.data,
            activities_done=form.activities_done.data,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            lab_id=form.lab_id.data,
            created_by=current_user.id,
            facilitator_ids=form.facilitators.data,
        )
        if request.is_json:
            facilitator_names = ", ".join(user.full_name for user in programme.facilitators)
            facilitator_ids = ",".join(str(user.id) for user in programme.facilitators)
            row_html = f"""
            <tr
              data-id="{programme.id}"
              data-title="{programme.title}"
              data-objective="{programme.objective}"
              data-target-audience="{programme.target_audience}"
              data-attendance-count="{programme.attendance_count}"
              data-activities-done="{programme.activities_done}"
              data-date="{programme.date.strftime('%Y-%m-%d')}"
              data-start-time="{programme.start_time.strftime('%H:%M')}"
              data-end-time="{programme.end_time.strftime('%H:%M')}"
              data-lab-id="{programme.lab_id}"
              data-facilitator-ids="{facilitator_ids}"
            >
              <td>{programme.title}</td>
              <td>{programme.date.strftime('%Y-%m-%d')}</td>
              <td>{programme.attendance_count}</td>
              <td>{programme.lab.name}</td>
              <td>{facilitator_names}</td>
            </tr>
            """
            return jsonify(success=True, message="Programme logged successfully.", row_html=row_html, reload=False, reset=True)
        flash("Programme logged successfully.", "success")
    else:
        errors = "; ".join(
            [f"{field}: {', '.join(messages)}" for field, messages in form.errors.items()]
        )
        if request.is_json:
            return jsonify(success=False, message=f"Unable to log programme. {errors}"), 400
        flash("Unable to log programme. Please check the form.", "danger")

    return redirect(url_for("programmes.index"))


@programmes_bp.route("/<int:programme_id>/update", methods=["POST"])
@login_required
def update(programme_id):
    programme = Programme.query.get_or_404(programme_id)
    form = ProgrammeForm()
    labs = Lab.query.order_by(Lab.name).all()
    form.lab_id.choices = [(lab.id, f"{lab.name} ({lab.province.name})") for lab in labs]
    _set_facilitator_choices(form)
    if form.validate_on_submit():
        if current_user.role == "Lab Trainee" and programme.lab_id != current_user.assigned_lab_id:
            abort(403)
        if current_user.role == "Lab Trainee" and form.lab_id.data != current_user.assigned_lab_id:
            abort(403)
        programme.title = form.title.data
        programme.objective = form.objective.data
        programme.target_audience = form.target_audience.data
        programme.attendance_count = form.attendance_count.data
        programme.activities_done = form.activities_done.data
        programme.date = form.date.data
        programme.start_time = form.start_time.data
        programme.end_time = form.end_time.data
        programme.lab_id = form.lab_id.data
        programme.facilitators = User.query.filter(User.id.in_(form.facilitators.data)).all()
        db.session.commit()
        flash("Programme updated successfully.", "success")
    else:
        flash("Unable to update programme. Please review the form.", "danger")
    return redirect(url_for("programmes.index"))


@programmes_bp.route("/<int:programme_id>/delete", methods=["POST"])
@login_required
def delete(programme_id):
    programme = Programme.query.get_or_404(programme_id)
    if current_user.role == "Lab Trainee" and programme.lab_id != current_user.assigned_lab_id:
        abort(403)
    db.session.delete(programme)
    db.session.commit()
    flash("Programme deleted successfully.", "success")
    return redirect(url_for("programmes.index"))
