from app.extensions import db
from app.models.province import Province
from app.models.lab import Lab
from app.models.user import User
from app.utils import generate_secure_password


def create_province(name: str) -> Province:
    province = Province(name=name.strip())
    db.session.add(province)
    db.session.commit()
    return province


def update_province(province: Province, name: str) -> Province:
    province.name = name.strip()
    db.session.commit()
    return province


def delete_province(province: Province) -> None:
    db.session.delete(province)
    db.session.commit()


def create_lab(name: str, province_id: int, latitude: float, longitude: float, radius_meters: float) -> Lab:
    lab = Lab(
        name=name.strip(),
        province_id=province_id,
        latitude=latitude,
        longitude=longitude,
        radius_meters=radius_meters,
    )
    db.session.add(lab)
    db.session.commit()
    return lab


def update_lab(lab: Lab, name: str, province_id: int, latitude: float, longitude: float, radius_meters: float) -> Lab:
    lab.name = name.strip()
    lab.province_id = province_id
    lab.latitude = latitude
    lab.longitude = longitude
    lab.radius_meters = radius_meters
    db.session.commit()
    return lab


def delete_lab(lab: Lab) -> None:
    db.session.delete(lab)
    db.session.commit()


def create_user(
    full_name: str,
    email: str,
    role: str,
    assigned_lab_id: int = None,
    active: bool = True,
    staff_number: str = None,
):
    password = generate_secure_password()
    user = User(
        full_name=full_name.strip(),
        staff_number=staff_number.strip() if staff_number else None,
        email=email.strip().lower(),
        role=role,
        assigned_lab_id=assigned_lab_id if assigned_lab_id else None,
        active=active,
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user, password


def update_user(
    user: User,
    full_name: str,
    email: str,
    role: str,
    assigned_lab_id: int = None,
    active: bool = True,
    staff_number: str = None,
) -> User:
    user.full_name = full_name.strip()
    user.staff_number = staff_number.strip() if staff_number else None
    user.email = email.strip().lower()
    user.role = role
    user.assigned_lab_id = assigned_lab_id if assigned_lab_id else None
    user.active = active
    db.session.commit()
    return user


def delete_user(user: User) -> None:
    db.session.delete(user)
    db.session.commit()


def reset_user_password(user: User) -> str:
    password = generate_secure_password()
    user.set_password(password)
    db.session.commit()
    return password


def assign_user_lab(user: User, lab_id: int):
    user.assigned_lab_id = lab_id
    db.session.commit()
    return user
