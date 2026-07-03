#!/usr/bin/env bash
# Regenerate the voiceover for specific beat(s) without re-rolling the others.
# Cached takes live per-beat as capture/vo_<id>.mp3 (index-free) — so inserting a
# beat never shifts another's take, and every beat you don't name is reused as-is.
# Rebuilds capture/voiceover.mp3 + capture/timestamps.json + out/episode.json.
# (Render + music mix are separate: remotion render, then ./music_mix.sh.)
#
# Usage: ELEVENLABS_API_KEY=... ./regen_beat.sh <beat-id> [<beat-id> ...]
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
unset -f node npm npx nvm 2>/dev/null || true

: "${ELEVENLABS_API_KEY:?set ELEVENLABS_API_KEY (e.g. from ~/.config/elevenlabs/key)}"
[ $# -ge 1 ] || { echo "usage: $0 <beat-id> [<beat-id> ...]" >&2; exit 2; }

echo "== re-synthesize: $* =="
REGEN="$*" "$PY" - <<'EOF'
import json, os, subprocess, sys
sys.path.insert(0, os.getcwd())
from lib.script import load_script
from tts import _elevenlabs_beat, _ffprobe_duration

regen = set(os.environ["REGEN"].split())
beats = load_script("script.json")
bad = regen - {b.id for b in beats}
assert not bad, f"unknown beat id(s): {sorted(bad)}"
ts_path = "capture/timestamps.json"
ts = json.load(open(ts_path)) if os.path.exists(ts_path) else {"beats": {}}

for b in beats:
    mp3 = f"capture/vo_{b.id}.mp3"
    if b.id in regen or not os.path.exists(mp3):
        print(f"  synth {b.id}")
        words = _elevenlabs_beat(b.vo, mp3)
        ts["beats"][b.id] = {"duration": _ffprobe_duration(mp3), "words": words}
    elif b.id not in ts["beats"]:
        raise SystemExit(f"cached {mp3} exists but no timestamps for '{b.id}' — run a full build.sh")

mp3s = [f"capture/vo_{b.id}.mp3" for b in beats]
open("capture/vo_list.txt", "w").write("".join(f"file '{os.path.abspath(m)}'\n" for m in mp3s))
subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0",
                "-i", "capture/vo_list.txt", "-c", "copy", "capture/voiceover.mp3"], check=True)
json.dump(ts, open(ts_path, "w"), indent=2)
print("  voiceover.mp3 + timestamps.json rebuilt")
EOF

echo "== episode.json =="
"$PY" build_episode.py script.json capture/timestamps.json out/episode.json
