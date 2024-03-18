import requests
import os
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, get_jwt, jwt_required, create_refresh_token, get_jwt_identity
from blocklist import BLOCKLIST
from sqlalchemy import or_


from schemas import UserSchema, UserRegistrationSchema
from models import UserModel
from db import db

blp = Blueprint("users", __name__, description="Operations on users")

def send_simple_message(to, subject, body):
    domain = os.getenv("MAILGUN_DOMAIN")
    return requests.post(
		f"https://api.mailgun.net/v3/{domain}/messages",
		auth=("api", os.getenv("MAILGUN_API_KEY")),
		data={"from": "Wrvthlss <mailgun@{domain}>",
			"to": [to],
			"subject": subject,
			"text": body})


@blp.route("/register")
class UserRegistration(MethodView):
    @blp.arguments(UserRegistrationSchema)
    def post(self, user_data):

        if UserModel.query.filter(
            # checks either argument is true
            or_(
                UserModel.username == user_data["username"],
                UserModel.email == user_data["email"]
            )).first():
                abort(409, message={"A user with that username already exists."})

        user = UserModel(
            username=user_data["username"],
            email=user_data["email"],
            password=pbkdf2_sha256.hash(user_data["password"]),
        )

        try:
            db.session.add(user)
            db.session.commit()

            send_simple_message(
                to=user.email,
                subject="Successfully signed up",
                body="Hi, you have successfully signed up to the API."
            )

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

        