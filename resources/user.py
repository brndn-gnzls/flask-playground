from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, create_refresh_token, get_jwt_identity
from blocklist import BLOCKLIST

from schemas import UserSchema
from models import UserModel
from db import db

blp = Blueprint("users", __name__, description="Operations on users")


@blp.route("/register")
class UserRegistration(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):

        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"]),
        )

        try:
            db.session.add(user)
            db.session.commit()
            return {"message": "[+] User successfully created!"}, 201
        except IntegrityError as e:
            db.session.rollback()
            abort(
                400, message=f"[!] A user with that username already exists: {str(e)}"
            )


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        user = UserModel.query.filter( UserModel.username == user_data["username"] ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            # Generate fresh access token
            access_token = create_access_token(identity=user.id, fresh=True)

            # Refresh token
            refresh_token = create_refresh_token(identity=user.id)

            return {"access token": access_token, "refresh_token": refresh_token}

        abort(401, message="[!] Invalid credentials...")

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)

        return {"access token": new_token}

@blp.route("/user/<int:user_id>")
class User(MethodView):

    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": "[+] User deleted!"}, 200


# Logout
@blp.route("/logout")
class UserLogout(MethodView):

    @jwt_required()
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "[+] Successfully logged out!"}

        