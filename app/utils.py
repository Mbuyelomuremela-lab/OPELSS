import math
import random
import string
from functools import wraps
from flask import abort, flash, redirect, request, url_for
from flask_login import current_user


def generate_secure_password(length: int = 7) -> str:
    symbols = "@_#"
    alphabet = string.ascii_letters + string.digits + symbols
    password = [random.choice(string.ascii_uppercase), random.choice(string.ascii_lowercase), random.choice(string.digits), random.choice(symbols)]
    password += [random.choice(alphabet) for _ in range(max(length - 4, 2))]
    random.shuffle(password)
    return "".join(password)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius * c


def role_required(*allowed_roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("auth.login", next=request.path))

            if current_user.role not in allowed_roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def lab_trainee_required(view):
    return role_required("Lab Trainee")(view)


def hq_required(view):
    return role_required("HQ Trainee", "Admin")(view)
