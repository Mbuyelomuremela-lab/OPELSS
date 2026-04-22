from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app.enquiries import enquiries_bp
from app.enquiries.forms import EnquiryForm, UpdateEnquiryForm, TrackingForm
from app.enquiries.services import create_enquiry, update_enquiry_status
from app.models.enquiry import Enquiry
from app.models.lab import Lab
from app.models.province import Province
from app.extensions import db


@enquiries_bp.route("/")
@login_required
def index():
    if current_user.role == "Lab Trainee":
        if not current_user.assigned_lab:
            flash("Your lab has not been assigned yet.", "warning")
            return redirect(url_for("dashboard.home"))
        enquiries = Enquiry.query.filter_by(lab_id=current_user.assigned_lab_id).order_by(Enquiry.created_at.desc()).all()
    else:
        enquiries = Enquiry.query.order_by(Enquiry.created_at.desc()).all()

    labs = Lab.query.order_by(Lab.name).all()
    form = EnquiryForm()
    form.lab_id.choices = [(lab.id, f"{lab.name} ({lab.province.name})") for lab in labs]
    if current_user.role == "Lab Trainee":
        form.lab_id.data = current_user.assigned_lab_id

    return render_template("enquiries/index.html", enquiries=enquiries, form=form)


@enquiries_bp.route("/create", methods=["POST"])
@login_required
def create():
    payload = request.get_json() if request.is_json else None
    form = EnquiryForm(data=payload) if payload else EnquiryForm()
    form.lab_id.choices = [(lab.id, f"{lab.name} ({lab.province.name})") for lab in Lab.query.order_by(Lab.name).all()]
    if form.validate_on_submit():
        if current_user.role == "Lab Trainee" and form.lab_id.data != current_user.assigned_lab_id:
            abort(403)
        enquiry = create_enquiry(
            student_name=form.student_name.data,
            student_number=form.student_number.data,
            category=form.category.data,
            description=form.description.data,
            lab_id=form.lab_id.data,
        )
        if request.is_json:
            row_html = f"""
            <tr>
              <td>{enquiry.tracking_number}</td>
              <td>{enquiry.student_name}</td>
              <td>{enquiry.category}</td>
              <td>{enquiry.status}</td>
              <td>{enquiry.lab.name}</td>
              <td>{'Yes' if enquiry.escalated else 'No'}</td>
              <td>
                <a href=\"{url_for('enquiries.update', enquiry_id=enquiry.id)}\" class=\"btn btn-sm btn-outline-primary\">Update</a>
              </td>
            </tr>
            """
            return jsonify(success=True, message=f"Enquiry created with tracking {enquiry.tracking_number}.", row_html=row_html, reload=False, reset=True)
        flash(f"Enquiry created with tracking {enquiry.tracking_number}.", "success")
    else:
        errors = "; ".join(
            [f"{field}: {', '.join(messages)}" for field, messages in form.errors.items()]
        )
        if request.is_json:
            return jsonify(success=False, message=f"Unable to submit enquiry. {errors}"), 400
        flash("Unable to submit enquiry. Please check the form.", "danger")
    return redirect(url_for("enquiries.index"))


@enquiries_bp.route("/update/<int:enquiry_id>", methods=["GET", "POST"])
@login_required
def update(enquiry_id):
    enquiry = Enquiry.query.get_or_404(enquiry_id)
    if current_user.role not in ["Admin", "HQ Trainee"] and current_user.role != "Lab Trainee":
        abort(403)
    if current_user.role == "Lab Trainee" and enquiry.lab_id != current_user.assigned_lab_id:
        abort(403)
    payload = request.get_json() if request.is_json else None
    form = UpdateEnquiryForm(obj=enquiry, data=payload) if payload else UpdateEnquiryForm(obj=enquiry)
    if form.validate_on_submit():
        update_enquiry_status(
            enquiry,
            status=form.status.data,
            resolution_note=form.resolution_note.data,
            escalated=form.status.data == "Escalated",
        )
        if request.is_json:
            return jsonify(success=True, message="Enquiry status updated successfully.", redirect=url_for("enquiries.index"))
        flash("Enquiry status updated successfully.", "success")
        return redirect(url_for("enquiries.index"))
    return render_template("enquiries/update.html", form=form, enquiry=enquiry)


@enquiries_bp.route("/track", methods=["GET", "POST"])
def track():
    form = TrackingForm()
    enquiry = None
    if form.validate_on_submit():
        enquiry = Enquiry.query.filter_by(tracking_number=form.tracking_number.data.strip()).first()
        if not enquiry:
            flash("No enquiry found with that tracking number.", "danger")
    return render_template("enquiries/track.html", form=form, enquiry=enquiry)


@enquiries_bp.route("/<int:enquiry_id>/delete", methods=["POST"])
@login_required
def delete(enquiry_id):
    enquiry = Enquiry.query.get_or_404(enquiry_id)
    if current_user.role == "Lab Trainee" and enquiry.lab_id != current_user.assigned_lab_id:
        abort(403)
    db.session.delete(enquiry)
    db.session.commit()
    flash("Enquiry deleted successfully.", "success")
    return redirect(url_for("enquiries.index"))
