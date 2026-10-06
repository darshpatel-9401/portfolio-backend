from flask import Blueprint, jsonify, request

from app import extensions
from app.services.email import send_contact_email
from app.utils import schemas
from app.utils.rate_limit import limit
from app.utils.text import utcnow
from app.utils.validation import validate

bp = Blueprint("contact", __name__)


@bp.post("/contact")
@limit("contact", 5, 600)
def contact():
    data = validate(request.get_json(silent=True), schemas.CONTACT)
    data.update({"is_read": False, "created_at": utcnow()})
    extensions.db["messages"].insert_one(data)  # 1) save in MongoDB
    send_contact_email(data)                    # 2) email it to you (if SMTP is configured)
    return jsonify({"message": "Thanks! Your message has been sent."}), 201
