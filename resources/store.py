import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import stores
from schemas import StoresSchema

blp = Blueprint("stores", __name__, description="Operations on stores")

@blp.route("/store/<string:store_id>")
class Store(MethodView):

    @blp.response(200, StoresSchema)
    def get(self, store_id):
        try:
            return stores[store_id]
        except KeyError:
            abort(404, message="[-] Store not found...")

    def delete(self, store_id):
        try:
            del stores[store_id]
            return {"message": "[+] Store deleted!"}
        except KeyError:
            abort(404, message="[-] Store not found...")

@blp.route("/store")
class StoreList(MethodView):


    @blp.arguments(StoresSchema)
    @blp.response(200, StoresSchema)
    def post(self, store_data):
        for store in stores.values():
            if store_data["name"] == store["name"]:
                abort(400, message=f"[!] Store already exists...")

        store_id = uuid.uuid4().hex

        # Unpack the data in the variable and add the uuid for the store.
        store = {**store_data, "id": store_id}
        stores[store_id] = store

        return store, 201
    
@blp.route("/stores")
class Stores(MethodView):

    @blp.response(200, StoresSchema(many=True))  # Produces a list.
    def get(self):
        # return {"stores": list(stores.values())} <<< [!] No longer needed.
        return stores.values() # Since blp.arguments produces a list, the above is not needed.