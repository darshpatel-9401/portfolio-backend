import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Every setting comes from environment variables (.env). Nothing secret is written in code."""

    SECRET_KEY = os.environ.get("SECRET_KEY", "")
    MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB = os.environ.get("MONGO_DB", "portfolio_cms")
    ACCESS_TOKEN_MINUTES = int(os.environ.get("ACCESS_TOKEN_MINUTES", 30))
    REFRESH_TOKEN_DAYS = int(os.environ.get("REFRESH_TOKEN_DAYS", 7))
    CORS_ORIGINS = [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",") if o.strip()]
    UPLOAD_DIR = os.path.abspath(os.environ.get("UPLOAD_DIR", "uploads"))
    MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", 5))
    MAX_CONTENT_LENGTH = (int(os.environ.get("MAX_UPLOAD_MB", 5)) + 1) * 1024 * 1024  # Flask rejects bigger requests

    SMTP_HOST = os.environ.get("SMTP_HOST", "")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    SMTP_FROM = os.environ.get("SMTP_FROM", "")
    CONTACT_RECEIVER = os.environ.get("CONTACT_RECEIVER", "")

    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")
