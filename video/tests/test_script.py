import json
import os
import pytest
from lib.script import load_script, Beat


def _write(tmp_path, obj):
    p = tmp_path / "s.json"
    p.write_text(json.dumps(obj))
    return str(p)


def test_loads_beats(tmp_path):
    path = _write(tmp_path, {"beats": [{"id": "a", "clip": "a.mp4", "vo": "hello"}]})
    beats = load_script(path)
    assert beats == [Beat(id="a", clip="a.mp4", vo="hello")]


def test_rejects_missing_field(tmp_path):
    path = _write(tmp_path, {"beats": [{"id": "a", "clip": "a.mp4"}]})
    with pytest.raises(ValueError):
        load_script(path)


def test_rejects_duplicate_id(tmp_path):
    path = _write(tmp_path, {"beats": [{"id": "a", "clip": "a.mp4", "vo": "x"},
                                        {"id": "a", "clip": "b.mp4", "vo": "y"}]})
    with pytest.raises(ValueError):
        load_script(path)


def test_rejects_empty_field(tmp_path):
    path = _write(tmp_path, {"beats": [{"id": "a", "clip": "a.mp4", "vo": ""}]})
    with pytest.raises(ValueError):
        load_script(path)


def test_real_script_has_nine_beats():
    path = os.path.join(os.path.dirname(__file__), "..", "script.json")
    beats = load_script(path)
    assert [b.id for b in beats] == ["cold-open", "problem", "setup", "record", "knobs", "stress", "analyze", "reveal", "outro"]
