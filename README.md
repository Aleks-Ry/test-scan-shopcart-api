# shopcart-api

A minimal cart/checkout JSON API over an in-memory store. Two demo accounts
(`alice`, `bob`) share the password `demo` unless `DEMO_PASSWORD` is set.

Callers log in once and pass the returned token as `Authorization: Bearer <token>`
on every other request. Each account has a running balance that checkout debits.

## Running it

```bash
pip install -r requirements.txt
python app.py          # http://127.0.0.1:5001
```

## Endpoints

| Method | Path                 | Purpose                              |
| ------ | -------------------- | ------------------------------------ |
| POST   | `/login`             | `{username, password}` → `{token}`   |
| GET    | `/me`                | current account and balance          |
| GET    | `/catalog`           | available SKUs and prices            |
| POST   | `/cart/items`        | `{sku, qty}` → add a line to the cart |
| GET    | `/cart`              | cart lines and running total         |
| POST   | `/checkout`          | turn the cart into an order          |
| GET    | `/orders`            | orders belonging to the caller       |
| GET    | `/orders/<id>`       | a single order                       |

## Example

```bash
T=$(curl -s -X POST localhost:5001/login -H 'Content-Type: application/json' \
      -d '{"username":"alice","password":"demo"}' | python -c 'import json,sys;print(json.load(sys.stdin)["token"])')
curl -s -X POST localhost:5001/cart/items -H "Authorization: Bearer $T" \
     -H 'Content-Type: application/json' -d '{"sku":"SKU-MUG","qty":2}'
curl -s -X POST localhost:5001/checkout -H "Authorization: Bearer $T"
```
