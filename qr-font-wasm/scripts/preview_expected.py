#!/usr/bin/env python3
"""Preview the glyph grid the WASM shaper would emit (no HarfBuzz required)."""

from __future__ import annotations

import sys

import qrcode as qrlib

MODULE = 40


def main() -> None:
    text = sys.argv[1] if len(sys.argv) > 1 else "https://example.com"
    code = qrlib.QRCode(border=0)
    code.add_data(text)
    code.make(fit=True)
    matrix = code.get_matrix()
    width = len(matrix)
    modules = sum(row.count(True) for row in matrix)
    qr_width = width * MODULE
    print(f"Input: {text!r}")
    print(f"QR version: {width}×{width} modules")
    print(f"Dark modules → glyph 2 with offsets: {modules}")
    print(f"Trailing glyph 1 (space) x_advance: {qr_width}")
    print()
    print("First 5 module glyphs (glyph_id, x_offset, y_offset):")
    shown = 0
    for y, row in enumerate(matrix):
        for x, dark in enumerate(row):
            if not dark:
                continue
            print(f"  2  {x * MODULE:4d}  {y * MODULE:4d}")
            shown += 1
            if shown >= 5:
                print("  ...")
                return


if __name__ == "__main__":
    main()
