"""Build episode.json (the Remotion props) from script.json + timestamps.json."""
import json
import sys
from lib.script import load_script


def words_to_frames(words, fps, offset_frames):
    return [{"word": w["word"],
             "startFrame": offset_frames + round(w["start"] * fps),
             "endFrame": offset_frames + round(w["end"] * fps)} for w in words]


def chunk_cues(word_frames, fps, max_words=7):
    cues = []
    for i in range(0, len(word_frames), max_words):
        group = word_frames[i:i + max_words]
        cues.append({"startFrame": group[0]["startFrame"], "endFrame": group[-1]["endFrame"], "words": group})
    for i in range(len(cues) - 1):            # bridge gaps so captions never flicker to blank
        cues[i]["endFrame"] = cues[i + 1]["startFrame"]
    return cues


def build_episode(script_path, timestamps_path, fps=24, width=1920, height=1080):
    beats = load_script(script_path)
    ts = json.loads(open(timestamps_path).read())["beats"]
    out_beats, all_cues, offset_frames = [], [], 0
    for b in beats:
        info = ts[b.id]
        dur = info["duration"]
        duration_frames = max(1, round(dur * fps))
        out_beats.append({"id": b.id, "clip": b.clip, "durationFrames": duration_frames})
        wf = words_to_frames(info.get("words", []), fps, offset_frames)
        all_cues.extend(chunk_cues(wf, fps))
        offset_frames += duration_frames
    return {"fps": fps, "width": width, "height": height, "beats": out_beats, "captions": all_cues}


if __name__ == "__main__":
    ep = build_episode(sys.argv[1], sys.argv[2])
    json.dump(ep, open(sys.argv[3], "w"), indent=2)
    print(f"wrote {sys.argv[3]}: {len(ep['beats'])} beats, {len(ep['captions'])} cues")
