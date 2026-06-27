#!/usr/bin/env python3
"""Build a minimal base font for the QR WASM shaper."""

from __future__ import annotations

import struct
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen


UPEM = 1000
MODULE = 40  # matches MODULE_SIZE in src/lib.rs


def square_glyph(size: float) -> object:
    pen = TTGlyphPen(None)
    pen.moveTo((0, 0))
    pen.lineTo((size, 0))
    pen.lineTo((size, size))
    pen.lineTo((0, size))
    pen.closePath()
    return pen.glyph()


def space_glyph() -> object:
    pen = TTGlyphPen(None)
    return pen.glyph()


def main() -> None:
    out = Path(__file__).resolve().parent.parent / "build" / "QRBase.ttf"
    out.parent.mkdir(parents=True, exist_ok=True)

    fb = FontBuilder(UPEM, isTTF=True)
    fb.setupGlyphOrder([".notdef", "space", "module"])
    fb.setupCharacterMap({0x20: "space", 0x2588: "module"})  # █ as module fallback
    fb.setupGlyf(
        {
            ".notdef": space_glyph(),
            "space": space_glyph(),
            "module": square_glyph(MODULE),
        }
    )
    fb.setupHorizontalMetrics(
        {
            ".notdef": (UPEM // 2, 0),
            "space": (UPEM // 4, 0),
            "module": (0, 0),
        }
    )
    fb.setupHorizontalHeader(ascent=900, descent=-100)
    fb.setupOS2(sTypoAscender=900, sTypoDescender=-100, usWinAscent=900, usWinDescent=100)
    fb.setupPost()
    fb.setupNameTable({"familyName": "QRBase", "styleName": "Regular"})
    fb.setupHead()
    fb.save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
