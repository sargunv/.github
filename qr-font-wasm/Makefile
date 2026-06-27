.PHONY: all base wasm font clean

WASM_SRC=target/wasm32-unknown-unknown/release/qr_font_wasm.wasm
WASM_OUT=build/qr_shaper.wasm

all: font

base:
	python3 scripts/build_base_font.py

wasm:
	cargo build --release --target wasm32-unknown-unknown
	cp $(WASM_SRC) $(WASM_OUT)

font: base wasm
	python3 scripts/embed_wasm.py build/QRBase.ttf $(WASM_OUT) build/QRFont-Wasm.ttf

clean:
	rm -rf build pkg target
