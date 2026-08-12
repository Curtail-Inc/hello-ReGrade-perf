#!/usr/bin/env bash
# Mix the music bed under the voiceover and mux with the silent render.
# Music is sidechain-ducked by the voice, so it swells only in narration gaps.
# No Remotion re-render needed — video stream is copied untouched.
#
# Inputs:  out/silent.mp4  capture/voiceover_norm.mp3  capture/music.mp3
# Output:  out/hello-regrade.mp4
#
set -euo pipefail
cd "$(dirname "$0")"

# Bed level and duck shape, overridable for tuning: BED_VOLUME=1.4 ./music_mix.sh
#
# Measured against a voiceover normalized to -16 LUFS, these put the bed about
# 5 dB under the voice. The earlier settings (0.22 with ratio 6 at a 0.02
# threshold) sat 26 dB under and were inaudible in a browser tab: a 0.02
# threshold is roughly -34 dB, so any speech triggered a full duck, and a 600 ms
# release never let the music back between words.
BED_VOLUME="${BED_VOLUME:-1.10}"        # static level before ducking
BED_RATIO="${BED_RATIO:-3}"             # duck depth while the voice is speaking
BED_THRESHOLD="${BED_THRESHOLD:-0.05}"  # voice level that starts the duck
BED_RELEASE="${BED_RELEASE:-250}"       # ms for the bed to swell back after a phrase

# Fade the bed out over the last 4s, derived from the actual render length.
VDUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 out/silent.mp4)
FADE_ST=$(awk -v d="$VDUR" 'BEGIN{printf "%.1f", d-4}')

ffmpeg -y -i out/silent.mp4 -i capture/voiceover_norm.mp3 -i capture/music.mp3 \
  -filter_complex "\
[2:a]aformat=channel_layouts=stereo,afade=t=in:d=2,afade=t=out:st=${FADE_ST}:d=4,volume=${BED_VOLUME}[mq];\
[1:a]aformat=channel_layouts=stereo,asplit=2[vo][sc];\
[mq][sc]sidechaincompress=threshold=${BED_THRESHOLD}:ratio=${BED_RATIO}:attack=20:release=${BED_RELEASE}[duck];\
[vo][duck]amix=inputs=2:duration=first:normalize=0[mix];\
[mix]alimiter=limit=0.97[out]" \
  -map 0:v -map "[out]" -c:v copy -c:a aac -ac 2 -b:a 192k -shortest -movflags +faststart \
  out/hello-regrade.mp4
echo "✓ out/hello-regrade.mp4 (with music bed)"
