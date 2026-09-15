"""Cart and order HTTP API."""

from flask import Flask, jsonify, request, send_from_directory

import store

app = Flask(__name__, static_folder="static", static_url_path="")


@app.get("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


def current_user():
    header = request.headers.get("Authorization", "")
    token = header[7:] if header.startswith("Bearer ") else ""
    return store.user_for_token(token)


@app.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    token = store.login(body.get("username", ""), body.get("password", ""))
    if not token:
        return jsonify(error="invalid credentials"), 401
    return jsonify(token=token)


@app.get("/me")
def me():
    user = current_user()
    if not user:
        return jsonify(error="unauthenticated"), 401
    return jsonify(username=user, balance=store.USERS[user]["balance"])


@app.get("/catalog")
def catalog():
    return jsonify(store.CATALOG)


@app.post("/cart/items")
def add_to_cart():
    user = current_user()
    if not user:
        return jsonify(error="unauthenticated"), 401
    body = request.get_json(silent=True) or {}
    try:
        line = store.add_item(user, body.get("sku"), body.get("qty", 1))
    except KeyError:
        return jsonify(error="unknown sku"), 404
    except (TypeError, ValueError):
        return jsonify(error="qty must be a number"), 400
    return jsonify(line=line, total=store.cart_total(user))


@app.get("/cart")
def view_cart():
    user = current_user()
    if not user:
        return jsonify(error="unauthenticated"), 401
    return jsonify(lines=store.cart_of(user), total=store.cart_total(user))


@app.post("/checkout")
def checkout():
    user = current_user()
    if not user:
        return jsonify(error="unauthenticated"), 401
    if not store.cart_of(user):
        return jsonify(error="cart is empty"), 400
    order = store.checkout(user)
    return jsonify(order=order, balance=store.USERS[user]["balance"])


@app.get("/orders")
def list_orders():
    user = current_user()
    if not user:
        return jsonify(error="unauthenticated"), 401
    return jsonify(orders=store.orders_of(user))


@app.get("/orders/<int:order_id>")
def show_order(order_id):
    user = current_user()
    if not user:
        return jsonify(error="unauthenticated"), 401
    order = store.get_order(order_id)
    if not order:
        return jsonify(error="not found"), 404
    return jsonify(order=order)


if __name__ == "__main__":
    app.run(port=5001, debug=False)
