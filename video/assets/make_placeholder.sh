#!/usr/bin/env bash
# Generate a labeled 1920x1080 24fps placeholder clip so the pipeline can run
# before the real screen recording exists. Usage: make_placeholder.sh NAME LABEL SECONDS
set -euo pipefail

# This machine's ffmpeg is built without libfreetype, so the drawtext filter
# isn't available; labels are rendered with Pillow instead. Fail early with a
# clear message instead of a raw ModuleNotFoundError traceback.
if ! python3 -c 'import PIL' >/dev/null 2>&1; then
    echo "Pillow required: pip install pillow" >&2
    exit 1
fi

NAME="$1"; LABEL="$2"; SECS="${3:-4}"
OUT="$(cd "$(dirname "$0")/.." && pwd)/capture/${NAME}"
TMPDIR=$(mktemp -d)
trap "rm -rf $TMPDIR" EXIT

# Use Python with PIL to create a frame with text label
export LABEL
export FRAME_PATH="$TMPDIR/frame.png"
python3 << 'PYTHON_EOF'
import os
import sys
from PIL import Image, ImageDraw, ImageFont

label = os.environ["LABEL"]
frame_path = os.environ["FRAME_PATH"]

# Create a 1920x1080 image with dark background
img = Image.new('RGB', (1920, 1080), color=(0x1e, 0x20, 0x30))
draw = ImageDraw.Draw(img)

# Try a system font (macOS, then a common Linux path), falling back to PIL's
# built-in bitmap font if neither is present.
font = None
for font_path in (
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
):
    try:
        font = ImageFont.truetype(font_path, 54)
        break
    except OSError as e:
        print(f"warning: could not load font {font_path}: {e}", file=sys.stderr)
if font is None:
    print("warning: no system font found, falling back to PIL default font", file=sys.stderr)
    font = ImageFont.load_default()

# Draw text centered
bbox = draw.textbbox((0, 0), label, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (1920 - text_width) // 2
y = (1080 - text_height) // 2
draw.text((x, y), label, fill=(255, 255, 255), font=font)

# Save frame
img.save(frame_path)
PYTHON_EOF

# Create video from the frame, looped for the specified duration
ffmpeg -y -loop 1 -i "$TMPDIR/frame.png" -c:v libx264 -pix_fmt yuv420p -r 24 -t "$SECS" "${OUT}" >/dev/null 2>&1
echo "wrote ${OUT}"
