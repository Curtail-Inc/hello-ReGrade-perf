"""Build the WebVTT caption sidecar from an episode's word-level cues.

The rendered video burns its captions in, but a <video> element on a web page
wants a separate track file so viewers can turn captions off, and so the text is
selectable and indexable. Both come from the same cues, so they cannot drift.

Usage: make_vtt.py <episode.json> <out.vtt>
"""
import json
import sys
from pathlib import Path


def timestamp(frame, fps):
    """Frame number to the HH:MM:SS.mmm that WebVTT requires."""
    seconds = frame / fps
    hours, rest = divmod(seconds, 3600)
    minutes, secs = divmod(rest, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{secs:06.3f}"


def write_vtt(episode, path):
    """Write the track and return how many cues it holds."""
    fps = episode.get("fps", 24)
    lines = ["WEBVTT", ""]
    written = 0
    for cue in episode.get("captions", []):
        text = " ".join(w["word"] for w in cue["words"]).strip()
        # A cue with no words would render as a flicker of empty caption box.
        if not text:
            continue
        lines.append(f"{timestamp(cue['startFrame'], fps)} --> {timestamp(cue['endFrame'], fps)}")
        lines.append(text)
        lines.append("")
        written += 1
    Path(path).write_text("\n".join(lines))
    return written


def main(episode_path, out_path):
    episode = json.loads(Path(episode_path).read_text())
    count = write_vtt(episode, out_path)
    print(f"{count} cues -> {out_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
