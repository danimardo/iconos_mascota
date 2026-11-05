#!/usr/bin/env python3
"""Empaqueta manifest, .riv y WASM para abrir el visor incluso con file://."""
from __future__ import annotations

import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((ROOT / "manifest.json").read_text())
RIVS = [*MANIFEST["icons"], MANIFEST["mascot"]]
FILES = {item["riv"]: base64.b64encode((ROOT / item["riv"]).read_bytes()).decode("ascii") for item in RIVS}
WASM = base64.b64encode((ROOT / "visor/vendor/rive.wasm").read_bytes()).decode("ascii")
PAYLOAD = {"manifest": MANIFEST, "files": FILES, "wasm": WASM}
target = ROOT / "visor/data.js"
target.write_text("/* Generado por preparar_visor.py; no editar a mano. */\nwindow.BECALL_DEMO_DATA = " + json.dumps(PAYLOAD, ensure_ascii=False, separators=(",", ":")) + ";\n")
print(f"Visor empaquetado: {len(FILES)} .riv; {target.stat().st_size} bytes")
