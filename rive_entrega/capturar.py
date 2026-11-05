#!/usr/bin/env python3
"""Captura fotogramas de animaciones nombradas con el renderizador Rive."""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

import json
from generar import CLI, OUT


def capture(source: Path, animation: str, destination: Path, artboard: str, frame: int, viewport: str, audio: float | None = None):
    if source.name == "beca":
        code = json.loads((OUT / "beca-motion-codes.json").read_text())[animation]
        cmd = [str(CLI), str(source), f"--screenshot={destination}", f"--artboard={artboard}", f"--viewport={viewport}", "--fit=contain", f"--advance={frame}", f"--data=motion={code}"]
        if audio is not None:
            cmd.append(f"--data=audioLevel={audio}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        return
    with tempfile.TemporaryDirectory(prefix="becall-rive-") as temp:
        project = Path(temp) / source.name
        shutil.copytree(source, project, ignore=shutil.ignore_patterns("build", "*.riv", "*.log"))
        scene = project / "scene.rml"
        root = ET.parse(scene).getroot()
        art = next(a for a in root.findall("Artboard") if a.get("name") == artboard)
        anim = next(a for a in art.findall("LinearAnimation") if a.get("name") == animation)
        state = art.find("StateMachine/StateMachineLayer/AnimationState")
        if state is None:
            raise AssertionError("No default animation state")
        state.set("animationId", anim.get("id"))
        ET.indent(root)
        scene.write_text(ET.tostring(root, encoding="unicode") + "\n")
        cmd = [str(CLI), str(project), f"--screenshot={destination}", f"--artboard={artboard}", f"--viewport={viewport}", "--fit=contain", f"--advance={frame}"]
        if audio is not None:
            cmd.append(f"--data=audioLevel={audio}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)


def main():
    dest = OUT / "preview"
    dest.mkdir(exist_ok=True)
    beca = OUT / "proyectos/beca"
    for name, frame, level in [("wait", 80, 0), ("walk", 9, 0), ("speak", 14, 1), ("turn", 50, 0), ("explain", 35, 0)]:
        capture(beca, name, dest / f"beca-{name}.png", "Beca", frame, "512x552", level)
    icon = OUT / "proyectos/iconos/microphone"
    capture(icon, "listening", dest / "microphone-listening.png", "standard", 27, "240x240")
    for level in (0, 1):
        target = dest / f"beca-audio-{level}.png"
        result = subprocess.run([str(CLI), str(beca), f"--screenshot={target}", "--viewport=512x552", "--fit=contain", f"--data=audioLevel={level}"], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
    print("OK: 6 capturas de animación y 2 pruebas de audioLevel")


if __name__ == "__main__":
    main()
