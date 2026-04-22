from pathlib import Path
from uuid import uuid4
from flask import render_template, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.announcements import announcements_bp
from app.announcements.forms import AnnouncementForm
from app.announcements.services import create_announcement
from app.models.announcement import Announcement
from app.utils import role_required


@announcements_bp.route("/manage")
@login_required
@role_required("Admin", "HQ Trainee")
def manage():

    announcements = Announcement.query.order_by(Announcement.created_at.desc()).all()
    form = AnnouncementForm()
    return render_template("announcements/manage.html", announcements=announcements, form=form)


@announcements_bp.route("/create", methods=["POST"])
@login_required
@role_required("Admin", "HQ Trainee")
def create():

    form = AnnouncementForm()
    if form.validate_on_submit():
        poster_filename = None
        poster = form.poster.data
        if poster and getattr(poster, "filename", ""):
            uploads_dir = Path(current_app.config["UPLOAD_FOLDER"]) / "announcements"
            uploads_dir.mkdir(parents=True, exist_ok=True)
            safe_name = secure_filename(poster.filename)
            extension = Path(safe_name).suffix.lower() or ".png"
            poster_filename = f"{uuid4().hex}{extension}"
            poster.save(uploads_dir / poster_filename)

        announcement = create_announcement(
            title=form.title.data,
            message=form.message.data,
            expiry_date=form.expiry_date.data,
            created_by=current_user.id,
            poster_filename=poster_filename,
        )
        flash("Announcement published successfully.", "success")
    else:
        errors = "; ".join(
            [f"{field}: {', '.join(messages)}" for field, messages in form.errors.items()]
        )
        flash("Unable to publish announcement. Please check the form.", "danger")
    return redirect(url_for("announcements.manage"))


@announcements_bp.route("/poster/<path:filename>")
def poster(filename):
    directory = Path(current_app.config["UPLOAD_FOLDER"]) / "announcements"
    return send_from_directory(directory, filename)
