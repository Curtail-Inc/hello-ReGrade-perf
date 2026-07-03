# hello-ReGrade-perf Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A public demo that teaches performance stress-testing with ReGrade — a two-version orders API whose v2 returns byte-identical bodies but is slower (one constant, one load-induced), plus a branded explainer video.

**Architecture:** Flask app served by gunicorn (1 worker, 100 threads) so `--parallel` replay load reaches the app. `APP_VERSION` env switches v1/v2. v2 adds a constant O(n²) cost to `/products` and a global `threading.Lock` around a critical section in `/orders/<id>`. Docker Compose runs v1:8001 and v2:8002. The video reuses hello-ReGrade's Remotion+VHS+TTS pipeline.

**Tech Stack:** Python 3 / Flask / gunicorn, Docker Compose, pytest, bash (traffic + video capture), Remotion (Node 22) + VHS + ElevenLabs TTS.

## Global Constraints

- Response bodies MUST be byte-identical between v1 and v2 for every request (the only difference is latency) — enforced by tests.
- Endpoints are public (no auth) — zero behavioral noise; the perf regression is the sole signal.
- Server MUST serve concurrently (gunicorn `--workers 1 --threads 100`) or the load-induced regression won't reproduce.
- The 3 replay knobs are exactly `--repeat` (≤10000), `--parallel` (≤256, ≤repeat), `--pacing` (`full_speed`|`preserve_timing`). No `--rate`/`--duration` (don't exist).
- Public repo, Apache-2.0, pushed to `Curtail-Inc/hello-ReGrade-perf` as gh user `slisteraley` (switch, then restore `penguinboi`).
- Brand red `#E0001F`; reuse hello-ReGrade video pipeline verbatim where possible.

## File Structure

- `app/store.py` — data + both endpoints; version branches. One responsibility: the demo service.
- `app/wsgi.py` — gunicorn entrypoint (`app` object).
- `gunicorn.conf.py` — 1 worker, 100 threads.
- `Dockerfile`, `docker-compose.yml` — v1/v2 on 8001/8002.
- `traffic/generate.sh` — baseline traffic driver.
- `requirements.txt` — flask, gunicorn, (dev) pytest, requests.
- `tests/test_store.py` — identical-bodies + endpoint tests.
- `README.md`, `CLAUDE.md`, `LICENSE`.
- `video/` — copied+adapted hello-ReGrade pipeline (Phase 2).

---

### Task 1: The service — identical bodies, both endpoints (v1 behavior)

**Files:** Create `app/store.py`, `app/wsgi.py`, `requirements.txt`, `tests/test_store.py`.

**Interfaces:**
- Produces: a Flask `app` (in `store.py`, imported by `wsgi.py`); `GET /products` → `{"products":[...]}`; `GET /orders/<int:oid>` → one order dict; `GET /health` → `{"ok":true}`. `APP_VERSION` env (`v1`/`v2`, default `v1`) selects timing behavior. Data is deterministic (seeded) so bodies are stable.

- [ ] **Step 1 — failing test:** `tests/test_store.py`: import `store.app`, use `app.test_client()`; assert `/products` returns 200 and a stable JSON shape (e.g. 24 products, each `{id,name,price,category}`), `/orders/1001` returns 200 with `{id,items,subtotal,tax,total}`. Add the key test: `test_v1_and_v2_bodies_identical` — spin the client with `APP_VERSION=v1` and `v2` (reload module / factory), request the same paths, assert `resp_v1.data == resp_v2.data`.
- [ ] **Step 2 — run, expect fail** (`store` missing).
- [ ] **Step 3 — implement `store.py`:** seeded in-memory `PRODUCTS` (24 items) + `ORDERS` (a few ids). Endpoints build responses with **sorted keys, fixed float formatting** so bytes are stable. `APP_VERSION` read at import; v1 path = fast. Include `/health`.
- [ ] **Step 4 — run, expect pass.**
- [ ] **Step 5 — commit** `feat: two-version orders API with identical response bodies`.

### Task 2: v2 regressions — constant slowdown + load-induced lock

**Files:** Modify `app/store.py`; add `tests/test_store.py::test_v2_slower_*` (timing sanity, tolerant).

**Interfaces:** Consumes Task 1's endpoints. Produces: in v2 only, `/products` does an O(n²) re-sort adding ~35ms; `/orders/<id>` acquires a module-global `threading.Lock()` around an ~8ms critical section (busy-work loop calibrated to ~8ms, NOT sleep, so it's CPU-real). v1 does the same critical work **without** the global lock.

- [ ] **Step 1 — failing test:** `test_v2_products_slower` — measure wall time of `/products` under v1 vs v2 (single call), assert v2 ≥ v1 + 20ms. `test_bodies_still_identical` re-asserted. (Load-induced contention is validated live in Task 6, not unit-tested — hard to reproduce deterministically in-process.)
- [ ] **Step 2 — run, expect fail.**
- [ ] **Step 3 — implement:** guard both regressions behind `APP_VERSION=="v2"`. Constant: a documented O(n²) sort of the product list. Lock: `_ORDER_LOCK = threading.Lock()`; v2 wraps the critical section `with _ORDER_LOCK:`; comment explains it simulates a serialized shared-resource access. Calibrate busy-work to ~8ms on a modern CPU.
- [ ] **Step 4 — run, expect pass.**
- [ ] **Step 5 — commit** `feat: v2 constant + load-induced latency regressions`.

### Task 3: gunicorn + Docker (concurrent serving, v1:8001 / v2:8002)

**Files:** Create `gunicorn.conf.py` (`workers=1, threads=100, bind` from `PORT`), `Dockerfile`, `docker-compose.yml`.

- [ ] **Step 1:** `gunicorn.conf.py` — 1 worker, 100 threads, `timeout=120`.
- [ ] **Step 2:** `Dockerfile` — python:3.12-slim, install requirements, `CMD gunicorn -c gunicorn.conf.py app.wsgi:app`.
- [ ] **Step 3:** `docker-compose.yml` — service `v1` (`APP_VERSION=v1`, port 8001), service `v2` (`APP_VERSION=v2`, port 8002).
- [ ] **Step 4 — verify:** `docker compose up -d --build`; `curl :8001/health` and `:8002/health` → ok; `curl -s :8001/products | sha256` == `:8002/products | sha256` (bytes identical).
- [ ] **Step 5 — commit** `feat: dockerized concurrent serving for v1 and v2`.

### Task 4: traffic generator

**Files:** Create `traffic/generate.sh` + `tests/test_traffic.py` (script exists, is executable, references both endpoints).

- [ ] **Step 1 — failing test** (script missing / not referencing `/orders` and `/products`).
- [ ] **Step 2:** implement `generate.sh` — `TARGET` default `http://localhost:19870`; health-check `/health`; hit `/products` a few times and `/orders/<id>` for a couple ids; echo progress; `set -euo pipefail`.
- [ ] **Step 3 — run test, expect pass; smoke-run against `:8001`.**
- [ ] **Step 4 — commit** `feat: traffic generator for the baseline recording`.

### Task 5: README + CLAUDE.md + LICENSE

**Files:** Create `README.md`, `CLAUDE.md`, `LICENSE` (Apache-2.0).

- [ ] **Step 1:** `README.md` — prerequisites (account, API key, sensor install, MCP plugin), `docker compose up`, record, **stress-replay `--repeat 500 --parallel 50 --pacing full_speed`**, analyze in Claude Code (`summarize_deltas`=0 behavioral, `analyze_replay_performance`=regressions), the `--parallel 1` vs `--parallel 50` reveal. Mirror hello-ReGrade's README structure.
- [ ] **Step 2:** `CLAUDE.md` — tutor: narrate before each tool call; define latency/p95/p99/the 3 knobs; use `summarize_deltas` then `analyze_replay_performance`; **do NOT pre-empt the finding**; teach the load reveal.
- [ ] **Step 3:** `LICENSE` Apache-2.0.
- [ ] **Step 4 — commit** `docs: README, tutor CLAUDE.md, license`.

### Task 6: LIVE VALIDATION (must pass before the video)

**Files:** none (operational). Uses the real sensor (`~/.regrade-bin`), API key (`~/.regrade/key` or REGRADE_API_KEY), alpha (`app.regrade.curtail.com`), and the ReGrade MCP.

- [ ] **Step 1:** `docker compose up -d --build`.
- [ ] **Step 2:** record v1: `regrade proxy --target http://localhost:8001 --port 19870` + `TARGET=http://localhost:19870 ./traffic/generate.sh`; Ctrl-C → Recording ID.
- [ ] **Step 3:** single-shot replay v2 `--parallel 1` → note `/orders` is NOT yet a significant regression.
- [ ] **Step 4:** stress replay v2 `--repeat 500 --parallel 50 --pacing full_speed`.
- [ ] **Step 5:** via MCP: `summarize_deltas` → assert **0 behavioral deltas**; `analyze_replay_performance` → assert BOTH endpoints `direction: slower`, p<0.05; `/orders` significant only under load. If any assertion fails, tune the regression magnitudes / thread count / knob values until it reproduces cleanly. Record the exact IDs + numbers for the video.
- [ ] **Step 6 — commit** any tuning; write findings (IDs, latencies) into a scratch note for the video.

### Task 7 (Phase 2): The video — adapt the hello-ReGrade pipeline

**Files:** copy `hello-ReGrade/video/{remotion,capture/scenes.sh helpers,build.sh,regen_beat.sh,build_episode.py,tts.py,lib,tests}` → `hello-ReGrade-perf/video/`; new `video/script.json`, new `video/capture/scenes.sh` beats.

- [ ] **Step 1:** copy the pipeline; keep BrandCard/Captions/Highlights/SectionTag/CardBackdrop/OutroCard/theme; adjust as needed.
- [ ] **Step 2:** new `script.json` beats: brand → problem (perf slips past tests, esp. under load) → record → stress-replay (the 3 knobs) → summarize_deltas=0 / analyze_replay_performance regressions → the `--parallel 1` vs `--parallel 50` reveal → CTA.
- [ ] **Step 3:** new `scenes.sh` terminal scenes using the REAL numbers from Task 6.
- [ ] **Step 4:** build clips → TTS (`~/.config/elevenlabs/key`) → episode → Remotion render → music mix; verify frames; Desktop copy.
- [ ] **Step 5 — commit** `feat: branded performance stress-test explainer video`.

### Task 8: Ship

- [ ] Push repo to `Curtail-Inc/hello-ReGrade-perf` (create public repo via gh as `slisteraley`; restore `penguinboi`). Verify tests green before push.

---

## Self-Review

- **Spec coverage:** app (T1–T3), traffic (T4), docs/tutor (T5), the 3 knobs + perf-only regression + load reveal (T5/T6), live validation (T6), video (T7), ship (T8). ✓
- **Placeholders:** none — timing magnitudes and knob values are concrete; live tuning is an explicit step, not a TODO.
- **Type consistency:** endpoints `/products`, `/orders/<id>`, `/health` and `APP_VERSION` v1/v2 used consistently across tasks.
