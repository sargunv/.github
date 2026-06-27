#!/usr/bin/env python3
"""Render hb-shape WASM output as a PNG QR code image."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "build" / "QRFont-Wasm.ttf"
HB_SHAPE = os.environ.get("HB_SHAPE", "/usr/local/bin/hb-shape")
MODULE = 40


def parse_hb_shape(text: str, shaped: str) -> tuple[list[tuple[int, int, int]], int]:
    """Return (glyph_id, cluster, x_offset, y_offset) tuples and total advance."""
    glyphs: list[tuple[int, int, int]] = []
    total_advance = 0
    for part in shaped.strip().strip("[]").split("|"):
        if not part:
            continue
        # glyph=cluster+x_offset,y_offset@x_advance,y_advance
        m = re.match(
            r"(?P<gid>\d+)=(?P<cluster>\d+)"
            r"(?:@(?P<xo>-?\d+),(?P<yo>-?\d+))?"
            r"(?:\+(?P<xa>-?\d+),(?P<ya>-?\d+))?",
            part,
        )
        if not m:
            continue
        gid = int(m.group("gid"))
        cluster = int(m.group("cluster"))
        xo = int(m.group("xo") or 0)
        yo = int(m.group("yo") or 0)
        if m.group("xa") is not None:
            total_advance = max(total_advance, xo + int(m.group("xa")))
        glyphs.append((gid, cluster, xo, yo))
    return glyphs, total_advance


def main() -> None:
    text = sys.argv[1] if len(sys.argv) > 1 else "hello world"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "demo" / "qr-demo.png"
    out.parent.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["LD_LIBRARY_PATH"] = "/usr/local/lib/x86_64-linux-gnu:" + env.get(
        "LD_LIBRARY_PATH", ""
    )

    proc = subprocess.run(
        [HB_SHAPE, "--shaper=wasm", "--font-size=16", "--no-glyph-names", str(FONT)],
        input=text.encode(),
        capture_output=True,
        env=env,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(proc.stderr.decode() or "hb-shape failed")

    shaped = proc.stdout.decode().strip()
    glyphs, advance = parse_hb_shape(text, shaped)

    modules = [(xo, yo) for gid, _c, xo, yo in glyphs if gid == 2]
    size = advance or (max((x for x, _ in modules), default=0) + MODULE)
    height = max((y for _, y in modules), default=0) + MODULE

    scale = 4
    img = Image.new("RGB", (size * scale, height * scale), "white")
    draw = ImageDraw.Draw(img)
    for x, y in modules:
        draw.rectangle(
            [
                x * scale,
                y * scale,
                (x + MODULE) * scale - 1,
                (y + MODULE) * scale - 1,
            ],
            fill="black",
        )

    img.save(out)
    print(f"Input: {text!r}")
    print(f"hb-shape: {len(glyphs)} glyphs ({len(modules)} modules + spacer)")
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
