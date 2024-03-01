from flask import Flask, request
from flask_cors import CORS
from db import items, stores
import uuid
from flask_smorest import abort

app = Flask(__name__)
CORS(app)



@app.route("/stores", methods=["GET"])
def get_stores():
    return {"stores": list(stores.values())}


@app.route("/store", methods=["POST"])
def create_store():
    store_data = request.get_json()
    if "name" not in store_data:
        abort(
            400,
            message="[!] Bad Request... Ensure 'name' is included in the JSON payload."
        )
    
    for store in stores.values():
        if store_data["name"] == store["name"]:
            abort(400, message=f"[!] Store already exists...")

    store_id = uuid.uuid4().hex

    # Unpack the data in the variable and add the uuid for the store.
    store = {**store_data, "id": store_id}
    stores[store_id] = store

    return store, 201


@app.route("/item", methods=["POST"])
def create_item():
    item_data = request.get_json()
    if (
        "price" not in item_data
        or "store_id" not in item_data
        or "name" not in item_data
    ):
        abort(
            400,
            message="[-] Bad Request... Ensure 'price', 'store_id', and 'name' are included in the JSON payload."
        )

    for item in items.values():
        if (
            item_data["name"] == item["name"]
            and item_data["store_id"] == item["store_id"]
        ):
            abort(400, message=f"[!] Item already exists...")

    if item_data["store_id"] not in stores:
        abort(404, message="[-] Store not found...")

    item_id = uuid.uuid4().hex
    item = {**item_data, "id": item_id}
    items[item_id] = item

    return item, 201


@app.route("/items", methods=["GET"])
def get_items():
    return {"items": list(items.values())}


@app.route("/store/<string:store_id>", methods=["GET"])
def get_store(store_id):
    try:
        return stores[store_id]
    except KeyError:
        abort(404, message="[-] Store not found...")


@app.route("/item/<string:item_id>", methods=["GET"])
def get_item(item_id):
    try:
        return items[item_id]
    except KeyError:
        abort(404, message="[-] Item not found...")



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
