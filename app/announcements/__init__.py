from flask import Blueprint

announcements_bp = Blueprint("announcements", __name__, template_folder="templates", url_prefix="/announcements")

from . import routes
