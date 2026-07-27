"""In-memory data layer for the cart service."""

import itertools
import os
import secrets

from werkzeug.security import check_password_hash, generate_password_hash

CATALOG = {
    "SKU-TEA": {"name": "Loose leaf tea", "price": 12.50},
    "SKU-MUG": {"name": "Stoneware mug", "price": 18.00},
    "SKU-POT": {"name": "Glass teapot", "price": 34.00},
}

_DEMO_PASSWORD = os.environ.get("DEMO_PASSWORD", "demo")

USERS = {
    "alice": {"pw": generate_password_hash(_DEMO_PASSWORD), "balance": 0.0},
    "bob": {"pw": generate_password_hash(_DEMO_PASSWORD), "balance": 0.0},
}

SESSIONS = {}          # token -> username
CARTS = {}             # username -> list of {sku, qty}
ORDERS = {}            # order id -> {id, owner, lines, total}

_order_ids = itertools.count(1000)


def login(username, password):
    user = USERS.get(username)
    if not user or not check_password_hash(user["pw"], password):
        return None
    token = secrets.token_hex(16)
    SESSIONS[token] = username
    return token


def user_for_token(token):
    return SESSIONS.get(token)


def cart_of(username):
    return CARTS.setdefault(username, [])


def add_item(username, sku, qty):
    if sku not in CATALOG:
        raise KeyError(sku)
    qty = int(qty)
    cart = cart_of(username)
    for line in cart:
        if line["sku"] == sku:
            line["qty"] += qty
            return line
    line = {"sku": sku, "qty": qty}
    cart.append(line)
    return line


def cart_total(username):
    total = 0.0
    for line in cart_of(username):
        total += CATALOG[line["sku"]]["price"] * line["qty"]
    return round(total, 2)


def checkout(username):
    lines = list(cart_of(username))
    total = cart_total(username)
    order = {"id": next(_order_ids), "owner": username, "lines": lines, "total": total}
    ORDERS[order["id"]] = order
    USERS[username]["balance"] -= total
    CARTS[username] = []
    return order


def get_order(order_id):
    return ORDERS.get(order_id)


def orders_of(username):
    return [o for o in ORDERS.values() if o["owner"] == username]
