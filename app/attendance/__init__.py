from flask import Blueprint

attendance_bp = Blueprint("attendance", __name__, template_folder="templates", url_prefix="/attendance")

from . import routes
