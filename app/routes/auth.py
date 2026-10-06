from flask import Blueprint, g, jsonify, request

from app import extensions
from app.utils.auth import admin_required, check_password, create_token, hash_password, user_from_token
from app.utils.errors import ApiError
from app.utils.rate_limit import limit

bp = Blueprint("auth", __name__, url_prefix="/auth")


def _user_json(user):
    return {"id": str(user["_id"]), "email": user["email"]}


@bp.post("/login")
@limit("login", 8, 60)
def login():
    data = request.get_json(silent=True) or {}
    email, password = str(data.get("email", "")).strip().lower(), str(data.get("password", ""))
    user = extensions.db["users"].find_one({"email": email})
    # same message for "no such user" and "wrong password" so attackers learn nothing
    if not user or not check_password(password, user["password_hash"]):
        raise ApiError("Invalid email or password", 401)
    return jsonify({
        "access_token": create_token(user["_id"], "access"),
        "refresh_token": create_token(user["_id"], "refresh"),
        "user": _user_json(user),
    })


@bp.post("/refresh")
def refresh():
    """Send the refresh token as 'Authorization: Bearer <refresh_token>' to get a new access token."""
    user = user_from_token("refresh")
    if not user:
        raise ApiError("Session expired. Please log in again.", 401)
    return jsonify({"access_token": create_token(user["_id"], "access")})


@bp.get("/me")
@admin_required
def me():
    return jsonify(_user_json(g.admin))


@bp.post("/change-password")
@admin_required
def change_password():
    data = request.get_json(silent=True) or {}
    current, new = str(data.get("current_password", "")), str(data.get("new_password", ""))
    if not check_password(current, g.admin["password_hash"]):
        raise ApiError("Current password is incorrect", 400)
    if len(new) < 10 or len(new) > 200:
        raise ApiError("New password must be 10 to 200 characters", 400)
    extensions.db["users"].update_one({"_id": g.admin["_id"]}, {"$set": {"password_hash": hash_password(new)}})
    return jsonify({"message": "Password changed"})
