import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import StoresSchema
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models import StoreModel
from db import db

blp = Blueprint("stores", __name__, description="Operations on stores")

@blp.route("/store/<string:store_id>")
class Store(MethodView):

    @blp.response(200, StoresSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)

        return store

    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        raise NotImplementedError("[!] Deleting a store is not implemented.")

@blp.route("/store")
class StoreList(MethodView):


    @blp.arguments(StoresSchema)
    @blp.response(200, StoresSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)

        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError as e:
            abort(400, message=f"[!] A store with that name already exists: {e}")
        except SQLAlchemyError as e:
            abort(500, message=f"[-] An error occurred creating the store: {e}")
            

        return store
    
@blp.route("/stores")
class Stores(MethodView):

    @blp.response(200, StoresSchema(many=True))  # Produces a list.
    def get(self):
        # return {"stores": list(stores.values())} <<< [!] No longer needed.
        return stores.values() # Since blp.arguments produces a list, the above is not needed.