from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from app.enquiries import enquiries_bp
from app.enquiries.forms import (
    EnquiryForm, AssignEnquiryForm, ResolveEnquiryForm, NotResolvedForm, TrackingForm
)
from app.enquiries.services import (
    create_enquiry, assign_enquiry, start_progress,
    resolve_enquiry, mark_not_resolved, close_enquiry, reassign_enquiry,
)
from app.audit.services import log_activity
from app.models.enquiry import Enquiry
from app.models.lab import Lab
from app.models.user import User
from app.extensions import db


def _hq_users():
    return User.query.filter(
        User.role.in_(["Admin", "HQ Trainee"]),
        User.active == True,
    ).order_by(User.full_name).all()


def _json_str(data, key):
    return (data.get(key) or "").strip()


def _json_int(data, key):
    try:
        return int(data.get(key))
    except (TypeError, ValueError):
        return None


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

    assign_form = AssignEnquiryForm()
    assign_form.assigned_to.choices = [(u.id, u.full_name) for u in _hq_users()]

    resolve_form = ResolveEnquiryForm()
    not_resolved_form = NotResolvedForm()

    return render_template(
        "enquiries/index.html",
        enquiries=enquiries,
        form=form,
        assign_form=assign_form,
        resolve_form=resolve_form,
        not_resolved_form=not_resolved_form,
        labs=labs,
    )


@enquiries_bp.route("/create", methods=["POST"])
@login_required
def create():
    if current_user.role != "Lab Trainee":
        abort(403)
    if not current_user.assigned_lab_id:
        if request.is_json:
            return jsonify(success=False, message="No lab is assigned to your account."), 400
        flash("No lab is assigned to your account.", "warning")
        return redirect(url_for("enquiries.index"))

    if request.is_json:
        data = request.get_json() or {}
        student_name = _json_str(data, "student_name")
        student_number = _json_str(data, "student_number")
        category = _json_str(data, "category")
        description = _json_str(data, "description")
        escalation_reason = _json_str(data, "escalation_reason")

        errors = []
        if not student_name:      errors.append("Student name is required")
        if not student_number:    errors.append("Student number is required")
        if not category:          errors.append("Category is required")
        if not description:       errors.append("Description is required")
        if not escalation_reason: errors.append("Escalation reason is required")
        if errors:
            return jsonify(success=False, message="; ".join(errors)), 400

        enquiry = create_enquiry(
            student_name=student_name,
            student_number=student_number,
            category=category,
            description=description,
            lab_id=current_user.assigned_lab_id,
            escalation_reason=escalation_reason,
        )
        log_activity("created", "enquiry", f"{enquiry.tracking_number} ({enquiry.student_name})", enquiry.id)
        return jsonify(
            success=True,
            message="Enquiry submitted and escalated to HQ.",
            tracking_number=enquiry.tracking_number,
            student_name=enquiry.student_name,
            reload=True,
        )

    labs = Lab.query.order_by(Lab.name).all()
    form = EnquiryForm()
    form.lab_id.choices = [(lab.id, f"{lab.name} ({lab.province.name})") for lab in labs]
    if form.validate_on_submit():
        enquiry = create_enquiry(
            student_name=form.student_name.data,
            student_number=form.student_number.data,
            category=form.category.data,
            description=form.description.data,
            lab_id=current_user.assigned_lab_id,
            escalation_reason=form.escalation_reason.data,
        )
        log_activity("created", "enquiry", f"{enquiry.tracking_number} ({enquiry.student_name})", enquiry.id)
        flash(f"Enquiry {enquiry.tracking_number} submitted and escalated to HQ.", "success")
    else:
        flash("Unable to submit enquiry. Please check the form.", "danger")
    return redirect(url_for("enquiries.index"))


@enquiries_bp.route("/<int:enquiry_id>/assign", methods=["POST"])
@login_required
def assign(enquiry_id):
    if current_user.role != "Admin":
        abort(403)
    enquiry = Enquiry.query.get_or_404(enquiry_id)
    if enquiry.status not in ("Open", "Not Resolved"):
        if request.is_json:
            return jsonify(success=False, message="This enquiry cannot be assigned at its current status."), 400
        flash("This enquiry cannot be assigned at its current status.", "warning")
        return redirect(url_for("enquiries.index"))

    if request.is_json:
        data = request.get_json() or {}
        assigned_to = _json_int(data, "assigned_to")
        if not assigned_to:
            return jsonify(success=False, message="Please select a person to assign to."), 400
        assign_enquiry(enquiry, assigned_to=assigned_to, assigned_by=current_user.id)
        log_activity("assigned", "enquiry", f"{enquiry.tracking_number} ({enquiry.student_name})", enquiry.id)
        return jsonify(success=True, message="Enquiry assigned successfully.", reload=True)

    form = AssignEnquiryForm()
    form.assigned_to.choices = [(u.id, u.full_name) for u in _hq_users()]
    if form.validate_on_submit():
        assign_enquiry(enquiry, assigned_to=form.assigned_to.data, assigned_by=current_user.id)
        log_activity("assigned", "enquiry", f"{enquiry.tracking_number} ({enquiry.student_name})", enquiry.id)
        flash("Enquiry assigned successfully.", "success")
    else:
        flash("Invalid assignment.", "danger")
    return redirect(url_for("enquiries.index"))


@enquiries_bp.route("/<int:enquiry_id>/start", methods=["POST"])
@login_required
def start(enquiry_id):
    if current_user.role not in ("Admin", "HQ Trainee"):
        abort(403)
    enquiry = Enquiry.query.get_or_404(enquiry_id)
    if enquiry.assigned_to != current_user.id and current_user.role != "Admin":
        abort(403)
    if enquiry.status != "Assigned":
        if request.is_json:
            return jsonify(success=False, message="Enquiry must be Assigned before starting."), 400
        flash("Enquiry must be in Assigned status to start.", "warning")
        return redirect(url_for("enquiries.index"))
    start_progress(enquiry)
    log_activity("started", "enquiry", f"{enquiry.tracking_number} ({enquiry.student_name})", enquiry.id)
    if request.is_json:
        return jsonify(success=True, message="Enquiry marked as In Progress.", reload=True)
    flash("Enquiry marked as In Progress.", "success")
    return redirect(url_for("enquiries.index"))


@enquiries_bp.route("/<int:enquiry_id>/resolve", methods=["POST"])
@login_required
def resolve(enquiry_id):
    if current_user.role not in ("Admin", "HQ Trainee"):
        abort(403)
    enquiry = Enquiry.query.get_or_404(enquiry_id)
    if enquiry.assigned_to != current_user.id and current_user.role != "Admin":
        abort(403)
    if enquiry.status != "In Progress":
        if request.is_json:
            return jsonify(success=False, message="Enquiry must be In Progress to resolve."), 400
        flash("Enquiry must be In Progress to resolve.", "warning")
        return redirect(url_for("enquiries.index"))

    if request.is_json:
        data = request.get_json() or {}
        note = _json_str(data, "resolution_note")
        if not note:
            return jsonify(success=False, message="Resolution note is required."), 400
        resolve_enquiry(enquiry, resolution_note=note)
        log_activity("resolved", "enquiry", f"{enquiry.tracking_number} ({enquiry.student_name})", enquiry.id)
        return jsonify(success=True, message="Enquiry marked as Resolved.", reload=True)

    form = ResolveEnquiryForm()
    if form.validate_on_submit():
        resolve_enquiry(enquiry, resolution_note=form.resolution_note.data)
        log_activity("resolved", "enquiry", f"{enquiry.tracking_number} ({enquiry.student_name})", enquiry.id)
        flash("Enquiry marked as Resolved.", "success")
    else:
        flash("Resolution note is required.", "danger")
    return redirect(url_for("enquiries.index"))


@enquiries_bp.route("/<int:enquiry_id>/not-resolved", methods=["POST"])
@login_required
def not_resolved(enquiry_id):
    if current_user.role not in ("Admin", "HQ Trainee"):
        abort(403)
    enquiry = Enquiry.query.get_or_404(enquiry_id)
    if enquiry.assigned_to != current_user.id and current_user.role != "Admin":
        abort(403)
    if enquiry.status != "In Progress":
        if request.is_json:
            return jsonify(success=False, message="Enquiry must be In Progress to mark as not resolved."), 400
        flash("Enquiry must be In Progress to mark as not resolved.", "warning")
        return redirect(url_for("enquiries.index"))

    if request.is_json:
        data = request.get_json() or {}
        reason = _json_str(data, "not_resolved_reason")
        if not reason:
            return jsonify(success=False, message="Reason is required."), 400
        mark_not_resolved(enquiry, not_resolved_reason=reason)
        log_activity("not_resolved", "enquiry", f"{enquiry.tracking_number} ({enquiry.student_name})", enquiry.id)
        return jsonify(success=True, message="Enquiry marked as Not Resolved.", reload=True)

    form = NotResolvedForm()
    if form.validate_on_submit():
        mark_not_resolved(enquiry, not_resolved_reason=form.not_resolved_reason.data)
        log_activity("not_resolved", "enquiry", f"{enquiry.tracking_number} ({enquiry.student_name})", enquiry.id)
        flash("Enquiry marked as Not Resolved.", "success")
    else:
        flash("Reason is required.", "danger")
    return redirect(url_for("enquiries.index"))


@enquiries_bp.route("/<int:enquiry_id>/close", methods=["POST"])
@login_required
def close(enquiry_id):
    if current_user.role != "Admin":
        abort(403)
    enquiry = Enquiry.query.get_or_404(enquiry_id)
    close_enquiry(enquiry, closed_by=current_user.id)
    log_activity("closed", "enquiry", f"{enquiry.tracking_number} ({enquiry.student_name})", enquiry.id)
    if request.is_json:
        return jsonify(success=True, message="Enquiry closed.", reload=True)
    flash("Enquiry closed.", "success")
    return redirect(url_for("enquiries.index"))


@enquiries_bp.route("/<int:enquiry_id>/reopen", methods=["POST"])
@login_required
def reopen(enquiry_id):
    if current_user.role != "Admin":
        abort(403)
    enquiry = Enquiry.query.get_or_404(enquiry_id)
    if enquiry.status != "Closed":
        if request.is_json:
            return jsonify(success=False, message="Only Closed enquiries can be reopened."), 400
        flash("Only Closed enquiries can be reopened.", "warning")
        return redirect(url_for("enquiries.index"))
    enquiry.status = "Open"
    enquiry.closed_by = None
    enquiry.closed_at = None
    db.session.commit()
    log_activity("reopened", "enquiry", f"{enquiry.tracking_number} ({enquiry.student_name})", enquiry.id)
    if request.is_json:
        return jsonify(success=True, message="Enquiry reopened.", reload=True)
    flash("Enquiry reopened.", "success")
    return redirect(url_for("enquiries.index"))


@enquiries_bp.route("/<int:enquiry_id>/reassign", methods=["POST"])
@login_required
def reassign(enquiry_id):
    if current_user.role != "Admin":
        abort(403)
    enquiry = Enquiry.query.get_or_404(enquiry_id)
    if enquiry.status != "Not Resolved":
        if request.is_json:
            return jsonify(success=False, message="Only Not Resolved enquiries can be reassigned."), 400
        flash("Only Not Resolved enquiries can be reassigned.", "warning")
        return redirect(url_for("enquiries.index"))

    if request.is_json:
        data = request.get_json() or {}
        assigned_to = _json_int(data, "assigned_to")
        if not assigned_to:
            return jsonify(success=False, message="Please select a person to reassign to."), 400
        reassign_enquiry(enquiry, assigned_to=assigned_to, assigned_by=current_user.id)
        log_activity("reassigned", "enquiry", f"{enquiry.tracking_number} ({enquiry.student_name})", enquiry.id)
        return jsonify(success=True, message="Enquiry reassigned.", reload=True)

    form = AssignEnquiryForm()
    form.assigned_to.choices = [(u.id, u.full_name) for u in _hq_users()]
    if form.validate_on_submit():
        reassign_enquiry(enquiry, assigned_to=form.assigned_to.data, assigned_by=current_user.id)
        log_activity("reassigned", "enquiry", f"{enquiry.tracking_number} ({enquiry.student_name})", enquiry.id)
        flash("Enquiry reassigned.", "success")
    else:
        flash("Invalid reassignment.", "danger")
    return redirect(url_for("enquiries.index"))


@enquiries_bp.route("/<int:enquiry_id>/delete", methods=["POST"])
@login_required
def delete(enquiry_id):
    enquiry = Enquiry.query.get_or_404(enquiry_id)
    if current_user.role != "Lab Trainee":
        abort(403)
    if enquiry.lab_id != current_user.assigned_lab_id:
        abort(403)
    if enquiry.status != "Open":
        flash("Enquiry cannot be deleted once it has been assigned.", "warning")
        return redirect(url_for("enquiries.index"))
    label, entity_id = f"{enquiry.tracking_number} ({enquiry.student_name})", enquiry.id
    db.session.delete(enquiry)
    db.session.commit()
    log_activity("deleted", "enquiry", label, entity_id)
    flash("Enquiry deleted successfully.", "success")
    return redirect(url_for("enquiries.index"))


@enquiries_bp.route("/<int:enquiry_id>/edit", methods=["POST"])
@login_required
def edit(enquiry_id):
    if current_user.role != "Lab Trainee":
        abort(403)
    enquiry = Enquiry.query.get_or_404(enquiry_id)
    if enquiry.lab_id != current_user.assigned_lab_id:
        abort(403)
    if enquiry.status != "Open":
        flash("Enquiry cannot be edited once it has been assigned.", "warning")
        return redirect(url_for("enquiries.index"))

    if request.is_json:
        data = request.get_json() or {}
        student_name = _json_str(data, "student_name")
        student_number = _json_str(data, "student_number")
        category = _json_str(data, "category")
        description = _json_str(data, "description")
        escalation_reason = _json_str(data, "escalation_reason")

        errors = []
        if not student_name:      errors.append("Student name is required")
        if not student_number:    errors.append("Student number is required")
        if not category:          errors.append("Category is required")
        if not description:       errors.append("Description is required")
        if not escalation_reason: errors.append("Escalation reason is required")
        if errors:
            return jsonify(success=False, message="; ".join(errors)), 400

        enquiry.student_name = student_name
        enquiry.student_number = student_number
        enquiry.category = category
        enquiry.description = description
        enquiry.escalation_reason = escalation_reason
        db.session.commit()
        log_activity("updated", "enquiry", f"{enquiry.tracking_number} ({enquiry.student_name})", enquiry.id)
        return jsonify(success=True, message="Enquiry updated successfully.", reload=True)

    labs = Lab.query.order_by(Lab.name).all()
    form = EnquiryForm()
    form.lab_id.choices = [(lab.id, f"{lab.name} ({lab.province.name})") for lab in labs]
    if form.validate_on_submit():
        enquiry.student_name = form.student_name.data.strip()
        enquiry.student_number = form.student_number.data.strip()
        enquiry.category = form.category.data.strip()
        enquiry.description = form.description.data.strip()
        enquiry.escalation_reason = form.escalation_reason.data.strip()
        db.session.commit()
        log_activity("updated", "enquiry", f"{enquiry.tracking_number} ({enquiry.student_name})", enquiry.id)
        flash("Enquiry updated successfully.", "success")
    else:
        flash("Unable to update enquiry.", "danger")
    return redirect(url_for("enquiries.index"))


@enquiries_bp.route("/track", methods=["GET", "POST"])
def track():
    form = TrackingForm()
    enquiry = None
    if form.validate_on_submit():
        enquiry = Enquiry.query.filter_by(tracking_number=form.tracking_number.data.strip()).first()
        if not enquiry:
            flash("No enquiry found with that tracking number.", "danger")
    return render_template("enquiries/track.html", form=form, enquiry=enquiry)
