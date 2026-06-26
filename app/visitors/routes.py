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


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


@visitors_bp.route("/")
@login_required
def index():
    category = request.args.get("category") or None
    date_from = _parse_date(request.args.get("date_from"))
    date_to = _parse_date(request.args.get("date_to"))
    lab_filter = request.args.get("lab_id", type=int)
    province_filter = request.args.get("province_id", type=int)

    query = Visitor.query.join(Lab)

    if current_user.role == "Lab Trainee":
        if not current_user.assigned_lab:
            flash("You are not assigned to a lab yet.", "warning")
            return redirect(url_for("dashboard.home"))
        query = query.filter(Visitor.lab_id == current_user.assigned_lab_id)
    else:
        if lab_filter:
            query = query.filter(Visitor.lab_id == lab_filter)
        if province_filter:
            query = query.filter(Lab.province_id == province_filter)

    if category:
        query = query.filter(Visitor.category == category)
    if date_from:
        query = query.filter(Visitor.visit_date >= date_from)
    if date_to:
        query = query.filter(Visitor.visit_date <= date_to)

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
        selected_date_from=request.args.get("date_from") or "",
        selected_date_to=request.args.get("date_to") or "",
        selected_lab_id=lab_filter,
        selected_province_id=province_filter,
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

        is_unisa = form.category.data == "UNISA Student"
        visitor = Visitor(
            visitor_name=form.visitor_name.data,
            category=form.category.data,
            student_number=form.student_number.data if is_unisa else None,
            cellphone_number=None if is_unisa else form.cellphone_number.data,
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
              <td>{visitor.student_number or ''}</td>
              <td>{visitor.cellphone_number or ''}</td>
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
    province_id = request.args.get("province_id", type=int)
    lab_id = request.args.get("lab_id", type=int)
    category = request.args.get("category") or None
    date_from = _parse_date(request.args.get("date_from"))
    date_to = _parse_date(request.args.get("date_to"))
    buffer = export_visitors_excel(
        province_id=province_id,
        lab_id=lab_id,
        category=category,
        date_from=date_from,
        date_to=date_to,
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
        is_unisa = form.category.data == "UNISA Student"
        visitor.visitor_name = form.visitor_name.data
        visitor.category = form.category.data
        visitor.student_number = form.student_number.data if is_unisa else None
        visitor.cellphone_number = None if is_unisa else form.cellphone_number.data
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
