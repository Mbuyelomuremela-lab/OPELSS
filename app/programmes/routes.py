from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app.programmes import programmes_bp
from app.programmes.forms import ProgrammeForm
from app.programmes.services import create_programme
from app.models.programme import Programme
from app.models.lab import Lab
from app.extensions import db


@programmes_bp.route("/")
@login_required
def index():
    if current_user.role == "Lab Trainee":
        if not current_user.assigned_lab:
            flash("Your lab has not been assigned yet.", "warning")
            return redirect(url_for("dashboard.home"))
        programmes = Programme.query.filter_by(lab_id=current_user.assigned_lab_id).order_by(Programme.date.desc()).all()
    else:
        programmes = Programme.query.order_by(Programme.date.desc()).all()

    form = ProgrammeForm()
    labs = Lab.query.order_by(Lab.name).all()
    form.lab_id.choices = [(lab.id, f"{lab.name} ({lab.province.name})") for lab in labs]
    if current_user.role == "Lab Trainee":
        form.lab_id.data = current_user.assigned_lab_id

    return render_template("programmes/index.html", programmes=programmes, form=form)


@programmes_bp.route("/create", methods=["POST"])
@login_required
def create():
    payload = request.get_json() if request.is_json else None
    form = ProgrammeForm(data=payload) if payload else ProgrammeForm()
    labs = Lab.query.order_by(Lab.name).all()
    form.lab_id.choices = [(lab.id, f"{lab.name} ({lab.province.name})") for lab in labs]
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
        )
        if request.is_json:
            row_html = f"""
            <tr>
              <td>{programme.title}</td>
              <td>{programme.date.strftime('%Y-%m-%d')}</td>
              <td>{programme.attendance_count}</td>
              <td>{programme.lab.name}</td>
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
