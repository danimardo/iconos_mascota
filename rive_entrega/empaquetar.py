#!/usr/bin/env python3
"""Prepara el ZIP revisable para el cliente y comprueba su integridad."""
from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
archive = root / "BeCall_Rive_Entrega.zip"
folders = ("rive_entrega", "Beca_SVG", "BeCall_Icons_Fase3_SvelteKit")
prefix = Path("BeCall_Rive_Entrega")
skip_dirs = {"__pycache__", "node_modules", ".git"}
skip_suffixes = {".pyc", ".log"}

with ZipFile(archive, "w", compression=ZIP_DEFLATED, compresslevel=9) as zip_file:
    zip_file.writestr(
        str(prefix / "LEEME_CLIENTE.txt"),
        "BeCall · Iconos y Beca animados con Rive\n\n"
        "Para verlos, abra rive_entrega/visor/index.html en Chrome, Edge o Firefox.\n"
        "El visor incluye sus recursos y funciona sin conexión ni servidor.\n\n"
        "El catálogo de los 48 archivos .riv y las instrucciones para integrarlos "
        "están en rive_entrega/README.md e INTEGRACION.md.\n"
        "Beca_SVG y BeCall_Icons_Fase3_SvelteKit contienen los SVG originales.\n",
    )
    for folder in folders:
        for file in sorted((root / folder).rglob("*")):
            if not file.is_file() or any(part in skip_dirs for part in file.parts) or file.suffix in skip_suffixes:
                continue
            zip_file.write(file, prefix / file.relative_to(root))

with ZipFile(archive) as zip_file:
    bad = zip_file.testzip()
    assert bad is None, f"Archivo dañado: {bad}"
    names = set(zip_file.namelist())
    assert str(prefix / "rive_entrega/visor/index.html") in names
    assert str(prefix / "rive_entrega/visor/data.js") in names
    assert str(prefix / "rive_entrega/manifest.json") in names
    assert sum(n.startswith(str(prefix / "rive_entrega/riv/")) and n.endswith(".riv") for n in names) == 48
    print(f"ZIP verificado: {archive} · {len(names)} archivos · {archive.stat().st_size:,} bytes")
