import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")

    _db_url = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR / 'instance' / 'app.db'}")
    # SQLAlchemy 2.x requires "postgresql://" but Azure supplies "postgres://"
    if _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = _db_url

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    _is_postgres = _db_url.startswith("postgresql")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        **({"pool_size": 10, "max_overflow": 20, "pool_recycle": 1800} if _is_postgres else {}),
    }

    
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = os.environ.get("FLASK_ENV", "production") == "production"
    WTF_CSRF_TIME_LIMIT = None
    JSON_SORT_KEYS = False
    UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", str(BASE_DIR / "uploads"))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = "https"

class DevelopmentConfig(Config):
    DEBUG = True
    ENV = "development"
    SQLALCHEMY_ECHO = False
