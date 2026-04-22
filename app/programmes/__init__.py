from flask import Blueprint

programmes_bp = Blueprint("programmes", __name__, template_folder="templates", url_prefix="/programmes")

from . import routes
