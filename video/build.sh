#!/usr/bin/env bash
# Build the demo video: TTS -> episode.json -> Remotion silent render -> normalize VO -> ffmpeg mux VO.
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
unset -f node npm npx nvm 2>/dev/null || true

echo "== 1. voiceover =="
"$PY" tts.py script.json capture/voiceover.mp3 capture/timestamps.json

echo "== 2. episode.json =="
"$PY" build_episode.py script.json capture/timestamps.json out/episode.json

echo "== 3. remotion silent render =="
( cd remotion && npx remotion render Video ../out/silent.mp4 \
    --props=../out/episode.json --public-dir=../capture --codec=h264 --crf=16 )

echo "== 4. normalize voiceover loudness (streaming target ~-16 LUFS) =="
ffmpeg -y -i capture/voiceover.mp3 -af loudnorm=I=-16:TP=-1.5:LRA=11 \
  -ar 44100 -c:a libmp3lame -q:a 2 capture/voiceover_norm.mp3

echo "== 5. mux voiceover (stream-copy video — no re-encode) =="
ffmpeg -y -i out/silent.mp4 -i capture/voiceover_norm.mp3 \
  -map 0:v -map 1:a -c:v copy -c:a aac -ac 2 -b:a 192k -shortest \
  out/hello-regrade.mp4
echo "✓ out/hello-regrade.mp4"
