#!/usr/bin/env python3
"""Embed compiled WASM into the base font's Wasm OpenType table."""

from __future__ import annotations

import sys
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables.DefaultTable import DefaultTable


class WasmTable(DefaultTable):
    """Raw WASM bytecode table consumed by HarfBuzz's WASM shaper."""

    def decompile(self, data: bytes, ttFont) -> None:
        self.data = data

    def compile(self, ttFont) -> bytes:
        return self.data


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    base = root / "build" / "QRBase.ttf"
    wasm_path = root / "pkg" / "qr_font_wasm_bg.wasm"
    out = root / "build" / "QRFont-Wasm.ttf"

    if len(sys.argv) == 4:
        base, wasm_path, out = (Path(p) for p in sys.argv[1:4])

    if not base.exists():
        raise SystemExit(f"Missing base font: {base}")
    if not wasm_path.exists():
        raise SystemExit(f"Missing WASM binary: {wasm_path}")

    wasm_bytes = wasm_path.read_bytes()
    font = TTFont(base)
    font["Wasm"] = WasmTable("Wasm")
    font["Wasm"].data = wasm_bytes
    font.save(out)
    print(f"Wrote {out} ({len(wasm_bytes)} byte Wasm table)")


if __name__ == "__main__":
    main()
