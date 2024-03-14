import os

from flask import Flask, jsonify
from flask_smorest import Api
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from db import db
from blocklist import BLOCKLIST
import models

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint


def create_app(db_url=None):
    app = Flask(__name__)
    CORS(app)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = (
        "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    )

    basedir = os.path.abspath(os.path.dirname(__file__))

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv(
        "DATABASE_URL", 'sqlite:///' + os.path.join(basedir, 'instance', 'data.db')
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    migrate = Migrate(app, db)

    api = Api(app)

    app.config["JWT_SECRET_KEY"] = (
        "JgZ+UrtOKhKW9bwBY9Sz0fKabfiJB26+tEKflvDOmklsNLHDWNXW5/453eJUICjXIXw0yw+f1BT0w9Do2wbs5Q=="
    )
    jwt = JWTManager(app)

    # Token revocation for logout.
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        # If true request is terminated, the token has been revoked.
        return jwt_payload['jti'] in BLOCKLIST


    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "[-] The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )        
    # Token revocation for logout.

    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return(
            jsonify(
                {
                    "description": "[!] The token is not fresh...",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"message": "[!] The token has expired.", "error": "token_expired"}
            ),
            401,
        )

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify(
                {
                    "message": "[!] Signature verification failed.",
                    "error": "invalid_token",
                }
            ),
            401,
        )

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify(
                {
                    "description": "[!] The request does not contain an access token.",
                    "error": "authorization_required",
                }
            ),
            401,
        )

    # with app.app_context():
    #     try:
    #         db.create_all()
    #         print(f"[+] Database created: {os.getcwd()}")
    #     except Exception as e:
    #         print(f"[-] Error creating dtabase: {e}")

    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint)
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)

    # return app.
    return app
