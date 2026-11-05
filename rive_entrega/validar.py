#!/usr/bin/env python3
"""Audita todos los proyectos Rive y crea el catálogo visual de entrega."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from generar import CLI, OUT, ROOT, SVG_DIR, registry


def inspect(project: Path):
    result = subprocess.run([str(CLI), "inspect", str(project), "--json"], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    data = json.loads(result.stdout)
    if data["problems"]:
        raise AssertionError(f"{project.name}: {data['problems']}")
    return data


def descendants(node, type_name):
    if isinstance(node, dict):
        if node.get("type") == type_name:
            yield node
        for value in node.values():
            yield from descendants(value, type_name)
    elif isinstance(node, list):
        for value in node:
            yield from descendants(value, type_name)


def digest(path: Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sheet(entries):
    width, cell_w, cell_h = 1000, 200, 178
    rows = (len(entries) + 4) // 5
    canvas = Image.new("RGB", (width, rows * cell_h + 45), "#f1f4f6")
    draw = ImageDraw.Draw(canvas)
    draw.text((20, 13), "BeCall · 47 iconos Rive · variante standard", fill="#243B4C")
    for index, entry in enumerate(entries):
        x, y = (index % 5) * cell_w, 45 + (index // 5) * cell_h
        project = OUT / "proyectos/iconos" / entry["id"]
        icon = Image.new("RGBA", (240, 240), (0, 0, 0, 0))
        parts = sorted(project.glob("standard-*.png"), key=lambda p: int(p.stem.split("-")[-1]))
        for part in parts:
            icon.alpha_composite(Image.open(part).convert("RGBA"))
        if not icon.getbbox():
            raise AssertionError(f"{entry['id']} no tiene píxeles visibles")
        icon.thumbnail((112, 112), Image.Resampling.LANCZOS)
        canvas.paste(icon, (x + (cell_w - icon.width) // 2, y + 12), icon)
        draw.text((x + 16, y + 131), entry["id"], fill="#243B4C")
    target = OUT / "preview/catalogo-iconos.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(target)


def main():
    entries = registry()
    catalog = []
    for entry in entries:
        name = entry["id"]
        project = OUT / "proyectos/iconos" / name
        riv = OUT / "riv/iconos" / f"{name}.riv"
        data = inspect(project)
        boards = data["artboards"]
        assert [a["name"] for a in boards] == ["compact", "standard", "large"], name
        expected = {"idle", "hover", "pressed", "selected", "focus", "disabled", *entry["functionalStates"]}
        for board in boards:
            names = {a["name"] for a in descendants(board, "LinearAnimation")}
            assert expected <= names, (name, board["name"], expected - names)
        assert riv.is_file() and riv.stat().st_size > 1000, name
        catalog.append({"id": name, "label": entry["label"], "category": entry["category"],
                        "svg": str((SVG_DIR / entry["category"] / (entry["originalName"] + ".svg")).relative_to(ROOT)),
                        "artboards": ["compact", "standard", "large"],
                        "animations": sorted(expected), "riv": str(riv.relative_to(OUT)),
                        "bytes": riv.stat().st_size, "sha256": digest(riv)})
    beca_data = inspect(OUT / "proyectos/beca")
    beca_anims = sorted({a["name"] for a in descendants(beca_data["artboards"][0], "LinearAnimation")})
    assert {"idle", "wait", "listen", "receive", "translate", "speak", "conversation", "explain", "wave", "walk", "turn", "celebrate", "error", "blink"} <= set(beca_anims)
    beca_riv = OUT / "riv/mascota/beca.riv"
    assert beca_riv.is_file()
    motion_codes = json.loads((OUT / "beca-motion-codes.json").read_text())
    assert set(motion_codes) == set(beca_anims)
    manifest = {"schema": 1, "generator": "Rive CLI 1.7.0", "icons": catalog,
                "mascot": {"name": "Beca", "riv": str(beca_riv.relative_to(OUT)), "animations": beca_anims,
                           "viewModel": "BecaControls", "audioProperty": "audioLevel", "audioRange": [0, 1],
                           "motionProperty": "motion", "motionCodes": motion_codes,
                           "bytes": beca_riv.stat().st_size, "sha256": digest(beca_riv)}}
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    sheet(entries)
    print(f"OK: {len(catalog)} iconos, {sum(len(i['artboards']) for i in catalog)} artboards, {len(beca_anims)} animaciones de Beca")


if __name__ == "__main__":
    main()
