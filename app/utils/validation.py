"""Tiny input validator. Each schema lists the allowed fields and their types.
Anything not in the schema is dropped, so clients cannot sneak extra fields into the database."""
import re
from datetime import datetime

from app.utils.errors import ApiError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def Str(required=False, max=500, default=""):
    return {"type": "str", "required": required, "max": max, "default": default}


def Url(max=500):
    return {"type": "url", "required": False, "max": max, "default": ""}


def Email(required=True):
    return {"type": "email", "required": required, "max": 255, "default": ""}


def Int(min=None, max=None, default=0):
    return {"type": "int", "min": min, "max": max, "default": default}


def Bool(default=False):
    return {"type": "bool", "default": default}


def StrList(max_items=30, item_max=80):
    return {"type": "list", "max_items": max_items, "item_max": item_max}


def _clean(value, rule):
    kind = rule["type"]

    if kind in ("str", "url", "email"):
        if value is None:
            value = ""
        if not isinstance(value, str):
            raise ValueError("must be text")
        value = value.strip()
        if rule["required"] and not value:
            raise ValueError("is required")
        if len(value) > rule["max"]:
            raise ValueError(f"must be at most {rule['max']} characters")
        if value and kind == "url" and (value.startswith("//") or not value.startswith(("http://", "https://", "/", "#"))):
            raise ValueError("must start with http:// or https://")
        if value and kind == "email" and not EMAIL_RE.match(value):
            raise ValueError("is not a valid email address")
        return value

    if kind == "int":
        if value is None or value == "":
            return rule["default"]
        if isinstance(value, bool):
            raise ValueError("must be a number")
        try:
            number = int(value)
        except (TypeError, ValueError):
            raise ValueError("must be a number")
        if rule["min"] is not None and number < rule["min"]:
            raise ValueError(f"must be at least {rule['min']}")
        if rule["max"] is not None and number > rule["max"]:
            raise ValueError(f"must be at most {rule['max']}")
        return number

    if kind == "bool":
        return rule["default"] if value is None else bool(value)

    if kind == "list":
        if value is None:
            return []
        if not isinstance(value, list) or len(value) > rule["max_items"]:
            raise ValueError("must be a short list of text values")
        items = []
        for item in value:
            if not isinstance(item, str):
                raise ValueError("must contain text only")
            item = item.strip()
            if item:
                if len(item) > rule["item_max"]:
                    raise ValueError("has an item that is too long")
                items.append(item)
        return items

    raise ValueError("unknown field type")


def validate(data, schema):
    if not isinstance(data, dict):
        raise ApiError("Request body must be a JSON object", 400)
    clean, errors = {}, []
    for name, rule in schema.items():
        try:
            clean[name] = _clean(data.get(name), rule)
        except ValueError as e:
            errors.append(f"{name} {e}")
    if errors:
        raise ApiError("\n".join(errors), 400)
    return clean
