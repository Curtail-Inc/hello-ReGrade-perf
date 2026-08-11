#!/usr/bin/env bash
# ABOUTME: Moves the video source assets between this checkout and private S3 storage.
# ABOUTME: Usage: aws-vault exec curtail -- ./sync-assets.sh [pull|push]
#
# Clips, music and voiceovers are gitignored because they are large binaries, so
# a fresh clone cannot rebuild any video without them. They live in
# s3://curtail-shares/video-assets/ instead, which is private: that bucket only
# grants CloudFront access to public/*, so nothing here is reachable from a CDN.
#
# pull  fetch what this checkout is missing (what you want after cloning)
# push  upload what you have changed (after re-cutting a clip or re-recording)
#
# Neither direction deletes. Removing an asset is deliberate enough to be done by
# hand, and a stray delete here would destroy the only copy of a recording.
set -euo pipefail
cd "$(dirname "$0")"

BUCKET="${VIDEO_ASSET_BUCKET:-curtail-shares}"
PREFIX="${VIDEO_ASSET_PREFIX:-video-assets/hello-ReGrade-perf}"
REMOTE="s3://${BUCKET}/${PREFIX}"

MODE="${1:-pull}"

command -v aws >/dev/null || { echo "aws CLI not found" >&2; exit 1; }
aws sts get-caller-identity >/dev/null 2>&1 || {
  echo "No AWS credentials. Curtail uses aws-vault:" >&2
  echo "  aws-vault exec curtail -- $0 $MODE" >&2
  exit 1
}

# Only the inputs a build consumes. Rendered output stays out: it is derived, and
# out/ is where a build writes.
FILTERS=(--exclude "*" --include "*.mp4" --include "*.mp3" --include "*timestamps*.json")

case "$MODE" in
  pull)
    echo "pulling ${REMOTE}/ -> capture/"
    mkdir -p capture
    aws s3 sync "${REMOTE}/capture/" capture/ "${FILTERS[@]}"
    ;;
  push)
    echo "pushing capture/ -> ${REMOTE}/"
    aws s3 sync capture/ "${REMOTE}/capture/" "${FILTERS[@]}"
    ;;
  *)
    echo "usage: $0 [pull|push]" >&2
    exit 1
    ;;
esac

echo "✓ ${MODE} complete"
