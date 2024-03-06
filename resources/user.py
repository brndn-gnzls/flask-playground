from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token

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
            password=pbkdf2_sha256.hash(user_data["password"])
        )

        try:
            db.session.add(user)
            db.session.commit()
            return {"message": "[+] User successfully created!"}, 201
        except IntegrityError as e:
            db.session.rollback()
            abort(400, message=f"[!] A user with that username already exists: {str(e)}")

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