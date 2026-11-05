#!/usr/bin/env python3
"""Construye el personaje Beca en capas animables y un .riv verificable."""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET

from generar import OUT, ROOT, CLI, RML, animation, raster, xml_text

SOURCE = ROOT / "Beca_SVG/01_personaje/02_frontal.svg"
THREE_QUARTERS = ROOT / "Beca_SVG/01_personaje/03_tres_cuartos.svg"
PROJECT = OUT / "proyectos/beca"
PIVOT = {
    "leftLeg": (222, 455),
    "rightLeg": (301, 455),
    "soles": (260, 515),
    "leftArm": (195, 365),
    "rightArm": (329, 365),
    "body": (260, 420),
    "scarf": (260, 342),
    "head": (263, 335),
    "cheeks": (263, 255),
    "eyes": (263, 220),
    "mouth": (263, 267),
    "headphones": (263, 223),
    "threeQuarter": (256, 276),
}


def layer_svg(name):
    root = ET.parse(SOURCE).getroot()
    outer = next(node for node in root.iter() if node.get("id") == "personaje-beca")
    top = {
        "leftLeg": "piernas", "rightLeg": "piernas", "soles": "piernas",
        "leftArm": "brazo-izquierdo", "rightArm": "brazo-derecho",
        "body": "cuerpo", "scarf": "bufanda", "head": "cabeza",
        "cheeks": "cabeza", "eyes": "cabeza", "mouth": "cabeza", "headphones": "cabeza"
    }[name]
    for child in list(outer):
        if child.get("id") != top:
            outer.remove(child)
    if top == "piernas":
        legs = outer[0]
        selected = {"leftLeg": {0, 2}, "rightLeg": {1, 3}, "soles": {4}}[name]
        for index, child in enumerate(list(legs)):
            if index not in selected:
                legs.remove(child)
    if top == "cabeza":
        head = next(node for node in outer if node.get("id") == "cabeza")
        if name == "head":
            for child in list(head):
                if child.get("id") in {"rostro-expresion", "auriculares"}:
                    head.remove(child)
        else:
            for child in list(head):
                if child.get("id") != ("auriculares" if name == "headphones" else "rostro-expresion"):
                    head.remove(child)
            if name != "headphones":
                face = head[0]
                children = list(face)
                selected = {"cheeks": {0, 1}, "eyes": {2, 3, 4, 5}, "mouth": {6, 7}}[name]
                for index, child in enumerate(children):
                    if index not in selected:
                        face.remove(child)
    return root


def keys(obj, prop, values):
    return (obj, prop, values)


def main():
    PROJECT.mkdir(parents=True, exist_ok=True)
    names = ["leftLeg", "rightLeg", "soles", "leftArm", "rightArm", "body", "scarf", "head", "cheeks", "eyes", "mouth", "headphones"]
    for name in names:
        svg = PROJECT / f"{name}.svg"
        svg.write_text(xml_text(layer_svg(name)))
        raster(svg, PROJECT / f"{name}.png", size=552)
    raster(THREE_QUARTERS, PROJECT / "threeQuarter.png", size=552)

    ids = RML()
    doc = ET.Element("Rive", {"version": "1", "kind": "fragment"})
    art_id, machine_id, layer_id, style_id = ids.id(), ids.id(), ids.id(), ids.id()
    vm_id, audio_property_id, motion_property_id, vm_instance_id, converter_id = ids.id(), ids.id(), ids.id(), ids.id(), ids.id()
    art = ET.SubElement(doc, "Artboard", {"id": art_id, "name": "Beca", "width": "512", "height": "552", "styleId": style_id, "defaultStateMachineId": machine_id, "viewModelId": vm_id, "viewModelInstanceId": vm_instance_id})
    ET.SubElement(art, "LayoutComponentStyle", {"id": style_id, "name": "Artboard Style"})
    image_ids = {}
    assets = []
    # Rive paints first child on top; the order below is visual front to back.
    order = ["threeQuarter", "headphones", "mouth", "eyes", "cheeks", "head", "scarf", "body", "rightArm", "leftArm", "soles", "rightLeg", "leftLeg"]
    for name in order:
        pivot_x, pivot_y = PIVOT[name]
        img_id, asset_id = ids.id(), ids.id()
        image_ids[name] = img_id
        image = ET.SubElement(art, "Image", {"id": img_id, "name": name, "assetId": asset_id,
                                      "x": str(pivot_x), "y": str(pivot_y),
                                      "originX": f"{pivot_x / 512:.6f}", "originY": f"{pivot_y / 552:.6f}",
                                      "opacity": "0" if name == "threeQuarter" else "1"})
        if name == "mouth":
            ET.SubElement(image, "DataBindContext", {"sourcePathIds": f"{vm_id}-{audio_property_id}", "propertyKey": "17", "converterId": converter_id})
        assets.append((asset_id, name))
    machine = ET.SubElement(art, "StateMachine", {"id": machine_id, "name": "BecaMachine"})
    layer = ET.SubElement(machine, "StateMachineLayer", {"id": layer_id, "name": "Default"})
    any_state = ET.SubElement(layer, "AnyState", {"x": "0", "y": "-100"})
    ET.SubElement(layer, "ExitState", {"x": "420", "y": "-100"})
    entry = ET.SubElement(layer, "EntryState")
    idle_state_id, idle_anim_id = ids.id(), ids.id()
    ET.SubElement(entry, "StateTransition", {"stateToId": idle_state_id})
    ET.SubElement(layer, "AnimationState", {"id": idle_state_id, "animationId": idle_anim_id, "x": "160", "y": "0", "reset": "true"})
    motion_states = {"idle": idle_state_id}
    head = image_ids["head"]; eyes = image_ids["eyes"]; mouth = image_ids["mouth"]
    body = image_ids["body"]; scarf = image_ids["scarf"]
    left = image_ids["leftArm"]; right = image_ids["rightArm"]
    left_leg = image_ids["leftLeg"]; right_leg = image_ids["rightLeg"]
    soles = image_ids["soles"]
    front = [image_ids[n] for n in names]
    idle = animation("idle", [
        keys(head, 14, [(0, 335), (90, 332), (180, 335), (360, 335), (480, 335)]),
        keys(body, 17, [(0, 1), (90, 1.012), (180, 1), (480, 1)]),
        keys(eyes, 17, [(0, 1), (240, 1), (244, .08), (248, 1), (480, 1)]),
        keys(scarf, 15, [(0, 0), (90, .015), (180, 0), (480, 0)]),
    ], ids, 480, True)
    idle.set("id", idle_anim_id)
    art.append(idle)
    def add(name, targets, duration=60, loop=False):
        anim = animation(name, targets, ids, duration, loop)
        art.append(anim)
        state_id = ids.id()
        motion_states[name] = state_id
        ET.SubElement(layer, "AnimationState", {"id": state_id, "animationId": anim.get("id"), "x": str(160 + 125 * (len(motion_states) % 5)), "y": str(95 * (len(motion_states) // 5)), "reset": "true"})
    add("wait", [keys(head, 15, [(0, 0), (80, .08), (160, -.06), (240, 0)]),
                 keys(eyes, 13, [(0, 263), (80, 266), (160, 260), (240, 263)]),
                 keys(scarf, 15, [(0, 0), (120, .03), (240, 0)])], 240, True)
    add("listen", [keys(head, 15, [(0, 0), (30, -.09), (60, 0)]),
                   keys(eyes, 17, [(0, 1), (30, 1.08), (60, 1)])], 60, True)
    add("receive", [keys(head, 15, [(0, 0), (40, .07), (80, 0)]),
                    keys(left, 15, [(0, 0), (40, -.08), (80, 0)])], 80, True)
    add("translate", [keys(head, 14, [(0, 335), (45, 332), (90, 335)]),
                      keys(scarf, 15, [(0, 0), (45, .045), (90, 0)]),
                      keys(eyes, 13, [(0, 263), (45, 260), (90, 263)])], 90, True)
    add("speak", [keys(right, 15, [(0, 0), (14, -.08), (28, 0)]),
                  keys(head, 14, [(0, 335), (14, 331), (28, 335)])], 28, True)
    add("conversation", [keys(head, 15, [(0, 0), (16, -.07), (32, 0)]),
                         keys(right, 15, [(0, 0), (16, -.06), (32, 0)])], 32, True)
    add("explain", [keys(right, 15, [(0, 0), (20, -.38), (45, -.31), (65, 0)]),
                    keys(head, 15, [(0, 0), (30, -.045), (65, 0)])], 65)
    add("wave", [keys(right, 15, [(0, 0), (14, -.6), (27, -.43), (40, -.6), (56, 0)])], 56)
    add("walk", [keys(left_leg, 15, [(0, -.18), (18, .18), (36, -.18)]),
                 keys(right_leg, 15, [(0, .18), (18, -.18), (36, .18)]),
                 keys(soles, 18, [(0, 0), (36, 0)]),
                 keys(left_leg, 13, [(0, 208), (18, 236), (36, 208)]),
                 keys(right_leg, 13, [(0, 315), (18, 287), (36, 315)]),
                 keys(left_leg, 14, [(0, 455), (9, 439), (18, 455), (36, 455)]),
                 keys(right_leg, 14, [(0, 455), (18, 455), (27, 439), (36, 455)]),
                 keys(left, 15, [(0, -.1), (18, .1), (36, -.1)]),
                 keys(right, 15, [(0, .1), (18, -.1), (36, .1)]),
                 keys(body, 14, [(0, 420), (9, 414), (18, 420), (27, 414), (36, 420)]),
                 keys(head, 14, [(0, 335), (9, 330), (18, 335), (27, 330), (36, 335)])], 36, True)
    add("turn", [keys(image_ids["threeQuarter"], 18, [(0, 0), (28, 1), (72, 1), (100, 0)])] +
        [keys(obj, 18, [(0, 1), (28, 0), (72, 0), (100, 1)]) for obj in front], 100)
    add("celebrate", [keys(body, 14, [(0, 420), (15, 400), (30, 420), (48, 409), (65, 420)]),
                      keys(left, 15, [(0, 0), (15, .4), (30, 0), (48, .3), (65, 0)]),
                      keys(right, 15, [(0, 0), (15, -.4), (30, 0), (48, -.3), (65, 0)])], 65)
    add("error", [keys(head, 15, [(0, 0), (20, -.05), (40, .04), (60, 0)]),
                  keys(eyes, 17, [(0, 1), (30, .7), (60, 1)])], 60)
    add("blink", [keys(eyes, 17, [(0, 1), (5, .07), (10, 1)])], 10)
    for code, (name, state_id) in enumerate(motion_states.items()):
        transition = ET.SubElement(any_state, "StateTransition", {"stateToId": state_id, "duration": "100"})
        condition = ET.SubElement(transition, "TransitionViewModelCondition", {"opValue": "equal"})
        left = ET.SubElement(condition, "TransitionPropertyViewModelComparator")
        bindable = ET.SubElement(left, "BindablePropertyNumber")
        ET.SubElement(bindable, "DataBindContext", {"sourcePathIds": f"{vm_id}-{motion_property_id}", "propertyKey": "636"})
        ET.SubElement(condition, "TransitionValueNumberComparator", {"value": str(code)})
    for asset_id, name in assets:
        ET.SubElement(doc, "ImageAsset", {"id": asset_id, "name": name, "file": f"{name}.png"})
    ET.SubElement(doc, "DataConverterRangeMapper", {"id": converter_id, "name": "AudioToMouth", "minInput": "0", "maxInput": "1", "minOutput": "1", "maxOutput": "1.35", "clampLower": "true", "clampUpper": "true"})
    vm = ET.SubElement(doc, "ViewModel", {"id": vm_id, "name": "BecaControls", "defaultInstanceId": vm_instance_id})
    ET.SubElement(vm, "ViewModelPropertyNumber", {"id": audio_property_id, "name": "audioLevel"})
    ET.SubElement(vm, "ViewModelPropertyNumber", {"id": motion_property_id, "name": "motion"})
    instance = ET.SubElement(vm, "ViewModelInstance", {"id": vm_instance_id, "name": "Default", "exports": "true"})
    ET.SubElement(instance, "ViewModelInstanceNumber", {"viewModelPropertyId": audio_property_id, "propertyValue": "0"})
    ET.SubElement(instance, "ViewModelInstanceNumber", {"viewModelPropertyId": motion_property_id, "propertyValue": "0"})
    (OUT / "beca-motion-codes.json").write_text(json.dumps({name: code for code, name in enumerate(motion_states)}, indent=2) + "\n")
    ET.indent(doc)
    (PROJECT / "scene.rml").write_text(xml_text(doc) + "\n")
    (PROJECT / "rive.yaml").write_text("name: beca\nlogs:\n  file: build/rive.log\n  problems: build/problems.log\n")
    result = subprocess.run([str(CLI), str(PROJECT), "--once"], capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    dest = OUT / "riv/mascota"
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PROJECT / "build/beca.riv", dest / "beca.riv")
    print(result.stdout)


if __name__ == "__main__":
    main()
