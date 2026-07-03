# hello-ReGrade-perf

A hands-on demo of **performance stress-testing with [ReGrade](https://app.regrade.curtail.com)**.
You'll record a baseline against one version of a tiny service, **replay it under load**
against a "new version," and use **Claude Code + the ReGrade MCP tools** to catch a
**performance-only regression** — one that returns identical data, just slower, and that
functional tests can't see.

The twist: one endpoint is *always* a bit slower, and one is only slow **under concurrency**.
The second is invisible to a single-shot replay — you need the load knob to expose it.

## What you'll need

- **Docker** (for the demo service) and **curl** (for the traffic script).
- A **ReGrade account + API key** — sign up at https://app.regrade.curtail.com, install the
  `regrade` sensor from https://app.regrade.curtail.com/downloads, and set `REGRADE_API_KEY`
  (or `~/.regrade/key`).
- **Claude Code** with the ReGrade plugin:
  `claude plugin marketplace add https://app.regrade.curtail.com/downloads/latest/marketplace.json`
  then `claude plugin install regrade@regrade --scope user`, and connect it once (`/mcp`,
  signed into the same account as your key).

## The demo service

Two versions of a small read-only "orders" API. Both return **byte-identical JSON** — the
only difference is *how fast*:

- **v1** on `http://localhost:8001` — you record against this (the baseline).
- **v2** on `http://localhost:8002` — you replay against this (the "new version").

| Endpoint | v2's regression |
|---|---|
| `GET /products` | **Constant** — an inefficient synchronous re-validation adds a fixed ~35 ms to every call. |
| `GET /orders/<id>` | **Load-induced** — a global lock added "for thread-safety" serializes the hot path. Fine one request at a time; catastrophic under concurrency. |

The endpoints are **public** — no auth, so there's no behavioral noise. The regression is
*pure latency*.

```bash
git clone https://github.com/Curtail-Inc/hello-ReGrade-perf
cd hello-ReGrade-perf
docker compose up -d --build
```

## 1. Record a baseline against v1

In one terminal, start the sensor proxy in front of v1:

```bash
regrade proxy --target http://localhost:8001 --port 19870
```

In another, generate some traffic *through the proxy* (this recording is sequential — the
load comes later, from the replay):

```bash
TARGET=http://localhost:19870 ./traffic/generate.sh
```

Stop the proxy (Ctrl-C). The recording uploads and prints a `Recording ID: <uuid>` — note it.

## 2. Stress-replay against v2 — the three knobs

ReGrade's replay has three knobs for turning a recording into a load test:

- `--repeat <N>` — run the recording N times (piles up latency samples → statistical confidence).
- `--parallel <N>` — N **concurrent** replay sessions (this is the load).
- `--pacing full_speed|preserve_timing` — max pressure, or reproduce the original think-time.

Hammer v2:

```bash
regrade replay --rec-id <RECORDING_ID> --target http://localhost:8002 \
  --repeat 500 --parallel 50 --pacing full_speed
```

## 3. Read the result in Claude Code

Open this repo in Claude Code and ask it to walk you through the replay. Guided by this
repo's `CLAUDE.md`, it will:

- run `summarize_deltas` → **zero behavioral deltas** (nothing about the *responses* changed), then
- run `analyze_replay_performance` → both endpoints come back **`slower`**, with p50/p95/p99,
  a percent change, and a significance test. That's the regression — visible only in the
  performance surface.

## 4. Why the load knob matters

Replay `/orders/<id>` again at **`--parallel 1`** and it looks *fine* — as fast as v1. Then
crank **`--parallel 50`** and it falls apart. That's the load-induced regression: a lock that
never shows up in a functional test or a single-request check, only under real concurrency.
**That's the point of stress-replay.**

## How the versions differ

`app/store.py` is one file switched by `APP_VERSION`. Curious what changed? Look *after* you've
found it with ReGrade — the point is that ReGrade caught it from **traffic and timing alone**.

## License

Apache-2.0.
