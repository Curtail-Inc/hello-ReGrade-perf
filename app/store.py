# ABOUTME: A tiny two-version orders API. v1 and v2 return byte-identical bodies;
# ABOUTME: v2 only differs in latency — a constant slowdown and a load-induced lock.
import json
import os
import threading
import time

from flask import Flask, Response, abort

_CATEGORIES = ["tools", "home", "garden", "office"]

PRODUCTS = [
    {
        "id": i,
        "name": f"Product {i:02d}",
        "price": round(1.0 + i * 1.5, 2),
        "category": _CATEGORIES[i % len(_CATEGORIES)],
    }
    for i in range(1, 25)
]


def _order(oid, product_ids):
    items = []
    for pid in product_ids:
        p = PRODUCTS[pid - 1]
        qty = 1 + (pid % 3)
        items.append(
            {
                "product_id": pid,
                "name": p["name"],
                "qty": qty,
                "unit_price": p["price"],
                "line_total": round(qty * p["price"], 2),
            }
        )
    subtotal = round(sum(it["line_total"] for it in items), 2)
    tax = round(subtotal * 0.0725, 2)
    return {
        "id": oid,
        "items": items,
        "subtotal": subtotal,
        "tax": tax,
        "total": round(subtotal + tax, 2),
    }


ORDERS = {
    1001: _order(1001, [3, 7, 11]),
    1002: _order(1002, [1, 5]),
    1003: _order(1003, [12, 18, 20, 24]),
}

# v2 only: a global lock added "for thread-safety" that serializes the /orders hot path.
# Uncontended it costs nothing; under concurrent load every request queues behind it.
_ORDER_LOCK = threading.Lock()

# Simulated shared-resource read on /orders — I/O-bound, so it releases the GIL and
# genuinely runs in parallel across gunicorn threads (unless a lock serializes it).
_ORDER_IO_SECONDS = 0.008

# v2 only: an inefficient synchronous re-validation added to /products — a constant
# per-request tax that shows up even at --parallel 1.
_PRODUCTS_REGRESSION_SECONDS = 0.035


def _json(obj):
    # sort_keys → deterministic bytes, so v1 and v2 responses are identical.
    return Response(json.dumps(obj, sort_keys=True), mimetype="application/json")


def create_app(version=None):
    version = version or os.environ.get("APP_VERSION", "v1")
    is_v2 = version == "v2"
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return _json({"ok": True})

    @app.get("/products")
    def products():
        if is_v2:
            time.sleep(_PRODUCTS_REGRESSION_SECONDS)  # constant slowdown
        return _json({"products": PRODUCTS})

    @app.get("/orders/<int:oid>")
    def order(oid):
        record = ORDERS.get(oid)
        if record is None:
            abort(404)
        if is_v2:
            with _ORDER_LOCK:  # load-induced: serializes the read under concurrency
                time.sleep(_ORDER_IO_SECONDS)
        else:
            time.sleep(_ORDER_IO_SECONDS)  # same work, no global lock → runs in parallel
        return _json(record)

    return app
