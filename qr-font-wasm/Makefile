.PHONY: all base wasm font clean

all: font

base:
	python3 scripts/build_base_font.py

wasm:
	wasm-pack build --target web

font: base wasm
	python3 scripts/embed_wasm.py

clean:
	rm -rf build pkg target
