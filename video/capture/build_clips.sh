#!/usr/bin/env bash
# ABOUTME: Builds one 1080p VHS clip per beat from scenes.sh into video/capture/NN-*.mp4.
# ABOUTME: Measures each scene's real runtime so the clip length covers its narration.
set -euo pipefail
cd "$(dirname "$0")/.."   # video/
export PATH="$HOME/.regrade-bin:$PATH"
mkdir -p capture/tapes

BEATS=(
  "01-cold-open:title"
  "02-problem:beat_problem"
  "03-setup:beat_setup"
  "04-record:beat_record"
  "05-knobs:beat_knobs"
  "06-stress:beat_stress"
  "07-analyze:beat_analyze"
  "08-reveal:beat_reveal"
  "09-outro:outro"
)

for b in "${BEATS[@]}"; do
  name="${b%%:*}"; fn="${b##*:}"
  # Optional args restrict the rebuild to named clips (e.g. `build_clips.sh 07-rereplay`).
  if [ $# -gt 0 ] && [[ " $* " != *" $name "* ]]; then continue; fi
  TIMEFORMAT='%R'
  dur=$( { time bash capture/scenes.sh "$fn" >/dev/null 2>&1; } 2>&1 )
  sleepms=$(awk -v d="$dur" 'BEGIN{printf "%d", (d+1.3)*1000}')
  tape="capture/tapes/${name}.tape"
  cat > "$tape" <<TAPE
Output capture/${name}.mp4
Set Width ${VW:-1920}
Set Height ${VH:-1080}
Set FontSize ${VF:-32}
Set Padding ${VP:-70}
Set Theme "Catppuccin Mocha"
Set Framerate 24
Hide
Type "bash $(pwd)/capture/scenes.sh ${fn}; sleep 20"
Enter
Sleep 400ms
Show
Sleep ${sleepms}ms
TAPE
  echo "→ ${name}: scene ${dur}s, clip $(awk -v m=$sleepms 'BEGIN{printf "%.1f", m/1000}')s"
  vhs "$tape" >/dev/null 2>&1
done

echo "=== clips ==="
for f in capture/0*.mp4; do
  d=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$f")
  printf "%s  %.1fs\n" "$f" "$d"
done
