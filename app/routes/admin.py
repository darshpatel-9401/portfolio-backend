"""Admin-only routes that are not plain CRUD: dashboard, messages, media library, image upload."""
from bson import ObjectId
from flask import Blueprint, jsonify, request

from app import extensions
from app.services.images import check_image
from app.services.storage import get_storage
from app.utils.auth import admin_required
from app.utils.errors import ApiError
from app.utils.serialize import serialize
from app.utils.text import utcnow

bp = Blueprint("admin", __name__)


def _oid(value):
    if not ObjectId.is_valid(value):
        raise ApiError("Not found", 404)
    return ObjectId(value)


# ---------- dashboard ----------
@bp.get("/dashboard")
@admin_required
def dashboard():
    db = extensions.db
    recent = lambda name, sort, n=5: serialize(list(db[name].find({}, {"content": 0}).sort(sort, -1).limit(n)))
    return jsonify({
        "counts": {
            "projects": db["projects"].count_documents({}),
            "skills": db["skills"].count_documents({}),
            "blog_posts": db["blogs"].count_documents({}),
            "experience": db["experience"].count_documents({}),
            "unread_messages": db["messages"].count_documents({"is_read": False}),
        },
        "recent_messages": recent("messages", "created_at"),
        "recent_posts": recent("blogs", "created_at"),
        "recent_projects": recent("projects", "created_at"),
    })


# ---------- contact messages ----------
@bp.get("/messages")
@admin_required
def list_messages():
    return jsonify(serialize(list(extensions.db["messages"].find({}).sort("created_at", -1))))


@bp.patch("/messages/<message_id>")
@admin_required
def update_message(message_id):
    data = request.get_json(silent=True) or {}
    if not isinstance(data.get("is_read"), bool):
        raise ApiError("is_read must be true or false", 400)
    result = extensions.db["messages"].update_one({"_id": _oid(message_id)}, {"$set": {"is_read": data["is_read"]}})
    if result.matched_count == 0:
        raise ApiError("Message not found", 404)
    return jsonify(serialize(extensions.db["messages"].find_one({"_id": ObjectId(message_id)})))


@bp.delete("/messages/<message_id>")
@admin_required
def delete_message(message_id):
    if extensions.db["messages"].delete_one({"_id": _oid(message_id)}).deleted_count == 0:
        raise ApiError("Message not found", 404)
    return "", 204


# ---------- media ----------
@bp.get("/media")
@admin_required
def list_media():
    return jsonify(serialize(list(extensions.db["media"].find({}).sort("created_at", -1))))


@bp.post("/upload/image")
@admin_required
def upload_image():
    file = request.files.get("file")
    if not file:
        raise ApiError("No file sent (the form field must be called 'file')", 400)
    data = file.read()
    extension, mime = check_image(data)
    filename, url = get_storage().save(data, extension)  # random file name, original name is never used on disk
    doc = {
        "filename": filename, "original_name": (file.filename or "upload")[:200].replace("/", "_").replace("\\", "_"),
        "url": url, "file_type": mime, "size": len(data), "created_at": utcnow(),
    }
    result = extensions.db["media"].insert_one(doc)
    return jsonify(serialize(extensions.db["media"].find_one({"_id": result.inserted_id}))), 201


@bp.delete("/media/<media_id>")
@admin_required
def delete_media(media_id):
    doc = extensions.db["media"].find_one({"_id": _oid(media_id)})
    if not doc:
        raise ApiError("File not found", 404)
    get_storage().delete(doc["filename"])
    extensions.db["media"].delete_one({"_id": doc["_id"]})
    return "", 204
