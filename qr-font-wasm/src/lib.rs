//! HarfBuzz WASM shaper: turn typed text into a positioned grid of QR modules.
//!
//! Glyph IDs expected in the base font:
//!   1 = space (advance carrier)
//!   2 = filled module square (zero advance; positioned with offsets)

use harfbuzz_wasm::{Glyph, GlyphBuffer};
use qrcode::{Color, QrCode};
use wasm_bindgen::prelude::*;

const GLYPH_SPACE: u32 = 1;
const GLYPH_MODULE: u32 = 2;

/// Module size in font units. The base font is built at 1000 UPEM.
const MODULE_SIZE: i32 = 40;

#[wasm_bindgen]
pub fn shape(
    _shape_plan: u32,
    _font_ref: u32,
    buf_ref: u32,
    _features: u32,
    _num_features: u32,
) -> i32 {
    let buffer = GlyphBuffer::from_ref(buf_ref);

    let text: String = buffer
        .glyphs
        .iter()
        .map(|g| char::from_u32(g.codepoint).unwrap_or('?'))
        .collect();

    let text = text.trim();
    if text.is_empty() {
        return 1;
    }

    let Ok(code) = QrCode::new(text.as_bytes()) else {
        return 0;
    };

    let width = code.width();
    let qr_width = (width as i32) * MODULE_SIZE;
    let mut glyphs = Vec::new();
    let mut cluster = 0u32;

    for y in 0..width {
        for x in 0..width {
            if code[(x, y)] != Color::Dark {
                continue;
            }
            glyphs.push(Glyph {
                codepoint: GLYPH_MODULE,
                flags: 0,
                cluster,
                x_advance: 0,
                y_advance: 0,
                x_offset: x as i32 * MODULE_SIZE,
                y_offset: y as i32 * MODULE_SIZE,
            });
            cluster += 1;
        }
    }

    // Carriage return: one space glyph whose advance equals the QR bounding box.
    glyphs.push(Glyph {
        codepoint: GLYPH_SPACE,
        flags: 0,
        cluster,
        x_advance: qr_width,
        y_advance: 0,
        x_offset: 0,
        y_offset: 0,
    });

    let mut out = GlyphBuffer::from_ref(buf_ref);
    out.glyphs = glyphs;
    1
}
