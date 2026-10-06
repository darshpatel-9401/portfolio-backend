from pymongo import ASCENDING, MongoClient

client = None
db = None  # other files use  extensions.db["skills"]  etc.


def init_db(uri, name):
    global client, db
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    db = client[name]
    return db


def create_indexes():
    """Safe to run on every start. Unique indexes stop duplicate emails and slugs."""
    db["users"].create_index("email", unique=True)
    db["projects"].create_index("slug", unique=True)
    db["blogs"].create_index("slug", unique=True)
    db["blogs"].create_index([("is_published", ASCENDING), ("published_at", -1)])
    db["messages"].create_index([("created_at", -1)])
    db["settings"].create_index("key", unique=True)
