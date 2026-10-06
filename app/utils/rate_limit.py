import time
from collections import defaultdict
from functools import wraps

from flask import request

from app.utils.errors import ApiError

# In-memory counter (per server process). Fine for a portfolio; use Redis if you scale out.
_hits = defaultdict(list)


def limit(name, max_calls, per_seconds):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = (name, request.remote_addr)
            now = time.time()
            _hits[key] = [t for t in _hits[key] if now - t < per_seconds]
            if len(_hits[key]) >= max_calls:
                raise ApiError("Too many requests. Please try again later.", 429)
            _hits[key].append(now)
            return fn(*args, **kwargs)

        return wrapper

    return decorator
