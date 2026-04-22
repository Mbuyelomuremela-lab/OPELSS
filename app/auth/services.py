from app.extensions import db
from app.models.user import User
from app.utils import generate_secure_password, haversine_distance


def authenticate_user(email: str, password: str, latitude: str = None, longitude: str = None):
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return None, "Invalid email or password."

    if not user.active:
        return None, "Your account is inactive. Contact an administrator."

    if user.role == "Lab Trainee":
        if not (latitude and longitude):
            return None, "Geolocation is required for lab trainee login."

        try:
            lat = float(latitude)
            lon = float(longitude)
        except ValueError:
            return None, "Unable to read your location. Please enable geolocation."

        lab = user.assigned_lab
        if not lab:
            return None, "You are not yet assigned to a lab."

        distance = haversine_distance(lat, lon, lab.latitude, lab.longitude)
        if distance > lab.radius_meters:
            return None, "You must be inside your assigned lab radius to log in."

    return user, None


def reset_password(user: User, current_password: str, new_password: str):
    if not user.check_password(current_password):
        return False, "Current password is incorrect."

    user.set_password(new_password)
    db.session.commit()
    return True, "Password updated successfully."


def generate_password_for_new_user():
    return generate_secure_password()
