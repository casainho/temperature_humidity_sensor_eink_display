#!/usr/bin/env sh

set -eu

PORT="${1:-/dev/ttyACM0}"
OUT="${2:-latest_screen.png}"

exec python3 "$(dirname "$0")/capture_fb_image.py" \
  --port "$PORT" \
  --watch \
  --output "$OUT"
