# ABOUTME: Tests for the two-version orders API.
# ABOUTME: Guards the core invariant — v1 and v2 return byte-identical bodies (only latency differs).
import time

from app.store import create_app


def _client(version):
    return create_app(version).test_client()


def test_health_ok():
    r = _client("v1").get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"ok": True}


def test_products_shape():
    r = _client("v1").get("/products")
    assert r.status_code == 200
    products = r.get_json()["products"]
    assert isinstance(products, list) and len(products) == 24
    assert set(products[0]) == {"id", "name", "price", "category"}


def test_order_shape():
    r = _client("v1").get("/orders/1001")
    assert r.status_code == 200
    order = r.get_json()
    assert set(order) == {"id", "items", "subtotal", "tax", "total"}
    assert order["id"] == 1001


def test_missing_order_404():
    assert _client("v1").get("/orders/9999").status_code == 404


def test_v1_and_v2_bodies_identical():
    """The whole point: same data, same bytes — only the timing changes."""
    v1, v2 = _client("v1"), _client("v2")
    for path in ["/products", "/orders/1001", "/orders/1002", "/orders/1003"]:
        r1, r2 = v1.get(path), v2.get(path)
        assert r1.status_code == r2.status_code == 200
        assert r1.data == r2.data, f"bodies differ for {path} — regression must be latency-only"


def test_v2_products_constant_slowdown():
    """v2 /products is measurably slower than v1 even single-shot (constant regression)."""
    v1, v2 = _client("v1"), _client("v2")
    v1.get("/products"); v2.get("/products")  # warm
    t1 = min(_timed(v1, "/products") for _ in range(3))
    t2 = min(_timed(v2, "/products") for _ in range(3))
    assert t2 >= t1 + 0.020, f"expected v2 >= v1+20ms, got v1={t1*1000:.1f}ms v2={t2*1000:.1f}ms"


def _timed(client, path):
    start = time.perf_counter()
    client.get(path)
    return time.perf_counter() - start
