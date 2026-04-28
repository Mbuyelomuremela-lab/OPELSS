from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required
from app.admin import admin_bp
from app.admin.forms import ProvinceForm, LabForm, UserForm
from app.admin.services import (
    create_province,
    create_lab,
    create_user,
    update_province,
    update_lab,
    update_user,
    delete_province,
    delete_lab,
    delete_user,
    reset_user_password,
)
from app.models.province import Province
from app.models.lab import Lab
from app.models.user import User
from app.utils import role_required


@admin_bp.route("/")
@login_required
@role_required("Admin")
def index():
    provinces = Province.query.order_by(Province.name).all()
    labs = Lab.query.order_by(Lab.name).all()
    users = User.query.order_by(User.full_name).all()
    province_form = ProvinceForm()
    lab_form = LabForm()
    user_form = UserForm()
    lab_form.province_id.choices = [(p.id, p.name) for p in provinces]
    user_form.assigned_lab_id.choices = [(0, "Unassigned")] + [(l.id, f"{l.name} ({l.province.name})") for l in labs]
    return render_template(
        "admin/dashboard.html",
        provinces=provinces,
        labs=labs,
        users=users,
        province_form=province_form,
        lab_form=lab_form,
        user_form=user_form,
    )


@admin_bp.route("/provinces", methods=["POST"])
@login_required
@role_required("Admin")
def add_province():
    form = ProvinceForm()
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    
    if form.validate_on_submit():
        create_province(form.name.data)
        message = "Province added successfully."
        if is_ajax:
            return jsonify({"success": True, "message": message})
        flash(message, "success")
    else:
        message = "Unable to add province. Check the values and try again."
        if is_ajax:
            return jsonify({"success": False, "error": message}), 400
        flash(message, "danger")
    
    return redirect(url_for("admin.index"))


@admin_bp.route("/labs", methods=["POST"])
@login_required
@role_required("Admin")
def add_lab():
    form = LabForm()
    form.province_id.choices = [(p.id, p.name) for p in Province.query.order_by(Province.name).all()]
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    
    if form.validate_on_submit():
        create_lab(
            name=form.name.data,
            province_id=form.province_id.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            radius_meters=form.radius_meters.data,
        )
        message = "Lab created successfully."
        if is_ajax:
            return jsonify({"success": True, "message": message})
        flash(message, "success")
    else:
        message = "Unable to create lab. Please check the values."
        if is_ajax:
            return jsonify({"success": False, "error": message}), 400
        flash(message, "danger")
    
    return redirect(url_for("admin.index"))


@admin_bp.route("/users", methods=["POST"])
@login_required
@role_required("Admin")
def add_user():
    form = UserForm()
    form.assigned_lab_id.choices = [(0, "Unassigned")] + [
        (l.id, f"{l.name} ({l.province.name})") for l in Lab.query.order_by(Lab.name).all()
    ]
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    
    if form.validate_on_submit():
        staff_number = (form.staff_number.data or "").strip() or None
        if staff_number and User.query.filter_by(staff_number=staff_number).first():
            error = "Another user already uses this staff number."
            if is_ajax:
                return jsonify({"success": False, "error": error}), 400
            flash(error, "danger")
            return redirect(url_for("admin.index"))
        
        assigned_lab = form.assigned_lab_id.data or None
        if form.role.data == "Lab Trainee" and not assigned_lab:
            error = "Lab Trainee users must be assigned to a lab."
            if is_ajax:
                return jsonify({"success": False, "error": error}), 400
            flash(error, "danger")
            return redirect(url_for("admin.index"))
        
        user, password = create_user(
            full_name=form.full_name.data,
            email=form.email.data,
            role=form.role.data,
            assigned_lab_id=assigned_lab,
            active=form.active.data,
            staff_number=staff_number,
        )
        
        if is_ajax:
            return jsonify({
                "success": True,
                "message": "User created successfully.",
                "temporary_password": password
            })
        
        flash(f"User created. Temporary password: {password}", "success")
    else:
        error = "Unable to create user. Please check the provided details."
        if is_ajax:
            return jsonify({"success": False, "error": error}), 400
        flash(error, "danger")
    
    return redirect(url_for("admin.index"))


@admin_bp.route("/provinces/<int:province_id>/update", methods=["POST"])
@login_required
@role_required("Admin")
def edit_province(province_id):
    province = Province.query.get_or_404(province_id)
    name = (request.form.get("name") or "").strip()
    if not name:
        flash("Province name is required.", "danger")
        return redirect(url_for("admin.index"))

    duplicate = Province.query.filter(Province.id != province.id, Province.name.ilike(name)).first()
    if duplicate:
        flash("A province with this name already exists.", "danger")
        return redirect(url_for("admin.index"))

    update_province(province, name)
    flash("Province updated successfully.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/provinces/<int:province_id>/delete", methods=["POST"])
@login_required
@role_required("Admin")
def remove_province(province_id):
    province = Province.query.get_or_404(province_id)
    if province.labs:
        flash("Cannot delete province with linked labs. Reassign or delete labs first.", "danger")
        return redirect(url_for("admin.index"))
    delete_province(province)
    flash("Province deleted successfully.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/labs/<int:lab_id>/update", methods=["POST"])
@login_required
@role_required("Admin")
def edit_lab(lab_id):
    lab = Lab.query.get_or_404(lab_id)
    name = (request.form.get("name") or "").strip()
    province_id = request.form.get("province_id", type=int)
    latitude = request.form.get("latitude", type=float)
    longitude = request.form.get("longitude", type=float)
    radius_meters = request.form.get("radius_meters", type=float)

    if not all([name, province_id is not None, latitude is not None, longitude is not None, radius_meters is not None]):
        flash("All lab fields are required.", "danger")
        return redirect(url_for("admin.index"))

    if not Province.query.get(province_id):
        flash("Selected province does not exist.", "danger")
        return redirect(url_for("admin.index"))

    duplicate = Lab.query.filter(Lab.id != lab.id, Lab.name.ilike(name)).first()
    if duplicate:
        flash("A lab with this name already exists.", "danger")
        return redirect(url_for("admin.index"))

    update_lab(lab, name, province_id, latitude, longitude, radius_meters)
    flash("Lab updated successfully.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/labs/<int:lab_id>/delete", methods=["POST"])
@login_required
@role_required("Admin")
def remove_lab(lab_id):
    lab = Lab.query.get_or_404(lab_id)
    if any([lab.users, lab.attendance_logs, lab.assets, lab.visitors, lab.enquiries, lab.programmes]):
        flash("Cannot delete lab with linked records. Move or clear dependencies first.", "danger")
        return redirect(url_for("admin.index"))
    delete_lab(lab)
    flash("Lab deleted successfully.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/users/<int:user_id>/update", methods=["POST"])
@login_required
@role_required("Admin")
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    full_name = (request.form.get("full_name") or "").strip()
    email = (request.form.get("email") or "").strip().lower()
    role = request.form.get("role")
    staff_number = (request.form.get("staff_number") or "").strip() or None
    assigned_lab_id = request.form.get("assigned_lab_id", type=int) or None
    active = request.form.get("active") == "on"

    if not full_name or not email or role not in ["Admin", "HQ Trainee", "Lab Trainee"]:
        flash("Invalid user details provided.", "danger")
        return redirect(url_for("admin.index"))

    email_exists = User.query.filter(User.id != user.id, User.email == email).first()
    if email_exists:
        flash("Another user already uses this email address.", "danger")
        return redirect(url_for("admin.index"))

    if staff_number:
        if len(staff_number) != 8 or not staff_number.isdigit():
            flash("Staff number must be exactly 8 digits.", "danger")
            return redirect(url_for("admin.index"))
        duplicate_staff = User.query.filter(User.id != user.id, User.staff_number == staff_number).first()
        if duplicate_staff:
            flash("Another user already uses this staff number.", "danger")
            return redirect(url_for("admin.index"))

    if role == "Lab Trainee" and not assigned_lab_id:
        flash("Lab Trainee users must be assigned to a lab.", "danger")
        return redirect(url_for("admin.index"))

    update_user(
        user,
        full_name=full_name,
        email=email,
        role=role,
        assigned_lab_id=assigned_lab_id,
        active=active,
        staff_number=staff_number,
    )
    flash("User updated successfully.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@role_required("Admin")
def remove_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == "Admin" and User.query.filter_by(role="Admin").count() <= 1:
        flash("Cannot delete the last admin user.", "danger")
        return redirect(url_for("admin.index"))
    delete_user(user)
    flash("User deleted successfully.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/users/<int:user_id>/reset-password", methods=["POST"])
@login_required
@role_required("Admin")
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    password = reset_user_password(user)
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    
    message = f"Password reset successfully for {user.full_name}."
    
    if is_ajax:
        return jsonify({
            "success": True,
            "message": message,
            "temporary_password": password
        })
    
    flash(f"Password reset successfully. Temporary password for {user.full_name}: {password}", "success")
    return redirect(url_for("admin.index"))
