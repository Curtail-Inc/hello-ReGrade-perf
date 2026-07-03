#!/usr/bin/env bash
# ABOUTME: Drive baseline traffic through the sensor proxy so ReGrade records it.
# ABOUTME: Sequential by design — the stress/concurrency comes later from `regrade replay --parallel`.
set -euo pipefail

TARGET="${TARGET:-http://localhost:19870}"

if ! curl -sf "${TARGET}/products" >/dev/null 2>&1; then
  echo "✗ Can't reach ${TARGET}." >&2
  echo "  Make sure the demo is up (docker compose up -d) and, for recording," >&2
  echo "  that the sensor proxy is running on that port." >&2
  exit 1
fi

echo "→ GET /products  ×15"
for _ in $(seq 1 15); do
  curl -sSf "${TARGET}/products" >/dev/null
done

echo "→ GET /orders/{1001,1002,1003}  ×5 each"
for _ in $(seq 1 5); do
  for id in 1001 1002 1003; do
    curl -sSf "${TARGET}/orders/${id}" >/dev/null
  done
done

echo "✓ traffic complete — recording captured a baseline of both endpoints"
echo "  Next: stress-replay it against v2 with  --repeat 500 --parallel 50 --pacing full_speed"
