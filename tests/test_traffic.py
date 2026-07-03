# ABOUTME: Sanity checks for the baseline traffic generator.
import os
import stat

SCRIPT = os.path.join(os.path.dirname(__file__), "..", "traffic", "generate.sh")


def test_script_exists_and_executable():
    assert os.path.exists(SCRIPT)
    assert os.stat(SCRIPT).st_mode & stat.S_IXUSR, "generate.sh must be executable"


def test_script_hits_both_endpoints_and_guards_health():
    body = open(SCRIPT).read()
    assert "/products" in body
    assert "/orders/" in body
    assert "/health" in body  # reachability guard before generating traffic
