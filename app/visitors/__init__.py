from flask import Blueprint

visitors_bp = Blueprint("visitors", __name__, template_folder="templates", url_prefix="/visitors")

from . import routes
