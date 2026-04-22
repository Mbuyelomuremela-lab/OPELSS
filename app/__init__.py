from pathlib import Path
from flask import Flask
from flask_login import current_user
from config import Config
from app.extensions import db, migrate, login_manager, csrf


def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    instance_dir = Path(app.root_path).parent / "instance"
    instance_dir.mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from app.auth import auth_bp
    from app.admin import admin_bp
    from app.dashboard import dashboard_bp
    from app.attendance import attendance_bp
    from app.assets import assets_bp
    from app.visitors import visitors_bp
    from app.enquiries import enquiries_bp
    from app.programmes import programmes_bp
    from app.announcements import announcements_bp
    from app.reports import reports_bp

    blueprints = [
        auth_bp,
        admin_bp,
        dashboard_bp,
        attendance_bp,
        assets_bp,
        visitors_bp,
        enquiries_bp,
        programmes_bp,
        announcements_bp,
        reports_bp,
    ]

    for bp in blueprints:
        app.register_blueprint(bp)

    @app.context_processor
    def inject_role_flags():
        role = current_user.role if getattr(current_user, "is_authenticated", False) else None
        return {
            "is_hq_admin": role in ["Admin", "HQ Trainee"],
            "is_trainee": role == "Lab Trainee",
        }

    _ensure_runtime_schema_columns(app)

    return app


def _ensure_runtime_schema_columns(app: Flask) -> None:
    # Existing project migrations are incomplete; keep critical additive columns in sync.
    with app.app_context():
        try:
            with db.engine.begin() as conn:
                user_columns = {row[1] for row in conn.exec_driver_sql("PRAGMA table_info(users)").fetchall()}
                if "staff_number" not in user_columns:
                    conn.exec_driver_sql("ALTER TABLE users ADD COLUMN staff_number VARCHAR(8)")
                announcement_columns = {
                    row[1] for row in conn.exec_driver_sql("PRAGMA table_info(announcements)").fetchall()
                }
                if "poster_filename" not in announcement_columns:
                    conn.exec_driver_sql("ALTER TABLE announcements ADD COLUMN poster_filename VARCHAR(255)")
        except Exception:
            # App should remain bootable even when database is mounted read-only.
            pass


def seed_data():
    from app.models.user import User
    from app.models.province import Province
    from app.models.lab import Lab

    province = Province.query.first()
    if not province:
        province = Province(name="Headquarters")
        db.session.add(province)
        db.session.commit()

    if not Lab.query.first():
        lab = Lab(
            name="Main Lab",
            province_id=province.id,
            latitude=0.0,
            longitude=0.0,
            radius_meters=1000,
        )
        db.session.add(lab)
        db.session.commit()
    else:
        lab = Lab.query.first()

    if not User.query.filter_by(email="admin@opelss.com").first():
        admin = User(
            full_name="System Admin",
            email="admin@opelss.com",
            role="Admin",
            active=True,
            assigned_lab_id=lab.id if lab else None,
        )
        admin.set_password("Admin@123")
        db.session.add(admin)
        db.session.commit()
