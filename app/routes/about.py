from flask import Blueprint, jsonify, request

from app import extensions
from app.utils import schemas
from app.utils.auth import admin_required
from app.utils.errors import ApiError
from app.utils.serialize import serialize
from app.utils.text import utcnow
from app.utils.validation import validate

bp = Blueprint("about", __name__)


@bp.get("/about")
def get_about():
    doc = extensions.db["about"].find_one({})
    if not doc:
        raise ApiError("About information has not been set up yet", 404)
    return jsonify(serialize(doc))


@bp.put("/about")
@admin_required
def update_about():
    data = validate(request.get_json(silent=True), schemas.ABOUT)
    data["updated_at"] = utcnow()
    extensions.db["about"].update_one({}, {"$set": data, "$setOnInsert": {"created_at": utcnow()}}, upsert=True)
    return jsonify(serialize(extensions.db["about"].find_one({})))


# ---------- site settings (site name, footer text ...) as simple key/value pairs ----------
@bp.get("/settings")
def get_settings():
    return jsonify({s["key"]: s["value"] for s in extensions.db["settings"].find({})})


@bp.put("/settings")
@admin_required
def update_settings():
    values = request.get_json(silent=True)
    if not isinstance(values, dict) or len(values) > 50:
        raise ApiError("Send an object of key/value pairs", 400)
    for key, value in values.items():
        if not isinstance(key, str) or not isinstance(value, str) or len(key) > 100 or len(value) > 5000:
            raise ApiError("Settings must be short text values", 400)
        extensions.db["settings"].update_one({"key": key}, {"$set": {"value": value}}, upsert=True)
    return jsonify({s["key"]: s["value"] for s in extensions.db["settings"].find({})})
