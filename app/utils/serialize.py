from datetime import datetime

from bson import ObjectId

HIDDEN = {"password_hash"}


def serialize(value):
    """Turns Mongo documents into JSON-friendly data: _id -> id, ObjectId -> text, dates -> ISO text."""
    if isinstance(value, list):
        return [serialize(v) for v in value]
    if isinstance(value, dict):
        out = {}
        for key, val in value.items():
            if key in HIDDEN:
                continue
            out["id" if key == "_id" else key] = serialize(val)
        return out
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, datetime):
        return value.isoformat(timespec="seconds") + "Z"
    return value
