import json
import tempfile
from pathlib import Path

from make_vtt import timestamp, write_vtt


def test_timestamp_formats_hours_minutes_and_milliseconds():
    assert timestamp(0, 24) == "00:00:00.000"
    assert timestamp(36, 24) == "00:00:01.500"
    assert timestamp(24 * 61, 24) == "00:01:01.000"
    assert timestamp(24 * 3661, 24) == "01:01:01.000"


def test_cue_text_joins_the_words_of_that_cue():
    episode = {
        "fps": 24,
        "captions": [
            {"startFrame": 0, "endFrame": 24,
             "words": [{"word": "hello", "startFrame": 0, "endFrame": 12},
                       {"word": "there", "startFrame": 12, "endFrame": 24}]},
        ],
    }
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "x.vtt"
        assert write_vtt(episode, out) == 1
        assert out.read_text() == "WEBVTT\n\n00:00:00.000 --> 00:00:01.000\nhello there\n"


def test_a_cue_with_no_words_is_skipped_rather_than_written_blank():
    """An empty cue would show as a flicker of empty subtitle box."""
    episode = {"fps": 24, "captions": [
        {"startFrame": 0, "endFrame": 24, "words": []},
        {"startFrame": 24, "endFrame": 48,
         "words": [{"word": "real", "startFrame": 24, "endFrame": 48}]},
    ]}
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "x.vtt"
        assert write_vtt(episode, out) == 1
        assert "real" in out.read_text()
        assert "00:00:00.000" not in out.read_text()


def test_regenerates_the_shipped_caption_track_byte_for_byte():
    """The published .en.vtt must be reproducible from episode.json alone.

    This is the whole point of the script: the tracks on the CDN were produced
    by something that was never committed, so nothing proved they could be
    rebuilt. If this fails, the shipped captions and this generator have
    diverged and one of them is wrong.
    """
    here = Path(__file__).resolve().parent.parent
    episode_path = here / "out" / "episode.json"
    shipped = here / "out" / "hello-regrade-perf-demo.en.vtt"
    if not episode_path.exists() or not shipped.exists():
        import pytest
        pytest.skip("needs a built episode and its shipped track")
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "regen.vtt"
        write_vtt(json.loads(episode_path.read_text()), out)
        assert out.read_text() == shipped.read_text()
