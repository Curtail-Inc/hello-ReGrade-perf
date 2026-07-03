# hello-ReGrade demo video

A ~90-second captioned + voiced walkthrough of the hello-ReGrade workflow —
record → replay → map the rotating token → the hidden order-total regression appears.
Built **programmatically** so it regenerates from source; no manual video editing.

Pipeline:

```
capture/scenes.sh      styled terminal + Claude-Code/MCP "scenes" (all numbers are real,
                       captured from live record/replay/summarize_deltas runs)
capture/build_clips.sh VHS renders each scene → capture/NN-*.mp4 (1080p)
tts.py                 ElevenLabs word-timestamped voiceover → capture/voiceover.mp3 + timestamps.json
build_episode.py       per-beat durations from the VO + karaoke caption cues → out/episode.json
remotion/              <Series> of beat clips + word-level captions → out/silent.mp4
ffmpeg                 mux the voiceover → out/hello-regrade.mp4  (1920×1080, 24fps)
```

## Prerequisites

- **Node 22+** (Remotion render) and **[VHS](https://github.com/charmbracelet/vhs)** (`brew install vhs`) for the terminal clips.
- **Python 3** venv with the pipeline deps:
  ```bash
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt   # elevenlabs + edge-tts
  ```
- `ELEVENLABS_API_KEY` in the environment (build-time only — never committed).

## Regenerate the video

```bash
# 1. render the terminal clips from the scenes
bash capture/build_clips.sh

# 2. voiceover + episode + Remotion render + mux
export ELEVENLABS_API_KEY=<your-key>
./build.sh
# → out/hello-regrade.mp4
```

To change wording, edit `capture/scenes.sh` (on-screen text) and `script.json` (voiceover),
keeping the two in sync, then re-run both steps.

## Notes

- **Everything shown is real data** — the delta counts (22 → 3), the `$.total 46.20 → 42.00`
  regression, and the profile/replay IDs come from actual `regrade record`/`replay` +
  `summarize_deltas` runs against the demo. The scenes replay that data cleanly rather than
  screen-recording a live TUI, so the video is deterministic and regenerable.
- The canonical mapping profile is `hello-regrade-demo` (id-mapping on `$.token` +
  a pattern-based `Authorization: Bearer` header transform with a `captures` group).
- `capture/*` clips, `out/`, and the generated `capture/tapes/` are gitignored.
