# hello-ReGrade-perf — Design

**Goal:** A public, hands-on demo that teaches how to **stress-test endpoint performance with ReGrade** — record a baseline, replay it against a "new version" under load using the three replay knobs, and surface a **performance-only regression** that behavioral/functional tests can't catch. Ships with a branded ~3–4 min explainer video.

**Why it matters:** ReGrade's replay measures per-request latency and compares it to the recorded baseline (Welch t-test + Cohen's d) via `analyze_replay_performance`. A v2 that returns **byte-identical responses but is slower** produces **zero** behavioral deltas (`summarize_deltas`/`query_deltas` = 0) — the regression exists *only* in the performance surface. And a regression that only degrades **under load** is invisible to a single-shot replay; you need the concurrency knob to expose it.

## The three replay knobs (from the product)

- `--repeat <N>` (default 1, max 10000) — execute the recording N times; piles up latency samples → statistical confidence.
- `--parallel <N>` (default 1, max 256, must be ≤ repeat) — N concurrent replay sessions → **real load**.
- `--pacing <full_speed|preserve_timing>` — max pressure vs. original inter-request think-time.

Stress config = `--repeat 500 --parallel 50 --pacing full_speed`.

## Architecture

Two versions of a tiny read-only "orders" API, switched by `APP_VERSION`, run by Docker Compose:

- **v1** → `http://localhost:8001` (record against this — the baseline)
- **v2** → `http://localhost:8002` (replay against this — the "new version")

Both versions return **identical JSON** for every request. The only difference is *latency*. **Endpoints are public (no auth)** — deliberately, so there is zero behavioral noise and the performance regression is the sole signal.

### The server (critical enabler)

The app is **Flask served by gunicorn with one worker and many threads** (`--workers 1 --threads 100`). One worker so a `threading.Lock` in v2 is a single shared contention point; many threads so `--parallel` up to ~50 genuinely reaches the app concurrently. Without real server concurrency, the *server* (not v2's lock) would be the bottleneck and `--parallel` would do nothing.

### The two regressions (v2 only; bodies unchanged)

| Endpoint | Response | v1 timing | v2 regression | Surfaces at |
|---|---|---|---|---|
| `GET /products` | product list (identical) | ~5 ms | **Constant slowdown** — an O(n²) re-sort / inefficient re-serialize adds a fixed ~35 ms every call | even `--parallel 1` |
| `GET /orders/<id>` | one order (identical) | ~8 ms | **Load-induced** — a global `threading.Lock` wraps an ~8 ms critical section (a "thread-safety fix" that serialized the hot path). v1 does the same work *without* the global lock | fine `--parallel 1`, balloons `--parallel 50` |

The load-induced endpoint is the star: at `--parallel 1` v2 ≈ v1; at `--parallel 50`, v2's requests queue on the lock (last one waits ~N×8 ms) while v1's run concurrently.

## Components

- `app/store.py` — single file, both versions via `APP_VERSION` env. Shared data + the two endpoints; v2 branches add the constant work and the global lock. Byte-identical response bodies asserted by tests.
- `app/wsgi.py` (or gunicorn target) + gunicorn config (1 worker, 100 threads).
- `Dockerfile` + `docker-compose.yml` — v1/v2 containers on 8001/8002 with `APP_VERSION` set; gunicorn command.
- `traffic/generate.sh` — drives baseline traffic through the sensor proxy: hits `/products` and `/orders/<id>` a handful of times. `TARGET` overridable (proxy vs direct).
- `README.md` — the walkthrough: prerequisites (account, API key, sensor, MCP plugin), record, **stress-replay with the 3 knobs**, analyze in Claude Code, the `--parallel 1` vs `--parallel 50` reveal.
- `CLAUDE.md` — tutor file: guide a first-timer, narrate before each MCP tool call, define terms (latency, p95/p99, regression, the 3 knobs), **do NOT pre-empt the finding**, use `summarize_deltas` (0 behavioral) then `analyze_replay_performance` (the regressions), and teach the load reveal.
- `tests/` — pytest: both versions return the exact same bodies for the same requests; the traffic script is well-formed; (optional) a local timing sanity check that v2 is measurably slower under simulated concurrency.
- `video/` — reused hello-ReGrade Remotion + VHS + TTS pipeline (BrandCard, scenes helpers, build.sh, regen_beat.sh, captions, music, CTA) with a new `script.json` + `scenes.sh` for the perf narrative.

## The demo workflow (what the README + video teach)

1. `docker compose up -d --build` → v1:8001, v2:8002.
2. **Record:** `regrade proxy --target http://localhost:8001 --port 19870` + `TARGET=http://localhost:19870 ./traffic/generate.sh` → Recording ID.
3. **Stress-replay v2:** `regrade replay --rec-id <id> --target http://localhost:8002 --repeat 500 --parallel 50 --pacing full_speed`.
4. In Claude Code (ReGrade MCP): `summarize_deltas` → **0 behavioral deltas** ("nothing changed… and yet"), then `analyze_replay_performance` → both endpoints `direction: slower`, p<0.05, p95/p99, % change.
5. **The reveal:** replay once at `--parallel 1` → `/orders/<id>` looks fine → crank `--parallel 50` → it degrades. That's the load-induced regression functional tests miss.

## The video (~3–4 min, branded)

Reuse the hello-ReGrade pipeline. Narrative beats: brand open → the problem (perf regressions slip past tests, especially under load) → the record→stress-replay→analyze loop → the 3 knobs on screen → `summarize_deltas` shows 0 behavioral / `analyze_replay_performance` shows the regressions → the `--parallel 1` vs `--parallel 50` reveal → why it matters → CTA (curtail.com free account).

## Testing & validation

- **Unit:** pytest asserts v1 and v2 return identical bodies for `/products` and `/orders/<id>`.
- **Smoke:** traffic script reaches the app and exits 0.
- **Live validation (must pass before shipping):** actually run record → stress-replay → `analyze_replay_performance` against alpha (`app.regrade.curtail.com`) with the real sensor + API key + MCP, and confirm: `summarize_deltas` = 0 behavioral deltas, and both endpoints show a significant `slower` regression; confirm `/orders/<id>` is *not* significant at `--parallel 1` but *is* at `--parallel 50`.
- **Video:** script/build tests like hello-ReGrade (`test_script.py`, remotion smoke render).

## Out of scope (YAGNI)

- No auth / token mapping (that's the behavioral demo's lesson; here it would only add noise).
- No write endpoints, no database — in-memory data is enough to demonstrate latency.
- No `--rate`/RPS or `--duration` flags — the product doesn't have them; throughput is governed by `--parallel` + `--pacing`.
