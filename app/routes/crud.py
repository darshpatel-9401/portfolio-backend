"""One function that builds list / read / create / update / delete routes for a content type.
GET is public (but only shows published/active items). POST, PUT, DELETE need an admin login.
If an admin is logged in, GET returns everything, including drafts and hidden items."""
import re

from bson import ObjectId
from flask import Blueprint, jsonify, request
from pymongo.errors import DuplicateKeyError

from app import extensions
from app.utils.auth import admin_required, get_current_admin
from app.utils.errors import ApiError
from app.utils.serialize import serialize
from app.utils.text import slugify, utcnow
from app.utils.validation import validate

ORDER = [("display_order", 1), ("_id", 1)]


def make_crud(name, schema, public_filter=None, public_sort=None, admin_sort=None,
              hook=None, by_slug=False, hide_in_list=None, extra_query=None):
    bp = Blueprint(name, __name__)

    def coll():
        return extensions.db[name]

    @bp.get(f"/{name}")
    def list_items():
        admin = get_current_admin()
        query = {} if admin else dict(public_filter or {})
        if extra_query:
            query.update(extra_query(request.args))
        sort = (admin_sort if admin else public_sort) or ORDER
        projection = None if admin or not hide_in_list else {f: 0 for f in hide_in_list}
        return jsonify(serialize(list(coll().find(query, projection).sort(sort))))

    @bp.get(f"/{name}/<ident>")
    def get_item(ident):
        query = {"slug": ident} if by_slug else ({"_id": ObjectId(ident)} if ObjectId.is_valid(ident) else None)
        if query is None:
            raise ApiError("Not found", 404)
        if not get_current_admin():
            query.update(public_filter or {})
        doc = coll().find_one(query)
        if not doc:
            raise ApiError("Not found", 404)
        return jsonify(serialize(doc))

    @bp.post(f"/{name}")
    @admin_required
    def create_item():
        data = validate(request.get_json(silent=True), schema)
        if hook:
            hook(data, None)
        data["created_at"] = data["updated_at"] = utcnow()
        try:
            result = coll().insert_one(data)
        except DuplicateKeyError:
            raise ApiError("That slug is already used. Please choose another one.", 409)
        return jsonify(serialize(coll().find_one({"_id": result.inserted_id}))), 201

    @bp.put(f"/{name}/<item_id>")
    @admin_required
    def update_item(item_id):
        if not ObjectId.is_valid(item_id):
            raise ApiError("Not found", 404)
        existing = coll().find_one({"_id": ObjectId(item_id)})
        if not existing:
            raise ApiError("Not found", 404)
        data = validate(request.get_json(silent=True), schema)
        if hook:
            hook(data, existing)
        data["updated_at"] = utcnow()
        try:
            coll().update_one({"_id": existing["_id"]}, {"$set": data})
        except DuplicateKeyError:
            raise ApiError("That slug is already used. Please choose another one.", 409)
        return jsonify(serialize(coll().find_one({"_id": existing["_id"]})))

    @bp.delete(f"/{name}/<item_id>")
    @admin_required
    def delete_item(item_id):
        if not ObjectId.is_valid(item_id):
            raise ApiError("Not found", 404)
        result = coll().delete_one({"_id": ObjectId(item_id)})
        if result.deleted_count == 0:
            raise ApiError("Not found", 404)
        return "", 204

    return bp


# ---------- small hooks for content types that need extra work ----------
def project_hook(data, existing):
    data["slug"] = slugify(data.get("slug") or data["title"])


def blog_hook(data, existing):
    data["slug"] = slugify(data.get("slug") or data["title"])
    old = (existing or {}).get("published_at")
    # stamp the date the first time a post is published; keep it if it is unpublished later
    data["published_at"] = (old or utcnow()) if data["is_published"] else old


def blog_search(args):
    """Public blog search: ?q=word&tag=python. Values from the URL are always plain text, so no operators can sneak in."""
    query = {}
    q = (args.get("q") or "").strip()[:100]
    if q:
        pattern = {"$regex": re.escape(q), "$options": "i"}
        query["$or"] = [{"title": pattern}, {"description": pattern}]
    tag = (args.get("tag") or "").strip()[:40]
    if tag:
        query["tags"] = tag
    return query
