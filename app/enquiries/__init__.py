from flask import Blueprint

enquiries_bp = Blueprint("enquiries", __name__, template_folder="templates", url_prefix="/enquiries")

from . import routes
