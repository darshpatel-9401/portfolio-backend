import re
from datetime import datetime


def slugify(text):
    return re.sub(r"[^a-zA-Z0-9]+", "-", (text or "").lower()).strip("-") or "item"


def utcnow():
    return datetime.utcnow().replace(microsecond=0)
