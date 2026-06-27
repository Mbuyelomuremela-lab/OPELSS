from pathlib import Path
from flask import Flask
from flask_login import current_user
from config import Config
from app.extensions import db, migrate, login_manager, csrf

# Import models so SQLAlchemy registers all tables during app startup.
from app import models  # noqa: F401


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
    from app.audit import audit_bp

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
        audit_bp,
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

    with app.app_context():
        db.create_all()
        seed_data()

    _ensure_runtime_schema_columns(app)

    return app


def _ensure_runtime_schema_columns(app: Flask) -> None:
    # Keeps critical additive columns in sync across SQLite (dev) and PostgreSQL (prod).
    with app.app_context():
        try:
            dialect = db.engine.dialect.name  # "sqlite" or "postgresql"

            def existing_columns(table: str) -> set:
                if dialect == "sqlite":
                    rows = conn.exec_driver_sql(f"PRAGMA table_info({table})").fetchall()
                    return {row[1] for row in rows}
                else:
                    rows = conn.exec_driver_sql(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_name = :t", {"t": table}
                    ).fetchall()
                    return {row[0] for row in rows}

            def add_column(table: str, col: str, col_type: str) -> None:
                conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")

            with db.engine.begin() as conn:
                user_cols = existing_columns("users")
                if "staff_number" not in user_cols:
                    add_column("users", "staff_number", "VARCHAR(8)")

                ann_cols = existing_columns("announcements")
                if "poster_filename" not in ann_cols:
                    add_column("announcements", "poster_filename", "VARCHAR(255)")

                vis_cols = existing_columns("visitors")
                if "student_number" not in vis_cols:
                    add_column("visitors", "student_number", "VARCHAR(8)")
                if "cellphone_number" not in vis_cols:
                    add_column("visitors", "cellphone_number", "VARCHAR(20)")

                enq_cols = existing_columns("enquiries")
                enq_additions = [
                    ("escalation_reason", "TEXT"),
                    ("not_resolved_reason", "TEXT"),
                    ("assigned_by", "INTEGER"),
                    ("closed_by", "INTEGER"),
                    ("escalated_at", "TIMESTAMP"),
                    ("assigned_at", "TIMESTAMP"),
                    ("in_progress_at", "TIMESTAMP"),
                    ("resolved_at", "TIMESTAMP"),
                    ("closed_at", "TIMESTAMP"),
                ]
                for col, col_type in enq_additions:
                    if col not in enq_cols:
                        add_column("enquiries", col, col_type)

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
