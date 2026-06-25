#!/usr/bin/env python3
"""Build MicroPython font modules from source fonts in a local folder.

This scans a source directory for font files and uses `tools/font_to_py.py`
to generate Python font modules into an output directory.

Expected naming:
  - Fonts with a pixel height encoded in the filename, e.g. `Roboto-Bold36.ttf`
    or `roboto36.otf`, will have the trailing number used as the height.
  - `bdf` and `pcf` sources use height 0, as the height comes from the file.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


FONT_EXTS = {".ttf", ".otf", ".bdf", ".pcf"}
HEIGHT_RE = re.compile(r"(\d+)$")


def infer_height(path: Path) -> int:
    if path.suffix.lower() in {".bdf", ".pcf"}:
        return 0
    m = HEIGHT_RE.search(path.stem)
    if not m:
        raise ValueError(
            f"Cannot infer height from {path.name}. "
            "Rename it so the stem ends with the pixel height, e.g. RobotoBold36.ttf."
        )
    return int(m.group(1))


def iter_sources(source_dir: Path):
    for path in sorted(source_dir.iterdir()):
        if path.is_file() and path.suffix.lower() in FONT_EXTS:
            yield path


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-dir", default="fonts", help="Directory containing source font files")
    ap.add_argument("--output-dir", default="firmware/fonts", help="Directory for generated .py fonts")
    ap.add_argument("--converter", default="tools/font_to_py.py", help="Path to the vendored font_to_py.py")
    ap.add_argument("--no-xmap", action="store_true", help="Do not pass -x to the converter")
    ap.add_argument("--dry-run", action="store_true", help="Print the conversions without running them")
    args = ap.parse_args()

    source_dir = Path(args.source_dir)
    output_dir = Path(args.output_dir)
    converter = Path(args.converter)

    if not source_dir.exists():
        print(f"Source directory not found: {source_dir}", file=sys.stderr)
        return 1
    if not converter.exists():
        print(f"Converter not found: {converter}", file=sys.stderr)
        return 1

    sources = list(iter_sources(source_dir))
    if not sources:
        print(f"No font sources found in {source_dir}", file=sys.stderr)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    for src in sources:
        height = infer_height(src)
        out = output_dir / f"{src.stem.lower()}.py"
        cmd = [sys.executable, str(converter)]
        if not args.no_xmap:
            cmd.append("-x")
        cmd.extend([str(src), str(height), str(out)])
        print(" ".join(cmd))
        if not args.dry_run:
            subprocess.run(cmd, check=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
