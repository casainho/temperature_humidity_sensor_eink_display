#!/usr/bin/env python3
"""Capture one framebuffer dump from the ESP32 serial output and render it.

The firmware prints frames wrapped in:
  FB_BEGIN counter=N len=5000
  ...
  FB_END counter=N

This script waits for the next complete frame, reconstructs the 200x200
1-bit display image, and writes a PNG.
"""

from __future__ import annotations

import argparse
import binascii
import re
import sys
import time
import tempfile
from pathlib import Path

import serial
from PIL import Image


WIDTH = 200
HEIGHT = 200
BYTES_PER_ROW = WIDTH // 8
FRAME_BYTES = BYTES_PER_ROW * HEIGHT

BEGIN_RE = re.compile(r"^FB_BEGIN counter=(\d+) len=(\d+)$")
ROW_RE = re.compile(r"^[0-9a-fA-F]{4}: ([0-9a-fA-F]+)$")


def capture_frame(ser: serial.Serial) -> tuple[int, bytes]:
    counter = None
    buf = bytearray()
    collecting = False

    while True:
        raw = ser.readline()
        if not raw:
            continue

        try:
            line = raw.decode("utf-8", "replace").strip()
        except Exception:
            continue

        if not collecting:
            m = BEGIN_RE.match(line)
            if m:
                counter = int(m.group(1))
                expected = int(m.group(2))
                if expected != FRAME_BYTES:
                    raise ValueError(f"Unexpected frame length {expected}, expected {FRAME_BYTES}")
                buf.clear()
                collecting = True
            continue

        if line.startswith("FB_END"):
            if counter is None:
                raise RuntimeError("Got FB_END without FB_BEGIN")
            if len(buf) != FRAME_BYTES:
                raise ValueError(f"Captured {len(buf)} bytes, expected {FRAME_BYTES}")
            return counter, bytes(buf)

        m = ROW_RE.match(line)
        if m:
            payload = m.group(1)
            buf.extend(binascii.unhexlify(payload))


def framebuffer_to_image(buf: bytes, reverse_bits: bool = False) -> Image.Image:
    if len(buf) != FRAME_BYTES:
        raise ValueError(f"Framebuffer size {len(buf)} does not match {FRAME_BYTES}")

    img = Image.new("L", (WIDTH, HEIGHT), 255)
    px = img.load()

    for y in range(HEIGHT):
        row_off = y * BYTES_PER_ROW
        for x in range(WIDTH):
            byte = buf[row_off + (x // 8)]
            shift = (7 - (x % 8)) if reverse_bits else (x % 8)
            bit = (byte >> shift) & 1
            px[x, y] = 255 if bit else 0

    return img


def score_image(img: Image.Image) -> int:
    """Heuristic score to pick the most plausible screen orientation."""
    bw = img.convert("L").point(lambda p: 0 if p > 128 else 1)
    px = bw.load()
    w, h = bw.size
    mid_x = w // 2
    mid_y = h // 2
    tl = sum(px[x, y] for y in range(mid_y) for x in range(mid_x))
    tr = sum(px[x, y] for y in range(mid_y) for x in range(mid_x, w))
    bl = sum(px[x, y] for y in range(mid_y, h) for x in range(mid_x))
    br = sum(px[x, y] for y in range(mid_y, h) for x in range(mid_x, w))
    return (2 * tl) + bl - tr - br


def orient_image(img: Image.Image, rotate: int = 0, flip_h: bool = False, flip_v: bool = False) -> Image.Image:
    if rotate:
        img = img.rotate(rotate, expand=True)
    if flip_h:
        img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if flip_v:
        img = img.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    return img


def save_image_atomic(img: Image.Image, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(delete=False, dir=str(out_path.parent), suffix=".png") as tmp:
        tmp_path = Path(tmp.name)
    try:
        img.save(tmp_path)
        tmp_path.replace(out_path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", default="/dev/ttyACM0", help="Serial port for the ESP32 board")
    ap.add_argument("--baud", type=int, default=115200, help="Serial baud rate")
    ap.add_argument("--output", default="latest_frame.png", help="Output image path")
    ap.add_argument("--timeout", type=float, default=10.0, help="Read timeout in seconds")
    ap.add_argument("--rotate", type=int, choices=(0, 90, 180, 270), default=0,
                    help="Rotate the rendered image before saving")
    ap.add_argument("--flip-h", action="store_true", help="Mirror the rendered image horizontally")
    ap.add_argument("--flip-v", action="store_true", help="Flip the rendered image vertically")
    ap.add_argument("--auto-orient", action="store_true",
                    help="Try all rotations/flips and bit orders, then pick a heuristic match")
    ap.add_argument("--bit-order", choices=("lsb", "msb"), default="msb",
                    help="Bit order used by the raw framebuffer bytes")
    ap.add_argument("--watch", action="store_true",
                    help="Keep capturing and overwrite the output file on every new frame")
    args = ap.parse_args()

    out_path = Path(args.output)

    def render_frame(buf: bytes) -> tuple[Image.Image, str]:
        reverse_bits = args.bit_order == "msb"
        img = framebuffer_to_image(buf, reverse_bits=reverse_bits)
        if args.auto_orient:
            best = None
            best_desc = None
            for rb in (False, True):
                raw = framebuffer_to_image(buf, reverse_bits=rb)
                for rot in (0, 90, 180, 270):
                    for fh in (False, True):
                        for fv in (False, True):
                            candidate = orient_image(raw, rotate=rot, flip_h=fh, flip_v=fv)
                            score = score_image(candidate)
                            desc = f"bits={'msb' if rb else 'lsb'} r{rot}_{'h' if fh else 'n'}{'v' if fv else ''}"
                            if best is None or score > best[0]:
                                best = (score, candidate)
                                best_desc = desc
            return best[1], f"auto-orient={best_desc}"
        img = orient_image(img, rotate=args.rotate, flip_h=args.flip_h, flip_v=args.flip_v)
        return img, f"render=bits={args.bit_order} rotate={args.rotate} flip_h={args.flip_h} flip_v={args.flip_v}"

    with serial.Serial(args.port, args.baud, timeout=args.timeout) as ser:
        ser.reset_input_buffer()
        if args.watch:
            last_counter = None
            while True:
                counter, buf = capture_frame(ser)
                if counter == last_counter:
                    continue
                img, desc = render_frame(buf)
                save_image_atomic(img, out_path)
                print(f"{desc}")
                print(f"saved {out_path} from counter={counter}")
                last_counter = counter
        else:
            counter, buf = capture_frame(ser)
            img, desc = render_frame(buf)
            save_image_atomic(img, out_path)
            print(f"{desc}")
            print(f"saved {out_path} from counter={counter}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
