from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from .forms import LoginForm, PasswordResetForm
from .services import authenticate_user, reset_password
from app.models.announcement import Announcement
from app.models.province import Province
from app.utils import sast_today
from sqlalchemy.orm import joinedload


@auth_bp.route("/")
def landing():
    announcements = Announcement.query.filter(Announcement.expiry_date >= sast_today()).order_by(Announcement.created_at.desc()).all()
    provinces = Province.query.options(joinedload(Province.labs)).order_by(Province.name).all()
    form = LoginForm()
    return render_template("landing.html", announcements=announcements, provinces=provinces)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user, error = authenticate_user(
            email=form.email.data,
            password=form.password.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
        )
        if error:
            flash(error, "danger")
        else:
            login_user(user)
            flash("Welcome back, {}.".format(user.full_name), "success")
            next_page = request.args.get("next") or url_for("dashboard.home")
            return redirect(next_page)

    return render_template("login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/reset-password", methods=["GET", "POST"])
@login_required
def reset_password_handler():
    form = PasswordResetForm()
    if form.validate_on_submit():
        success, message = reset_password(current_user, form.current_password.data, form.new_password.data)
        flash(message, "success" if success else "danger")
        if success:
            return redirect(url_for("dashboard.home"))

    return render_template("reset_password.html", form=form)
