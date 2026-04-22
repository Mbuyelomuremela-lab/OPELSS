import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        f"sqlite:///{BASE_DIR / 'instance' / 'app.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
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
