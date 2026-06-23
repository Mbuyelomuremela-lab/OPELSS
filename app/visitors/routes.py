from datetime import datetime

from flask import render_template, redirect, url_for, flash, request, send_file, abort, jsonify
from flask_login import login_required, current_user
from app.visitors import visitors_bp
from app.visitors.forms import VisitorForm
from app.visitors.services import export_visitors_excel
from app.models.visitor import Visitor
from app.models.lab import Lab
from app.models.province import Province
from app.utils import role_required
from app.extensions import db


@visitors_bp.route("/")
@login_required
def index():
    category = request.args.get("category", type=str)
    visit_date_str = request.args.get("visit_date", type=str)
    lab_id = request.args.get("lab_id", type=int)
    province_id = request.args.get("province_id", type=int)

    query = Visitor.query.join(Lab)
    if current_user.role == "Lab Trainee":
        if not current_user.assigned_lab:
            flash("You are not assigned to a lab yet.", "warning")
            return redirect(url_for("dashboard.home"))
        query = query.filter(Visitor.lab_id == current_user.assigned_lab_id)
    if category:
        query = query.filter(Visitor.category == category)
    if visit_date_str:
        try:
            visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d").date()
            query = query.filter(Visitor.visit_date == visit_date)
        except ValueError:
            visit_date = None
    else:
        visit_date = None

    if current_user.role != "Lab Trainee":
        if lab_id:
            query = query.filter(Visitor.lab_id == lab_id)
        if province_id:
            query = query.filter(Lab.province_id == province_id)

    visitors = query.order_by(Visitor.visit_date.desc()).all()
    labs = Lab.query.order_by(Lab.name).all()
    provinces = Province.query.order_by(Province.name).all()

    form = VisitorForm()
    form.lab_id.choices = [(lab.id, f"{lab.name} ({lab.province.name})") for lab in labs]
    if current_user.role == "Lab Trainee":
        form.lab_id.data = current_user.assigned_lab_id

    return render_template(
        "visitors/index.html",
        visitors=visitors,
        form=form,
        labs=labs,
        provinces=provinces,
        selected_category=category,
        selected_visit_date=visit_date_str,
        selected_lab_id=str(lab_id) if lab_id is not None else "",
        selected_province_id=str(province_id) if province_id is not None else "",
    )


@visitors_bp.route("/create", methods=["POST"])
@login_required
def create_visitor():
    payload = request.get_json() if request.is_json else None
    form = VisitorForm(data=payload) if payload else VisitorForm()
    form.lab_id.choices = [(lab.id, f"{lab.name} ({lab.province.name})") for lab in Lab.query.order_by(Lab.name).all()]
    if form.validate_on_submit():
        if current_user.role == "Lab Trainee" and form.lab_id.data != current_user.assigned_lab_id:
            abort(403)

        visitor = Visitor(
            visitor_name=form.visitor_name.data,
            category=form.category.data,
            student_number=form.student_number.data if form.category.data == "Unisa Student" else None,
            id_number=form.id_number.data if form.category.data != "Unisa Student" else None,
            purpose=form.purpose.data,
            visit_date=form.visit_date.data,
            lab_id=form.lab_id.data,
        )
        db.session.add(visitor)
        db.session.commit()
        if request.is_json:
            row_html = f"""
            <tr>
              <td>{visitor.visitor_name}</td>
              <td>{visitor.category}</td>
              <td>{visitor.purpose}</td>
              <td>{visitor.visit_date.strftime('%Y-%m-%d')}</td>
              <td>{visitor.lab.name}</td>
            </tr>
            """
            return jsonify(success=True, message="Visitor logged successfully.", row_html=row_html, reload=False, reset=True)
        flash("Visitor logged successfully.", "success")
    else:
        errors = "; ".join(
            [f"{field}: {', '.join(messages)}" for field, messages in form.errors.items()]
        )
        if request.is_json:
            return jsonify(success=False, message=f"Unable to log visitor. {errors}"), 400
        flash("Unable to log visitor. Please review the form.", "danger")
    return redirect(url_for("visitors.index"))


@visitors_bp.route("/export")
@login_required
def export():
    if current_user.role not in ["Admin", "HQ Trainee"]:
        abort(403)
    category = request.args.get("category", type=str)
    visit_date_str = request.args.get("visit_date", type=str)
    lab_id = request.args.get("lab_id", type=int)
    province_id = request.args.get("province_id", type=int)
    visit_date = None
    if visit_date_str:
        try:
            visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d").date()
        except ValueError:
            visit_date = None
    buffer = export_visitors_excel(
        province_id=province_id,
        lab_id=lab_id,
        category=category,
        visit_date=visit_date,
    )
    return send_file(
        buffer,
        as_attachment=True,
        download_name="visitors_export.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@visitors_bp.route("/<int:visitor_id>/update", methods=["POST"])
@login_required
def update_visitor(visitor_id):
    visitor = Visitor.query.get_or_404(visitor_id)
    form = VisitorForm()
    form.lab_id.choices = [(lab.id, f"{lab.name} ({lab.province.name})") for lab in Lab.query.order_by(Lab.name).all()]
    if form.validate_on_submit():
        if current_user.role == "Lab Trainee" and visitor.lab_id != current_user.assigned_lab_id:
            abort(403)
        if current_user.role == "Lab Trainee" and form.lab_id.data != current_user.assigned_lab_id:
            abort(403)
        visitor.visitor_name = form.visitor_name.data
        visitor.category = form.category.data
        visitor.student_number = form.student_number.data if form.category.data == "Unisa Student" else None
        visitor.id_number = form.id_number.data if form.category.data != "Unisa Student" else None
        visitor.purpose = form.purpose.data
        visitor.visit_date = form.visit_date.data
        visitor.lab_id = form.lab_id.data
        db.session.commit()
        flash("Visitor updated successfully.", "success")
    else:
        flash("Unable to update visitor. Please review the form.", "danger")
    return redirect(url_for("visitors.index"))


@visitors_bp.route("/<int:visitor_id>/delete", methods=["POST"])
@login_required
def delete_visitor(visitor_id):
    visitor = Visitor.query.get_or_404(visitor_id)
    if current_user.role == "Lab Trainee" and visitor.lab_id != current_user.assigned_lab_id:
        abort(403)
    db.session.delete(visitor)
    db.session.commit()
    flash("Visitor deleted successfully.", "success")
    return redirect(url_for("visitors.index"))
