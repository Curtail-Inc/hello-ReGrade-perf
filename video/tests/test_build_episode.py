import json
import pytest
import tempfile
from build_episode import words_to_frames, chunk_cues, build_episode


def test_words_to_frames_offsets_and_scales():
    words = [{"word": "hi", "start": 0.0, "end": 0.5}, {"word": "there", "start": 0.5, "end": 1.0}]
    wf = words_to_frames(words, fps=24, offset_frames=24)
    assert wf[0] == {"word": "hi", "startFrame": 24, "endFrame": 36}   # 24 + 0.0*24 .. 24 + 0.5*24
    assert wf[1] == {"word": "there", "startFrame": 36, "endFrame": 48}


def test_chunk_cues_groups_and_bridges_gaps():
    wf = [{"word": w, "startFrame": i * 10, "endFrame": i * 10 + 5} for i, w in enumerate("a b c d e f g h".split())]
    cues = chunk_cues(wf, fps=24, max_words=7)
    assert len(cues) == 2                       # 8 words -> 7 + 1
    assert len(cues[0]["words"]) == 7 and len(cues[1]["words"]) == 1   # 7+1, not 4+4
    assert cues[0]["words"][0]["word"] == "a"
    assert cues[0]["endFrame"] == cues[1]["startFrame"]   # no blank flicker between cues


def test_caption_offset_is_frame_quantized_not_seconds():
    # Two beats of duration=0.521s each round to durationFrames = round(0.521*24) = round(12.504) = 13,
    # so the video's actual boundary after both beats is 13+13 = 26 frames. A third beat's first
    # caption word (start=0.0) must land at startFrame == 26 (the summed durationFrames), not
    # round(2*0.521*24) = round(25.008) = 25 (the seconds-accumulated value the old code produced).
    d = tempfile.mkdtemp()
    script_path = f"{d}/s.json"
    timestamps_path = f"{d}/t.json"

    json.dump({"beats": [
        {"id": "a", "clip": "a.mp4", "vo": "x"},
        {"id": "b", "clip": "b.mp4", "vo": "y"},
        {"id": "c", "clip": "c.mp4", "vo": "z"},
    ]}, open(script_path, "w"))
    json.dump({"beats": {
        "a": {"duration": 0.521, "words": []},
        "b": {"duration": 0.521, "words": []},
        "c": {"duration": 1.0, "words": [{"word": "hi", "start": 0.0, "end": 0.5}]},
    }}, open(timestamps_path, "w"))

    ep = build_episode(script_path, timestamps_path, fps=24)
    assert ep["beats"][0]["durationFrames"] == 13
    assert ep["beats"][1]["durationFrames"] == 13
    assert ep["captions"][0]["words"][0]["startFrame"] == 26


def test_duration_frames_floored_at_one():
    # Minimal script + timestamps with a ~0 duration beat
    d = tempfile.mkdtemp()
    script_path = f"{d}/s.json"
    timestamps_path = f"{d}/t.json"

    json.dump({"beats": [{"id": "a", "clip": "a.mp4", "vo": "x"}]}, open(script_path, "w"))
    json.dump({"beats": {"a": {"duration": 0.0, "words": []}}}, open(timestamps_path, "w"))

    ep = build_episode(script_path, timestamps_path, fps=24)
    assert ep["beats"][0]["durationFrames"] == 1
