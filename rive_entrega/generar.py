#!/usr/bin/env python3
"""Genera fuentes RML, capas PNG y archivos Rive de los SVG aprobados."""
from __future__ import annotations

import copy
import json
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
LIB = ROOT / "BeCall_Icons_Fase3_SvelteKit/src/lib/becall-icons"
SVG_DIR = LIB / "svg"
CLI = Path("/home/danimardo/.rive/bin/rive")
NS = "{http://www.w3.org/2000/svg}"
SVG_ELEMENTS = {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon", "g", "text"}
FUNCTIONAL = {"listening", "processing", "speaking", "success", "error", "warning", "muted", "connecting", "disconnected", "paused", "completed"}


def registry():
    text = (LIB / "registry.ts").read_text()
    block = text.split("export const UI_REGISTRY = {", 1)[1].split("} as const;", 1)[0]
    entries = []
    for line in block.splitlines():
        match = re.match(r'\s*"[^"]+":\s*(\{.*\}),?$', line)
        if match:
            entries.append(json.loads(match[1]))
    assert len(entries) == 51, len(entries)
    return entries


def xml_text(node):
    return ET.tostring(node, encoding="unicode")


def raster(svg_path: Path, out: Path, keep_index: int | None = None, size: int = 240):
    tree = ET.parse(svg_path)
    root = tree.getroot()
    viewbox = root.get("viewBox") or "0 0 24 24"
    width = float(viewbox.split()[2]); height = float(viewbox.split()[3])
    root.set("width", str(round(size * width / max(width, height))))
    root.set("height", str(round(size * height / max(width, height))))
    if keep_index is not None:
        drawables = [child for child in root if child.tag.rsplit("}", 1)[-1] in SVG_ELEMENTS]
        for i, child in enumerate(drawables):
            if i != keep_index:
                root.remove(child)
    svg = xml_text(root)
    svg = re.sub(r"var\([^,]+,\s*([^\)]+)\)", lambda m: m[1].strip(), svg)
    temporary = out.with_suffix(".svg")
    temporary.write_text(svg)
    result = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(temporary), "-frames:v", "1", str(out)], capture_output=True, text=True)
    temporary.unlink()
    if result.returncode:
        raise RuntimeError(f"Raster error {svg_path}: {result.stderr}")


def drawable_count(svg_path: Path):
    root = ET.parse(svg_path).getroot()
    return sum(child.tag.rsplit("}", 1)[-1] in SVG_ELEMENTS for child in root)


class RML:
    def __init__(self):
        self.next_id = 2

    def id(self):
        value = f"0:{self.next_id}"
        self.next_id += 1
        return value


def animation(name, targets, frames, duration=36, loop=False):
    """targets: list of (id, property key, base value, peak value)."""
    anim = ET.Element("LinearAnimation", {"name": name, "id": frames.id(), "duration": str(duration), "loopValue": "1" if loop else "0"})
    for object_id, prop, values in targets:
        ko = ET.SubElement(anim, "KeyedObject", {"objectId": object_id})
        kp = ET.SubElement(ko, "KeyedProperty", {"propertyKey": str(prop)})
        for frame, value in values:
            ET.SubElement(kp, "KeyFrameDouble", {"frame": str(frame), "value": f"{value:.6g}", "interpolationType": "1"})
    return anim


def icon_project(entry):
    icon_id = entry["id"]
    category = entry["category"]
    original = entry["originalName"]
    source_dir = SVG_DIR / category
    project = OUT / "proyectos/iconos" / icon_id
    project.mkdir(parents=True, exist_ok=True)
    source_paths = {"standard": source_dir / f"{original}.svg", "compact": source_dir / f"{original}.compact.svg", "large": source_dir / f"{original}.large.svg"}
    for p in source_paths.values():
        if not p.exists():
            raise FileNotFoundError(p)
    render_jobs = []
    for variant, path in source_paths.items():
        count = drawable_count(path) if variant == "standard" else 1
        for part in range(count):
            dest = project / f"{variant}-{part}.png"
            render_jobs.append((path, dest, part if variant == "standard" and count > 1 else None, 240))
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(raster, *job) for job in render_jobs]
        for future in as_completed(futures):
            future.result()

    ids = RML()
    doc = ET.Element("Rive", {"version": "1", "kind": "fragment"})
    assets = []
    for variant_index, variant in enumerate(("compact", "standard", "large")):
        files = sorted(project.glob(f"{variant}-*.png"), key=lambda p: int(p.stem.split("-")[-1]))
        art_id, machine_id, layer_id, style_id = ids.id(), ids.id(), ids.id(), ids.id()
        art = ET.SubElement(doc, "Artboard", {"id": art_id, "name": variant, "width": "24", "height": "24", "x": str(variant_index * 40), "y": "0", "styleId": style_id, "defaultStateMachineId": machine_id})
        ET.SubElement(art, "LayoutComponentStyle", {"id": style_id, "name": "Artboard Style"})
        image_ids = []
        # SVG paints last child on top; Rive paints first child on top.
        for file in reversed(files):
            img_id, asset_id = ids.id(), ids.id()
            image_ids.append(img_id)
            ET.SubElement(art, "Image", {"id": img_id, "name": file.stem, "assetId": asset_id, "x": "12", "y": "12", "scaleX": "0.1", "scaleY": "0.1"})
            assets.append((asset_id, file.name))
        machine = ET.SubElement(art, "StateMachine", {"id": machine_id, "name": "IconMachine"})
        layer = ET.SubElement(machine, "StateMachineLayer", {"id": layer_id, "name": "Default"})
        ET.SubElement(layer, "AnyState", {"x": "0", "y": "-100"})
        ET.SubElement(layer, "ExitState", {"x": "400", "y": "-100"})
        entry_state = ET.SubElement(layer, "EntryState")
        idle_anim_id, idle_state_id = ids.id(), ids.id()
        ET.SubElement(entry_state, "StateTransition", {"stateToId": idle_state_id})
        ET.SubElement(layer, "AnimationState", {"id": idle_state_id, "animationId": idle_anim_id, "x": "160", "y": "0"})
        ET.SubElement(art, "LinearAnimation", {"id": idle_anim_id, "name": "idle", "duration": "1"})
        all_imgs = image_ids
        primary = image_ids[0]
        def scale_anim(name, factor, duration=30, loop=False):
            mid = duration // 2
            vals = [(0, .1), (mid, .1 * factor), (duration, .1)]
            return animation(name, [(obj, 16, vals) for obj in all_imgs] + [(obj, 17, vals) for obj in all_imgs], ids, duration, loop)
        art.append(scale_anim("hover", 1.07, 24))
        art.append(scale_anim("pressed", .89, 16))
        art.append(scale_anim("selected", 1.09, 36))
        art.append(animation("focus", [(obj, 18, [(0, 1), (20, .65), (40, 1)]) for obj in all_imgs], ids, 40))
        art.append(animation("disabled", [(obj, 18, [(0, .45), (1, .45)]) for obj in all_imgs], ids, 1))
        semantics = set(entry["functionalStates"]) & FUNCTIONAL
        for state in sorted(semantics):
            if state in {"processing", "connecting"}:
                targets = [(primary, 15, [(0, 0), (60, 6.283185)])] if icon_id in {"loader", "loader-circle", "settings"} else [(primary, 18, [(0, 1), (30, .55), (60, 1)])]
                art.append(animation(state, targets, ids, 60, True))
            elif state in {"listening", "speaking"}:
                peak = .116 if state == "speaking" else .112
                art.append(animation(state, [
                    (primary, 16, [(0, .1), (27, peak), (54, .1)]),
                    (primary, 17, [(0, .1), (27, peak), (54, .1)]),
                    (primary, 18, [(0, .72), (27, 1), (54, .72)]),
                ], ids, 54, True))
            elif state in {"error", "warning", "disconnected"}:
                art.append(animation(state, [(obj, 13, [(0, 12), (6, 11.2), (12, 12.8), (18, 11.6), (24, 12)]) for obj in all_imgs], ids, 24))
            elif state in {"success", "completed"}:
                art.append(scale_anim(state, 1.17, 34))
            elif state == "muted":
                art.append(animation(state, [(obj, 18, [(0, 1), (16, .5), (32, 1)]) for obj in all_imgs], ids, 32))
            elif state == "paused":
                art.append(animation(state, [(obj, 18, [(0, .75), (1, .75)]) for obj in all_imgs], ids, 1))
    for asset_id, file in assets:
        ET.SubElement(doc, "ImageAsset", {"id": asset_id, "name": file.removesuffix(".png"), "file": file})
    ET.indent(doc)
    (project / "scene.rml").write_text(xml_text(doc) + "\n")
    (project / "rive.yaml").write_text(f"name: {icon_id}\nlogs:\n  file: build/rive.log\n  problems: build/problems.log\n")
    return project


def main():
    entries = registry()
    if len(sys.argv) > 1:
        requested = set(sys.argv[1:])
        entries = [entry for entry in entries if entry["id"] in requested]
        missing = requested - {entry["id"] for entry in entries}
        if missing:
            raise ValueError(f"Iconos desconocidos: {', '.join(sorted(missing))}")
    projects = [icon_project(entry) for entry in entries]
    riv_dir = OUT / "riv/iconos"
    riv_dir.mkdir(parents=True, exist_ok=True)
    for project in projects:
        result = subprocess.run([str(CLI), str(project), "--once", "--quiet"], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(f"{project.name}: {result.stdout}\n{result.stderr}")
        shutil.copy2(project / "build" / f"{project.name}.riv", riv_dir / f"{project.name}.riv")
    print(f"Generated {len(projects)} icon Rive files")


if __name__ == "__main__":
    main()
