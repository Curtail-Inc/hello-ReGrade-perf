from tts import words_from_alignment


def test_words_from_alignment_splits_on_space():
    # ElevenLabs returns per-character arrays
    alignment = {
        "characters": list("hi there"),
        "character_start_times_seconds": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
        "character_end_times_seconds":   [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
    }
    words = words_from_alignment(alignment)
    assert [w["word"] for w in words] == ["hi", "there"]
    assert words[0]["start"] == 0.0 and words[0]["end"] == 0.2
    assert words[1]["start"] == 0.3 and words[1]["end"] == 0.8


def test_stub_beat_produces_words_and_audio(tmp_path):
    import os
    from tts import _stub_beat
    out = str(tmp_path / "s.mp3")
    words = _stub_beat("hello there world", out)
    assert [w["word"] for w in words] == ["hello", "there", "world"]
    assert words[0]["start"] == 0.0 and words[-1]["end"] > words[0]["end"]
    assert os.path.getsize(out) > 0   # ffmpeg wrote real audio


def test_warn_if_stub_warns_when_tts_stub_set(monkeypatch, capsys):
    from tts import _warn_if_stub
    monkeypatch.setenv("TTS_STUB", "1")
    _warn_if_stub()
    assert "TTS_STUB active" in capsys.readouterr().err


def test_warn_if_stub_silent_when_tts_stub_unset(monkeypatch, capsys):
    from tts import _warn_if_stub
    monkeypatch.delenv("TTS_STUB", raising=False)
    _warn_if_stub()
    assert capsys.readouterr().err == ""
