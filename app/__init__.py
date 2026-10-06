import logging

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

from app import extensions
from app.config import Config
from app.utils.errors import ApiError


def create_app():
    if not Config.SECRET_KEY:
        raise RuntimeError("SECRET_KEY is missing. Copy .env.example to .env and set a long random value.")

    app = Flask(__name__)
    app.config.from_object(Config)

    # Only your own portfolio and admin sites may call the API from a browser
    CORS(app, origins=Config.CORS_ORIGINS, allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "PATCH", "DELETE"])

    extensions.init_db(Config.MONGO_URI, Config.MONGO_DB)
    extensions.create_indexes()

    from app.routes import about, admin, auth, contact
    from app.routes.content import blueprints

    for bp in [auth.bp, about.bp, contact.bp, admin.bp, *blueprints]:
        app.register_blueprint(bp)

    @app.get("/uploads/<path:filename>")
    def uploads(filename):
        return send_from_directory(Config.UPLOAD_DIR, filename)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    # ---- all errors are returned as JSON: {"detail": "message"} ----
    @app.errorhandler(ApiError)
    def handle_api_error(e):
        return jsonify({"detail": e.message}), e.status

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        message = "File is too large" if e.code == 413 else e.description
        return jsonify({"detail": message}), e.code

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        logging.exception("Unexpected error")
        return jsonify({"detail": "Server error"}), 500

    return app
