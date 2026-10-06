from datetime import datetime, timedelta, timezone
from functools import wraps

import bcrypt
import jwt
from bson import ObjectId
from flask import g, request

from app import extensions
from app.config import Config
from app.utils.errors import ApiError


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_token(user_id, kind):
    """'access' = short life, sent with every request. 'refresh' = long life, only used to get a new access token."""
    now = datetime.now(timezone.utc)
    life = timedelta(minutes=Config.ACCESS_TOKEN_MINUTES) if kind == "access" else timedelta(days=Config.REFRESH_TOKEN_DAYS)
    return jwt.encode({"sub": str(user_id), "type": kind, "iat": now, "exp": now + life}, Config.SECRET_KEY, algorithm="HS256")


def decode_token(token, kind):
    try:
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    return data if data.get("type") == kind else None


def bearer_token():
    header = request.headers.get("Authorization", "")
    return header[7:] if header.startswith("Bearer ") else None


def user_from_token(kind="access"):
    token = bearer_token()
    data = decode_token(token, kind) if token else None
    if not data or not ObjectId.is_valid(data["sub"]):
        return None
    return extensions.db["users"].find_one({"_id": ObjectId(data["sub"])})


def get_current_admin():
    """Logged-in admin or None. Public routes use it to decide whether to also show drafts."""
    return user_from_token("access")


def admin_required(fn):
    """Put under a route to make it admin-only. The check happens on the server."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        admin = get_current_admin()
        if not admin:
            raise ApiError("Not authenticated", 401)
        g.admin = admin
        return fn(*args, **kwargs)

    return wrapper
