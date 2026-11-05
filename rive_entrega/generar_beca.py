#!/usr/bin/env python3
"""Construye a Beca como personaje articulado y genera un .riv verificable.

Rig (v2):
- Jerarquía real: personaje > frente > torso > cabeza > cara. Lo que mueve la
  cabeza arrastra ojos, boca, mofletes, auriculares y antena.
- Bufanda en dos piezas: nudo rígido y cola deformada por una malla con tres
  huesos, para que ondee como tela.
- Expresiones (guiño, sorprendida, pensando, satisfecha, error), poses de
  brazos y elementos (destellos, check, aviso, duda) tomados de los SVG
  aprobados de Beca_SVG/02_expresiones y alternados en cada animación.
- Curvas de aceleración (cubic/elastic) en lugar de interpolación lineal.

El contrato con la app no cambia: artboard «Beca», máquina «BecaMachine»,
View Model «BecaControls» con «motion» (códigos 0-13 en el mismo orden) y
«audioLevel» enlazado a la escala vertical de la boca.
"""
from __future__ import annotations

import base64
import copy
import json
import math
import os
import shutil
import subprocess
from pathlib import Path
from xml.etree import ElementTree as ET

from generar import OUT, ROOT, CLI, RML, raster, xml_text

# El ffmpeg de miniforge no trae el decodificador SVG; el del sistema sí.
os.environ["PATH"] = "/usr/bin:" + os.environ.get("PATH", "")

SVG = ROOT / "Beca_SVG"
FRONT = SVG / "01_personaje/02_frontal.svg"
THREE_QUARTERS = SVG / "01_personaje/03_tres_cuartos.svg"
EXPR = {
    "alegre": SVG / "02_expresiones/01_alegre.svg",
    "guino": SVG / "02_expresiones/02_guino.svg",
    "sorpresa": SVG / "02_expresiones/03_sorprendida.svg",
    "pensando": SVG / "02_expresiones/04_pensando.svg",
    "satisfecha": SVG / "02_expresiones/05_satisfecha.svg",
    "error": SVG / "02_expresiones/06_error_aviso.svg",
}
PROJECT = OUT / "proyectos/beca"
W, H = 512, 552
FPS = 60
MOTIONS = ["idle", "wait", "listen", "receive", "translate", "speak", "conversation",
           "explain", "wave", "walk", "turn", "celebrate", "error", "blink"]

X, Y, ROT, SX, SY, OP = 13, 14, 15, 16, 17, 18
PROP = {"x": X, "y": Y, "rot": ROT, "sx": SX, "sy": SY, "op": OP}

# ---------------------------------------------------------------- capas SVG
P = "personaje-beca"
FACE = [P, "cabeza", "rostro-expresion"]
# nombre: (svg, ruta de ids, índices de hijos que se conservan o None = todos)
LAYERS = {
    "leftLeg": (FRONT, [P, "piernas"], {0, 2}),
    "rightLeg": (FRONT, [P, "piernas"], {1, 3}),
    "soles": (FRONT, [P, "piernas"], {4}),
    "body": (FRONT, [P, "cuerpo"], None),
    "scarfTail": (FRONT, [P, "bufanda"], {0, 1}),
    "scarfKnot": (FRONT, [P, "bufanda"], {2, 3, 4}),
    "antenna": (FRONT, [P, "cabeza"], {0, 1}),
    "head": (FRONT, [P, "cabeza"], {2, 3, 4, 5}),
    "headphones": (FRONT, [P, "cabeza"], {7}),
    "cheeks": (FRONT, FACE, {0, 1}),
    "eyes": (FRONT, FACE, {2, 3, 4, 5}),
    "mouth": (FRONT, FACE, {6, 7}),
    "faceGuino": (EXPR["guino"], FACE, "noCheeks"),
    "faceSorpresa": (EXPR["sorpresa"], FACE, "noCheeks"),
    "facePensando": (EXPR["pensando"], FACE, "noCheeks"),
    "faceSatisfecha": (EXPR["satisfecha"], FACE, "noCheeks"),
    "faceError": (EXPR["error"], FACE, "noCheeks"),
    "rArm": (FRONT, [P, "brazo-derecho"], None),
    "rArmWave": (EXPR["alegre"], [P, "brazo-derecho"], None),
    "rArmPoint": (EXPR["guino"], [P, "brazo-derecho"], None),
    "rArmThink": (EXPR["pensando"], [P, "brazo-derecho"], None),
    "lArm": (FRONT, [P, "brazo-izquierdo"], None),
    "lArmUp": (EXPR["sorpresa"], [P, "brazo-izquierdo"], None),
    "lArmThink": (EXPR["pensando"], [P, "brazo-izquierdo"], None),
    "propRays": (EXPR["alegre"], ["rayos"], None),
    "propQuestion": (EXPR["pensando"], ["duda"], None),
    "propCheck": (EXPR["satisfecha"], ["verificacion"], None),
    "propWarn": (EXPR["error"], ["aviso"], None),
}
KEEP_TAGS = {"defs", "title", "desc", "style"}


def isolate(src: Path, chain, keep):
    root = ET.parse(src).getroot()
    node = root
    for ident in chain:
        target = next(c for c in node if c.get("id") == ident)
        for child in list(node):
            if child is not target and child.tag.rsplit("}", 1)[-1] not in KEEP_TAGS:
                node.remove(child)
        node = target
    if keep == "noCheeks":
        keep = set(range(2, len(node)))
    if keep is not None:
        for index, child in enumerate(list(node)):
            if index not in keep:
                node.remove(child)
    return root


# ---------------------------------------------------------------- jerarquía
# Beca se dibuja al 90 % sobre la base del artboard para dejar aire a los saltos.
STAGE_PIVOT, STAGE_SCALE = (260, 548), 0.9


def to_world(p):
    return (STAGE_PIVOT[0] + (p[0] - STAGE_PIVOT[0]) * STAGE_SCALE,
            STAGE_PIVOT[1] + (p[1] - STAGE_PIVOT[1]) * STAGE_SCALE)


# (nombre, padre, pivote en coordenadas del lienzo 512x552, imágenes, opacidad inicial)
NODES = [
    ("stage", None, STAGE_PIVOT, [], 1),
    ("character", "stage", (260, 515), [], 1),
    ("propCheck", "character", (445, 83), ["propCheck"], 0),
    ("propWarn", "character", (444, 92), ["propWarn"], 0),
    ("propRays", "character", (448, 140), ["propRays"], 0),
    ("propQuestion", "character", (462, 82), ["propQuestion"], 0),
    ("threeQuarter", "character", (256, 515), ["threeQuarter"], 0),
    ("front", "character", (260, 515), [], 1),
    ("torso", "front", (260, 458), [], 1),
    # brazos que se dibujan delante de la cabeza (mano en la barbilla / en el auricular)
    ("rightArmFront", "torso", (330, 366), ["rArmThink"], 0),
    ("leftArmFront", "torso", (193, 363), ["lArmUp"], 0),
    ("headRig", "torso", (263, 345), [], 1),
    ("headphones", "headRig", (263, 223), ["headphones"], 1),
    ("face", "headRig", (263, 240), [], 1),
    ("faceDefault", "face", (263, 240), [], 1),
    ("eyes", "faceDefault", (263, 221), ["eyes"], 1),
    ("mouth", "faceDefault", (263, 268), ["mouth"], 1),
    ("faceGuino", "face", (263, 240), ["faceGuino"], 0),
    ("faceSorpresa", "face", (263, 240), ["faceSorpresa"], 0),
    ("facePensando", "face", (263, 240), ["facePensando"], 0),
    ("faceSatisfecha", "face", (263, 240), ["faceSatisfecha"], 0),
    ("faceError", "face", (263, 240), ["faceError"], 0),
    ("cheeks", "face", (263, 262), ["cheeks"], 1),
    ("head", "headRig", (263, 240), ["head"], 1),
    ("antenna", "headRig", (196, 166), ["antenna"], 1),
    ("scarfKnot", "torso", (260, 342), ["scarfKnot"], 1),
    # la cola de la bufanda (malla) se inserta aquí, tras el nudo
    ("body", "torso", (260, 455), ["body"], 1),
    ("rightArm", "torso", (330, 366), [], 1),
    ("rArm", "rightArm", (330, 366), ["rArm"], 1),
    ("rArmWave", "rightArm", (330, 366), ["rArmWave"], 0),
    ("rArmPoint", "rightArm", (330, 366), ["rArmPoint"], 0),
    ("leftArm", "torso", (193, 363), [], 1),
    ("lArm", "leftArm", (193, 363), ["lArm"], 1),
    ("lArmThink", "leftArm", (193, 363), ["lArmThink"], 0),
    ("soles", "front", (260, 515), ["soles"], 1),
    ("rightLeg", "front", (301, 455), ["rightLeg"], 1),
    ("leftLeg", "front", (222, 455), ["leftLeg"], 1),
]
# Línea central de la cola de la bufanda: raíz (bajo el nudo) -> punta.
TAIL = [(238, 353), (183, 374), (139, 398), (95, 411)]
TAIL_START, TAIL_END = (252, 347), (82, 415)


def varuint(n):
    out = bytearray()
    while True:
        b = n & 0x7F
        n >>= 7
        out.append(b | 0x80 if n else b)
        if not n:
            return bytes(out)


def tail_mesh(alpha):
    """Tira de triángulos a lo largo de la cola, con pesos repartidos entre 3 huesos."""
    line = [TAIL_START] + TAIL[1:-1] + [TAIL_END]
    lengths = [math.dist(a, b) for a, b in zip(line, line[1:])]
    total = sum(lengths)
    bone_len = [math.dist(a, b) for a, b in zip(TAIL, TAIL[1:])]
    samples = 13
    centers, normals, along = [], [], []
    for i in range(samples):
        d = total * i / (samples - 1)
        k = 0
        while k < len(lengths) - 1 and d > lengths[k]:
            d -= lengths[k]; k += 1
        a, b = line[k], line[k + 1]
        t = min(d / lengths[k], 1)
        cx, cy = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        dx, dy = (b[0] - a[0]) / lengths[k], (b[1] - a[1]) / lengths[k]
        centers.append((cx, cy)); normals.append((-dy, dx))
        # posición proyectada sobre la cadena de huesos (0..3)
        best = None
        for j, (p, q) in enumerate(zip(TAIL, TAIL[1:])):
            vx, vy = q[0] - p[0], q[1] - p[1]
            u = ((cx - p[0]) * vx + (cy - p[1]) * vy) / (bone_len[j] ** 2)
            uc = max(0, min(1, u))
            dist = math.dist((cx, cy), (p[0] + vx * uc, p[1] + vy * uc))
            if best is None or dist < best[0]:
                best = (dist, j + uc)
        along.append(best[1])
    # semiancho mínimo que cubre todos los píxeles opacos de la cola
    half = 26
    while True:
        poly = [(c[0] + n[0] * half, c[1] + n[1] * half) for c, n in zip(centers, normals)] + \
               [(c[0] - n[0] * half, c[1] - n[1] * half) for c, n in reversed(list(zip(centers, normals)))]
        if all(_inside(px + .5, py + .5, poly) for px, py in alpha):
            break
        half += 2
        if half > 70:
            raise RuntimeError("La malla de la bufanda no cubre la cola")

    def weight(s):
        s = max(0.0, min(2.999, s))
        k = int(s); f = s - k
        if f < .3 and k > 0:
            w = .5 + f / .6
            return [(k, w), (k - 1, 1 - w)]
        if f > .7 and k < 2:
            w = .5 + (1 - f) / .6
            return [(k, w), (k + 1, 1 - w)]
        return [(k, 1.0)]

    verts = []
    for c, n, s in zip(centers, normals, along):
        for sign in (1, -1):
            verts.append(((c[0] + n[0] * half * sign, c[1] + n[1] * half * sign), weight(s)))
    tris = []
    for i in range(samples - 1):
        a, b, c, d = 2 * i, 2 * i + 1, 2 * i + 2, 2 * i + 3
        tris += [a, b, c, b, d, c]
    return verts, base64.b64encode(b"".join(varuint(i) for i in tris)).decode(), half


def _inside(x, y, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        xi, yi = poly[i]; xj, yj = poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi:
            inside = not inside
        j = i
    return inside


def pack(weights):
    q = [round(w * 255) for _, w in weights]
    q[0] += 255 - sum(q)
    indices = sum((t + 1) << (8 * i) for i, (t, _) in enumerate(weights))
    values = sum(v << (8 * i) for i, v in enumerate(q))
    return str(indices), str(values)


# ---------------------------------------------------------------- animación
EASE = {
    "io": (.45, 0, .55, 1),      # entrada y salida suaves
    "o": (.15, .6, .35, 1),      # sale rápido, frena
    "i": (.55, 0, .85, .4),      # arranca lento, acelera (caídas)
    "s": (.3, 0, .3, 1),
}


class Anim:
    def __init__(self, name, duration, loop):
        self.name, self.duration, self.loop = name, duration, loop
        self.tracks = {}

    def k(self, node, prop, keys):
        """keys: (frame, valor[, curva saliente]). Valores absolutos (x/y como desplazamiento)."""
        key = (node, PROP[prop])
        assert key not in self.tracks, f"{self.name}: pista repetida {node}.{prop}"
        norm = []
        for item in keys:
            frame, value = item[0], item[1]
            ease = item[2] if len(item) > 2 else "io"
            norm.append((round(frame), value, ease))
        norm.sort(key=lambda t: t[0])
        self.tracks[key] = norm
        return self

    def sine(self, node, prop, period, amp, base=0.0, phase=0.0, start=0, end=None, env=None):
        """Oscilación senoidal: picos con ease-in-out. phase en fracciones de periodo."""
        end = self.duration if end is None else end
        f = lambda t: math.sin(2 * math.pi * ((t - start) / period - phase))
        e = env or (lambda t: 1.0)
        keys = [(start, base + amp * e(start) * f(start), "io" if abs(f(start)) > .98 else "o")]
        n = -2
        while True:
            t = start + (phase + .25 + n * .5) * period
            n += 1
            if t <= start + .5:
                continue
            if t >= end - .5:
                break
            keys.append((t, base + amp * e(t) * f(t), "io"))
        keys.append((end, base + amp * e(end) * f(end), "io"))
        if len(keys) > 2:
            keys[-2] = (keys[-2][0], keys[-2][1], "i") if abs(f(end)) < .98 else keys[-2]
        # fotogramas enteros sin duplicados
        clean = {}
        for t, v, ease in keys:
            clean.setdefault(round(t), (round(t), v, ease))
        return self.k(node, prop, list(clean.values()))

    def show(self, node, spans, fade=0):
        """Opacidad 1 en los tramos [(desde, hasta)], 0 fuera."""
        keys = [(0, 0, "h")]
        for a, b in spans:
            if fade:
                keys += [(max(a - fade, 0), 0, "l"), (a, 1, "h"), (b, 1, "l"), (min(b + fade, self.duration), 0, "h")]
            else:
                keys += [(a, 1, "h"), (b, 0, "h")]
        return self.k(node, "op", _dedupe(keys))

    def hide(self, node, spans):
        keys = [(0, 1, "h")]
        for a, b in spans:
            keys += [(a, 0, "h"), (b, 1, "h")]
        return self.k(node, "op", _dedupe(keys))


def _dedupe(keys):
    out = {}
    for item in keys:
        out[item[0]] = item
    return sorted(out.values())


def swap_face(a, face, spans):
    a.show(face, spans)
    a.hide("faceDefault", spans)


def swap_arm(a, side, pose, spans):
    base = "rArm" if side == "r" else "lArm"
    a.show(pose, spans)
    a.hide(base, spans)


def scarf(a, period, amps=(.05, .09, .13), lag=.12, base=(0, 0, 0), start=0, end=None, env=None):
    """La cola ondea: cada hueso repite la onda del anterior con retraso."""
    for i, bone in enumerate(("scarf0", "scarf1", "scarf2")):
        a.sine(bone, "rot", period, amps[i], base=REST[(bone, ROT)] + base[i], phase=lag * (i + 1),
               start=start, end=end, env=env)


def antenna(a, period, amp, phase=.15, start=0, end=None, env=None):
    a.sine("antenna", "rot", period, amp, phase=phase, start=start, end=end, env=env)


def blink(a, frames, prop_keys=None):
    keys = [(0, 1, "h")]
    for f in frames:
        keys += [(f, 1, "i"), (f + 3, .08, "o"), (f + 8, 1, "io")]
    a.k("eyes", "sy", _dedupe(keys + [(a.duration, 1)]))


def build_animations():
    A = []

    # 0 · idle: respira, mira a los lados, parpadea; antena y bufanda en segundo plano
    a = Anim("idle", 480, True)
    a.sine("torso", "sy", 160, .022, base=1, phase=.75)
    a.sine("torso", "sx", 160, .01, base=1, phase=.25)
    a.sine("headRig", "rot", 240, .04)
    a.sine("headRig", "y", 160, 3, phase=.85)
    a.k("face", "x", [(0, 0), (110, 0, "o"), (126, -10), (200, -10, "o"), (220, 10), (296, 10, "o"), (312, 0), (480, 0)])
    a.k("face", "y", [(0, 0), (110, 0, "o"), (126, 2), (200, 2, "o"), (220, -2), (296, -2, "o"), (312, 0), (480, 0)])
    a.k("headphones", "x", [(0, 0), (110, 0, "o"), (126, 3), (200, 3, "o"), (220, -3), (296, -3, "o"), (312, 0), (480, 0)])
    blink(a, [60, 250, 380, 395])
    antenna(a, 240, .07, phase=.1)
    a.sine("rightArm", "rot", 160, .045, phase=.8)
    a.sine("leftArm", "rot", 160, .045, phase=.3)
    scarf(a, 120)
    A.append(a)

    # 1 · wait: mira alrededor, se lleva la mano a la barbilla, golpea el pie
    a = Anim("wait", 240, True)
    a.k("face", "x", [(0, 0), (14, 0, "o"), (28, -11), (90, -11, "o"), (104, 11), (150, 11, "o"), (166, 0), (240, 0)])
    a.k("face", "y", [(0, 0), (14, 0, "o"), (28, -4), (90, -4, "o"), (104, 1), (240, 0)])
    a.k("headphones", "x", [(0, 0), (14, 0, "o"), (28, 3.5), (90, 3.5, "o"), (104, -3.5), (150, -3.5, "o"), (166, 0), (240, 0)])
    a.k("headRig", "rot", [(0, 0), (16, 0, "o"), (34, -.12), (90, -.12, "o"), (108, .1), (150, .1, "o"), (170, 0), (240, 0)])
    swap_face(a, "facePensando", [(40, 92)])
    swap_arm(a, "r", "rightArmFront", [(40, 92)])
    a.k("rightArm", "rot", [(0, 0), (34, .12, "o"), (40, 0, "h"), (92, .1, "o"), (104, 0), (240, 0)])
    a.k("rightArmFront", "rot", [(0, 0), (40, -.12, "el"), (60, 0), (240, 0)])
    a.k("propQuestion", "op", [(0, 0, "h"), (44, 0, "o"), (52, 1), (84, 1, "i"), (92, 0, "h"), (240, 0, "h")])
    a.k("propQuestion", "sy", [(0, .3, "h"), (44, .3, "el"), (60, 1), (240, 1, "h")])
    a.k("propQuestion", "sx", [(0, .3, "h"), (44, .3, "el"), (60, 1), (240, 1, "h")])
    a.k("rightLeg", "rot", [(0, 0), (176, 0, "o"), (183, -.14, "i"), (190, 0, "o"), (197, -.14, "i"), (204, 0, "o"), (211, -.14, "i"), (218, 0), (240, 0)])
    a.k("rightLeg", "y", [(0, 0), (176, 0, "o"), (183, -6, "i"), (190, 0, "o"), (197, -6, "i"), (204, 0, "o"), (211, -6, "i"), (218, 0), (240, 0)])
    a.k("torso", "sy", [(0, 1), (176, 1), (190, .985), (204, 1.0), (218, .985), (240, 1)])
    blink(a, [100, 226])
    antenna(a, 120, .09)
    a.sine("leftArm", "rot", 120, .05)
    scarf(a, 120)
    A.append(a)

    # 2 · listen: inclina la cabeza y se lleva la mano al auricular
    a = Anim("listen", 120, True)
    a.sine("headRig", "rot", 60, .035, base=-.14)
    a.sine("headRig", "y", 60, 2.5, phase=.1)
    a.k("face", "x", [(0, -7), (120, -7)])
    a.k("face", "y", [(0, 1), (120, 1)])
    a.k("headphones", "x", [(0, 2.5), (120, 2.5)])
    a.sine("headphones", "sx", 30, .035, base=1.02)
    a.sine("headphones", "sy", 30, .035, base=1.02)
    swap_arm(a, "l", "leftArmFront", [(0, 120)])
    a.sine("leftArmFront", "rot", 60, .04, base=-.08, phase=.1)
    a.k("leftArmFront", "x", [(0, 6), (120, 6)])
    a.k("leftArmFront", "y", [(0, -4), (120, -4)])
    a.k("eyes", "sy", [(0, .88), (84, .88, "i"), (87, .08, "o"), (93, .88), (120, .88)])
    a.sine("torso", "rot", 120, .02, base=-.03)
    a.sine("rightArm", "rot", 60, .04)
    antenna(a, 30, .07, phase=.2)
    scarf(a, 60, amps=(.04, .07, .1))
    A.append(a)

    # 3 · receive: la señal llega: la antena vibra, mira hacia arriba, los auriculares laten
    a = Anim("receive", 120, True)
    a.sine("antenna", "rot", 12, .11)
    a.sine("antenna", "sy", 24, .05, base=1.02)
    a.k("face", "y", [(0, -7), (120, -7)])
    a.sine("face", "x", 120, 5)
    a.k("eyes", "sy", [(0, 1.1), (70, 1.1, "i"), (73, .08, "o"), (79, 1.1), (120, 1.1)])
    a.k("eyes", "sx", [(0, 1.08), (120, 1.08)])
    a.sine("headphones", "sx", 30, .045, base=1.03, phase=.25)
    a.sine("headphones", "sy", 30, .045, base=1.03, phase=.25)
    a.sine("headRig", "rot", 60, .05)
    a.sine("headRig", "y", 30, 2.5)
    a.sine("torso", "sy", 30, .015, base=1)
    a.k("torso", "rot", [(0, .025), (120, .025)])
    a.sine("rightArm", "rot", 60, .06, base=-.06)
    a.sine("leftArm", "rot", 60, .06, base=.06, phase=.5)
    scarf(a, 60, amps=(.05, .08, .12))
    A.append(a)

    # 4 · translate: «procesando»: pose pensativa, balanceo rítmico, antena girando
    a = Anim("translate", 120, True)
    swap_face(a, "facePensando", [(0, 120)])
    swap_arm(a, "r", "rightArmFront", [(0, 120)])
    swap_arm(a, "l", "lArmThink", [(0, 120)])
    a.sine("rightArmFront", "rot", 30, .035)
    a.sine("headRig", "rot", 60, .09)
    a.sine("face", "x", 60, 6, phase=.05)
    a.sine("headphones", "x", 60, -2, phase=.05)
    a.sine("headRig", "y", 30, 3, phase=.25)
    a.sine("torso", "sy", 30, .015, base=1, phase=.75)
    a.sine("antenna", "rot", 30, .16, phase=.15)
    a.sine("leftArm", "rot", 60, .04, phase=.5)
    a.k("eyes", "sy", [(0, 1), (120, 1)])
    a.k("propQuestion", "op", [(0, 0), (120, 0)])
    scarf(a, 60, amps=(.06, .1, .14))
    A.append(a)

    # 5 · speak: asiente, gesticula con la mano; la boca la mueve audioLevel
    a = Anim("speak", 60, True)
    a.sine("headRig", "rot", 30, .045)
    a.k("headRig", "y", [(0, 0, "i"), (8, 3, "o"), (22, -3), (30, 0, "i"), (38, 3, "o"), (52, -3), (60, 0)])
    a.sine("face", "x", 60, 5)
    a.sine("rightArm", "rot", 60, .2, base=-.12)
    a.sine("leftArm", "rot", 60, .06, phase=.5)
    a.sine("torso", "sy", 30, .018, base=1, phase=.75)
    a.sine("torso", "rot", 60, .02)
    antenna(a, 30, .08, phase=.2)
    blink(a, [40])
    scarf(a, 60)
    A.append(a)

    # 6 · conversation: escucha a un lado, responde al otro
    a = Anim("conversation", 120, True)
    a.k("headRig", "rot", [(0, -.12), (52, -.12, "s"), (66, .1), (112, .1, "s"), (120, -.12)])
    a.k("face", "x", [(0, -9), (52, -9, "s"), (66, 9), (112, 9, "s"), (120, -9)])
    a.k("headphones", "x", [(0, 3), (52, 3, "s"), (66, -3), (112, -3, "s"), (120, 3)])
    a.k("headRig", "y", [(0, 0), (14, 2), (28, 0), (42, 2), (56, 0), (72, 3, "o"), (82, -3), (92, 3, "o"), (102, -3), (120, 0)])
    a.k("rightArm", "rot", [(0, 0), (56, 0, "o"), (70, -.32), (80, -.2), (90, -.34), (100, -.2), (112, -.1, "s"), (120, 0)])
    a.k("leftArm", "rot", [(0, .05), (30, .1), (56, .05), (120, .05)])
    a.k("torso", "rot", [(0, -.03), (56, -.03, "s"), (68, .03), (112, .03, "s"), (120, -.03)])
    a.sine("torso", "sy", 30, .012, base=1)
    blink(a, [24, 96])
    antenna(a, 60, .08)
    scarf(a, 60)
    A.append(a)

    # 7 · explain: anticipa, levanta el índice con rebote, guiña y vuelve
    a = Anim("explain", 96, False)
    a.k("torso", "sy", [(0, 1), (8, .95, "o"), (16, 1.03, "io"), (26, 1), (96, 1)])
    a.k("torso", "rot", [(0, 0), (8, -.02), (18, .045), (74, .045, "io"), (90, 0), (96, 0)])
    swap_arm(a, "r", "rArmPoint", [(12, 80)])
    a.k("rightArm", "rot", [(0, 0), (10, .14, "h"), (12, .35, "el"), (34, 0), (40, 0, "io"), (46, -.07), (52, .02), (58, -.06), (64, 0), (76, 0, "i"), (80, .12, "o"), (92, 0), (96, 0)])
    a.k("rightArm", "sx", [(0, 1), (12, .85, "el"), (34, 1), (96, 1)])
    a.k("rightArm", "sy", [(0, 1), (12, .85, "el"), (34, 1), (96, 1)])
    a.k("headRig", "rot", [(0, 0), (8, -.03), (20, .1, "el"), (40, .1), (76, .1, "io"), (92, 0), (96, 0)])
    a.k("headRig", "y", [(0, 0), (8, 5, "o"), (18, -4), (30, 0), (96, 0)])
    a.k("face", "x", [(0, 0), (16, 0, "o"), (26, 9), (76, 9, "io"), (90, 0), (96, 0)])
    a.k("headphones", "x", [(0, 0), (16, 0, "o"), (26, -3), (76, -3, "io"), (90, 0), (96, 0)])
    swap_face(a, "faceGuino", [(48, 64)])
    a.sine("leftArm", "rot", 48, .05, start=0, end=96, phase=.5)
    antenna(a, 32, .12, phase=.2, env=lambda t: max(.25, 1 - t / 110))
    scarf(a, 48, amps=(.07, .12, .17))
    A.append(a)

    # 8 · wave: se agacha, levanta la mano abierta y saluda con destellos y guiño
    a = Anim("wave", 100, False)
    a.k("character", "sy", [(0, 1), (8, .93, "o"), (16, 1.04), (26, 1), (100, 1)])
    a.k("character", "sx", [(0, 1), (8, 1.05, "o"), (16, .98), (26, 1), (100, 1)])
    swap_arm(a, "r", "rArmWave", [(10, 84)])
    a.k("rightArm", "rot", [(0, 0), (9, .1, "h"), (10, .45, "el"), (26, 0), (30, 0), (38, .2), (46, -.12), (54, .2), (62, -.12), (70, .2), (78, 0, "i"), (84, .12, "o"), (96, 0), (100, 0)])
    a.k("torso", "rot", [(0, 0), (16, .035), (30, .035), (38, .05), (46, .02), (54, .05), (62, .02), (70, .05), (80, .035, "io"), (96, 0), (100, 0)])
    a.k("headRig", "rot", [(0, 0), (8, .03), (22, -.11, "el"), (44, -.11), (80, -.11, "io"), (96, 0), (100, 0)])
    a.k("headRig", "y", [(0, 0), (8, 6, "o"), (18, -5), (30, 0), (100, 0)])
    a.k("face", "x", [(0, 0), (12, 0, "o"), (22, 7), (80, 7, "io"), (94, 0), (100, 0)])
    swap_face(a, "faceGuino", [(46, 64)])
    blink(a, [80])
    a.k("propRays", "op", [(0, 0, "h"), (16, 0, "l"), (20, 1), (74, 1, "l"), (84, 0), (100, 0)])
    a.k("propRays", "sx", [(0, .2, "h"), (16, .2, "el"), (36, 1), (100, 1)])
    a.k("propRays", "sy", [(0, .2, "h"), (16, .2, "el"), (36, 1), (100, 1)])
    a.sine("propRays", "rot", 16, .08, start=30, end=78)
    a.sine("leftArm", "rot", 50, .06, phase=.5)
    antenna(a, 24, .14, phase=.2, env=lambda t: max(.2, 1 - t / 110))
    scarf(a, 32, amps=(.08, .13, .19), env=lambda t: max(.35, 1 - t / 140))
    A.append(a)

    # 9 · walk: camina en el sitio con rebote, balanceo y bufanda al viento
    a = Anim("walk", 40, True)
    a.k("leftLeg", "rot", [(0, -.2), (20, .2), (40, -.2)])
    a.k("rightLeg", "rot", [(0, .2), (20, -.2), (40, .2)])
    a.k("leftLeg", "y", [(0, 0), (10, -12, "o"), (20, 0, "i"), (40, 0)])
    a.k("rightLeg", "y", [(0, 0), (20, 0), (30, -12, "o"), (40, 0, "i")])
    a.k("leftLeg", "x", [(0, -10), (20, 12), (40, -10)])
    a.k("rightLeg", "x", [(0, 12), (20, -10), (40, 12)])
    a.k("soles", "op", [(0, 0), (40, 0)])
    a.k("torso", "y", [(0, 0, "o"), (10, -8, "i"), (20, 0, "o"), (30, -8, "i"), (40, 0)])
    a.k("torso", "sy", [(0, .975, "o"), (10, 1.02, "i"), (20, .975, "o"), (30, 1.02, "i"), (40, .975)])
    a.sine("torso", "rot", 40, .05)
    a.sine("headRig", "rot", 40, .05, phase=.62)
    a.k("headRig", "y", [(0, 2), (12, -3), (20, 2), (32, -3), (40, 2)])
    a.k("rightArm", "rot", [(0, -.25), (20, .2), (40, -.25)])
    a.k("leftArm", "rot", [(0, -.2), (20, .25), (40, -.2)])
    a.k("face", "x", [(0, 3), (40, 3)])
    antenna(a, 20, .13, phase=.3)
    scarf(a, 20, amps=(.07, .13, .19), base=(.12, .14, .16), lag=.15)
    blink(a, [26])
    A.append(a)

    # 10 · turn: salta y se gira a tres cuartos; aterriza, se balancea y vuelve
    a = Anim("turn", 110, False)
    a.k("character", "sy", [(0, 1), (8, .9, "o"), (18, 1.07), (28, .96, "o"), (38, 1, "el"), (70, 1), (78, .92, "o"), (88, 1.05), (96, .95, "o"), (106, 1), (110, 1)])
    a.k("character", "sx", [(0, 1), (8, 1.06, "o"), (18, .96), (28, 1.04, "o"), (38, 1), (70, 1), (78, 1.05, "o"), (88, .97), (96, 1.04, "o"), (106, 1), (110, 1)])
    a.k("character", "y", [(0, 0), (8, 0, "o"), (18, -30, "i"), (28, 0), (78, 0, "o"), (88, -24, "i"), (96, 0), (110, 0)])
    a.k("front", "op", [(0, 1, "h"), (14, 1, "l"), (20, 0, "h"), (84, 0, "l"), (90, 1, "h"), (110, 1)])
    a.k("threeQuarter", "op", [(0, 0, "h"), (14, 0, "l"), (20, 1, "h"), (84, 1, "l"), (90, 0, "h"), (110, 0)])
    a.k("threeQuarter", "rot", [(0, 0), (28, 0), (40, .04), (52, -.03), (64, .02), (76, 0), (110, 0)])
    a.k("headRig", "rot", [(0, 0), (8, .04), (18, -.05), (28, 0), (88, .05), (100, -.03), (110, 0)])
    scarf(a, 30, amps=(.06, .1, .15))
    A.append(a)

    # 11 · celebrate: anticipa, salta dos veces con brazos arriba, ojos felices y check
    a = Anim("celebrate", 120, False)
    a.k("character", "sy", [(0, 1), (10, .88, "o"), (18, 1.1), (30, 1.02, "i"), (40, .9, "o"), (50, 1.07), (60, 1, "i"), (68, .92, "o"), (82, 1, "el"), (120, 1)])
    a.k("character", "sx", [(0, 1), (10, 1.08, "o"), (18, .94), (30, 1, "i"), (40, 1.07, "o"), (50, .96), (60, 1, "i"), (68, 1.05, "o"), (82, 1, "el"), (120, 1)])
    a.k("character", "y", [(0, 0), (10, 0, "o"), (26, -44, "i"), (40, 0, "o"), (52, -26, "i"), (66, 0), (120, 0)])
    a.k("character", "rot", [(0, 0), (10, 0), (26, -.04), (40, 0), (52, .035), (66, 0), (120, 0)])
    swap_face(a, "faceSatisfecha", [(10, 96)])
    a.k("rightArm", "rot", [(0, 0), (10, .25, "el"), (30, -1.3), (40, -1.05), (52, -1.4), (64, -1.12), (76, -1.32), (88, -1.25, "io"), (104, .08, "o"), (114, 0), (120, 0)])
    a.k("leftArm", "rot", [(0, 0), (10, -.25, "el"), (30, 1.3), (40, 1.05), (52, 1.4), (64, 1.12), (76, 1.32), (88, 1.25, "io"), (104, -.08, "o"), (114, 0), (120, 0)])
    a.k("headRig", "y", [(0, 0), (10, 8, "o"), (20, -6), (40, 5, "o"), (52, -4), (66, 3, "o"), (78, 0), (120, 0)])
    a.k("headRig", "rot", [(0, 0), (26, .05), (52, -.05), (78, 0), (120, 0)])
    a.k("propCheck", "op", [(0, 0, "h"), (16, 0, "l"), (20, 1), (100, 1, "l"), (110, 0), (120, 0)])
    a.k("propCheck", "sx", [(0, 0, "h"), (16, 0, "el"), (40, 1), (120, 1)])
    a.k("propCheck", "sy", [(0, 0, "h"), (16, 0, "el"), (40, 1), (120, 1)])
    a.k("propCheck", "y", [(0, 20), (16, 20, "o"), (40, 0), (100, -8), (120, -8)])
    a.k("propRays", "op", [(0, 0, "h"), (40, 0, "l"), (44, 1), (90, 1, "l"), (100, 0), (120, 0)])
    # destellos reflejados a la izquierda de la cabeza (el check ocupa la derecha)
    a.k("propRays", "sx", [(0, -.2, "h"), (40, -.2, "el"), (60, -1.1), (120, -1.1)])
    a.k("propRays", "sy", [(0, .2, "h"), (40, .2, "el"), (60, 1.1), (120, 1.1)])
    a.k("propRays", "x", [(0, -372), (120, -372)])
    a.k("propRays", "y", [(0, -6), (120, -6)])
    antenna(a, 20, .16, phase=.2, env=lambda t: max(.15, 1 - t / 120))
    scarf(a, 26, amps=(.1, .16, .24), base=(.08, .1, .12), env=lambda t: max(.25, 1 - t / 130))
    A.append(a)

    # 12 · error: se sobresalta, ojos en X, sacude la cabeza, aviso; suspira y se recompone
    a = Anim("error", 100, False)
    a.k("character", "sy", [(0, 1), (5, 1.06, "o"), (12, .94), (22, 1, "el"), (64, 1), (74, .95, "io"), (90, 1), (100, 1)])
    a.k("character", "y", [(0, 0), (5, -10, "i"), (12, 0), (100, 0)])
    a.show("faceSorpresa", [(2, 12)])
    a.show("faceError", [(12, 76)])
    a.hide("faceDefault", [(2, 76)])
    a.k("rightArm", "rot", [(0, 0), (3, -.2, "el"), (20, -.85), (40, -.8, "io"), (56, 0, "o"), (100, 0)])
    a.k("leftArm", "rot", [(0, 0), (3, .2, "el"), (20, .85), (40, .8, "io"), (56, 0, "o"), (100, 0)])
    a.sine("headRig", "rot", 10, .13, start=8, end=58, env=lambda t: max(0, 1 - (t - 8) / 50))
    a.k("headRig", "y", [(0, 0), (5, -6), (12, 6, "o"), (24, 2), (66, 2, "io"), (76, 7, "io"), (92, 0), (100, 0)])
    a.k("torso", "rot", [(0, 0), (6, -.04), (16, .02), (28, 0), (100, 0)])
    a.k("torso", "sy", [(0, 1), (66, 1, "io"), (76, .96, "io"), (92, 1), (100, 1)])
    a.k("propWarn", "op", [(0, 0, "h"), (8, 0, "l"), (12, 1), (74, 1, "l"), (82, 0), (100, 0)])
    a.k("propWarn", "sx", [(0, 0, "h"), (8, 0, "el"), (30, 1), (100, 1)])
    a.k("propWarn", "sy", [(0, 0, "h"), (8, 0, "el"), (30, 1), (100, 1)])
    a.sine("propWarn", "rot", 14, .12, start=10, end=70, env=lambda t: max(0, 1 - (t - 10) / 60))
    a.k("face", "x", [(0, 0), (100, 0)])
    antenna(a, 12, .2, phase=.25, env=lambda t: max(0, 1 - t / 80))
    scarf(a, 14, amps=(.08, .13, .2), env=lambda t: max(.05, 1 - t / 90))
    A.append(a)

    # 13 · blink: parpadeo con un pequeño gesto de cabeza
    a = Anim("blink", 16, False)
    a.k("eyes", "sy", [(0, 1, "i"), (4, .06, "o"), (10, 1.06), (16, 1)])
    a.k("headRig", "y", [(0, 0), (4, 2), (12, 0), (16, 0)])
    A.append(a)
    return A


# ---------------------------------------------------------------- RML
REST = {}


def keyframe(parent, frame, value, ease):
    attrs = {"frame": str(frame), "value": f"{value:.6g}"}
    if ease == "h":
        attrs["interpolationType"] = "0"
        ET.SubElement(parent, "KeyFrameDouble", attrs)
    elif ease == "l":
        attrs["interpolationType"] = "1"
        ET.SubElement(parent, "KeyFrameDouble", attrs)
    elif ease == "el":
        attrs["interpolationType"] = "4"
        kf = ET.SubElement(parent, "KeyFrameDouble", attrs)
        ET.SubElement(kf, "ElasticInterpolator", {"easingValue": "1", "amplitude": "1", "period": "0.35"})
    else:
        attrs["interpolationType"] = "2"
        kf = ET.SubElement(parent, "KeyFrameDouble", attrs)
        x1, y1, x2, y2 = EASE[ease]
        ET.SubElement(kf, "CubicEaseInterpolator", {"x1": str(x1), "y1": str(y1), "x2": str(x2), "y2": str(y2)})


def main():
    from PIL import Image as PILImage
    import numpy as np

    PROJECT.mkdir(parents=True, exist_ok=True)
    for old in PROJECT.glob("*.png"):
        old.unlink()
    for old in PROJECT.glob("*.svg"):
        old.unlink()
    for name, (src, chain, keep) in LAYERS.items():
        svg = PROJECT / f"{name}.svg"
        svg.write_text(xml_text(isolate(src, chain, keep)))
        raster(svg, PROJECT / f"{name}.png", size=H)
        svg.unlink(missing_ok=True)
    raster(THREE_QUARTERS, PROJECT / "threeQuarter.png", size=H)

    ids = RML()
    doc = ET.Element("Rive", {"version": "1", "kind": "fragment"})
    art_id, machine_id, layer_id, style_id = ids.id(), ids.id(), ids.id(), ids.id()
    vm_id, audio_property_id, motion_property_id, vm_instance_id, converter_id = (ids.id() for _ in range(5))
    art = ET.SubElement(doc, "Artboard", {"id": art_id, "name": "Beca", "width": str(W), "height": str(H),
                                          "styleId": style_id, "defaultStateMachineId": machine_id,
                                          "viewModelId": vm_id, "viewModelInstanceId": vm_instance_id})
    ET.SubElement(art, "LayoutComponentStyle", {"id": style_id, "name": "Artboard Style"})

    obj = {}        # nombre -> id
    elem = {}       # nombre -> elemento XML
    world = {}
    assets = {}
    # En Rive el primer hijo se pinta encima: NODES va de delante hacia atrás.
    for name, parent, pivot, images, opacity in NODES:
        world[name] = pivot
        container = art if parent is None else elem[parent]
        px, py = (0, 0) if parent is None else world[parent]
        lx, ly = pivot[0] - px, pivot[1] - py
        node_id = ids.id()
        attrs = {"id": node_id, "name": name, "x": f"{lx:g}", "y": f"{ly:g}"}
        if opacity != 1:
            attrs["opacity"] = str(opacity)
        if name == "stage":
            attrs.update({"scaleX": str(STAGE_SCALE), "scaleY": str(STAGE_SCALE)})
        node = ET.SubElement(container, "Node", attrs)
        obj[name], elem[name] = node_id, node
        REST.update({(name, X): lx, (name, Y): ly, (name, ROT): 0, (name, SX): 1, (name, SY): 1, (name, OP): opacity})
        for image in images:
            asset_id = assets.setdefault(image, ids.id())
            img = ET.SubElement(node, "Image", {"id": ids.id(), "name": f"{image}Image", "assetId": asset_id, "x": "0", "y": "0",
                                                "originX": f"{pivot[0] / W:.6f}", "originY": f"{pivot[1] / H:.6f}"})
            if image == "mouth":
                ET.SubElement(img, "DataBindContext", {"sourcePathIds": f"{vm_id}-{audio_property_id}", "propertyKey": "17", "converterId": converter_id})
        if name == "scarfKnot":
            build_scarf(ids, elem["torso"], node, world, obj, assets, np, PILImage)

    # ---- máquina de estados
    machine = ET.SubElement(art, "StateMachine", {"id": machine_id, "name": "BecaMachine"})
    layer = ET.SubElement(machine, "StateMachineLayer", {"id": layer_id, "name": "Default"})
    any_state = ET.SubElement(layer, "AnyState", {"x": "0", "y": "-100"})
    ET.SubElement(layer, "ExitState", {"x": "420", "y": "-100"})
    entry = ET.SubElement(layer, "EntryState")

    anims = build_animations()
    assert [a.name for a in anims] == MOTIONS
    animated = sorted({key for a in anims for key in a.tracks})
    states = {}
    for index, a in enumerate(anims):
        la = ET.SubElement(art, "LinearAnimation", {"name": a.name, "id": ids.id(), "fps": str(FPS),
                                                    "duration": str(a.duration), "loopValue": "1" if a.loop else "0"})
        # Cada animación fija la pose completa: las pistas que no usa vuelven al reposo.
        tracks = dict(a.tracks)
        for key in animated:
            if key not in tracks:
                tracks[key] = [(0, REST[key], "h")]
        by_object = {}
        for (name, prop), keys in tracks.items():
            by_object.setdefault(name, []).append((prop, keys))
        for name in sorted(by_object):
            ko = ET.SubElement(la, "KeyedObject", {"objectId": obj[name]})
            for prop, keys in sorted(by_object[name]):
                kp = ET.SubElement(ko, "KeyedProperty", {"propertyKey": str(prop)})
                for frame, value, ease in keys:
                    assert 0 <= frame <= a.duration, (a.name, name, frame)
                    if prop in (X, Y) and (name, prop) in a.tracks:
                        value = REST[(name, prop)] + value  # x/y se escriben como desplazamiento
                    keyframe(kp, frame, value, ease)
        state_id = ids.id()
        states[a.name] = state_id
        ET.SubElement(layer, "AnimationState", {"id": state_id, "animationId": la.get("id"),
                                                "x": str(160 + 125 * (index % 5)), "y": str(95 * (index // 5)), "reset": "true"})
    ET.SubElement(entry, "StateTransition", {"stateToId": states["idle"]})
    for code, name in enumerate(MOTIONS):
        mix = "40" if name == "blink" else "120"
        transition = ET.SubElement(any_state, "StateTransition", {"stateToId": states[name], "duration": mix})
        condition = ET.SubElement(transition, "TransitionViewModelCondition", {"opValue": "equal"})
        left = ET.SubElement(condition, "TransitionPropertyViewModelComparator")
        bindable = ET.SubElement(left, "BindablePropertyNumber")
        ET.SubElement(bindable, "DataBindContext", {"sourcePathIds": f"{vm_id}-{motion_property_id}", "propertyKey": "636"})
        ET.SubElement(condition, "TransitionValueNumberComparator", {"value": str(code)})

    for image, asset_id in assets.items():
        ET.SubElement(doc, "ImageAsset", {"id": asset_id, "name": image, "file": f"{image}.png"})
    ET.SubElement(doc, "DataConverterRangeMapper", {"id": converter_id, "name": "AudioToMouth", "minInput": "0", "maxInput": "1",
                                                    "minOutput": "1", "maxOutput": "1.45", "clampLower": "true", "clampUpper": "true"})
    vm = ET.SubElement(doc, "ViewModel", {"id": vm_id, "name": "BecaControls", "defaultInstanceId": vm_instance_id})
    ET.SubElement(vm, "ViewModelPropertyNumber", {"id": audio_property_id, "name": "audioLevel"})
    ET.SubElement(vm, "ViewModelPropertyNumber", {"id": motion_property_id, "name": "motion"})
    instance = ET.SubElement(vm, "ViewModelInstance", {"id": vm_instance_id, "name": "Default", "exports": "true"})
    ET.SubElement(instance, "ViewModelInstanceNumber", {"viewModelPropertyId": audio_property_id, "propertyValue": "0"})
    ET.SubElement(instance, "ViewModelInstanceNumber", {"viewModelPropertyId": motion_property_id, "propertyValue": "0"})

    (OUT / "beca-motion-codes.json").write_text(json.dumps({name: code for code, name in enumerate(MOTIONS)}, indent=2) + "\n")
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


def build_scarf(ids, torso, knot, world, obj, assets, np, PILImage):
    """Cola de la bufanda: imagen con malla deformada por 3 huesos hijos del nudo."""
    alpha = np.array(PILImage.open(PROJECT / "scarfTail.png").getchannel("A"))
    ys, xs = np.nonzero(alpha > 8)
    pts = list(zip(xs[::3].tolist(), ys[::3].tolist()))
    verts, tri_bytes, half = tail_mesh(pts)
    # huesos (en el nudo, para seguir al torso y al nudo)
    kx, ky = world["scarfKnot"]
    angles = [math.atan2(b[1] - a[1], b[0] - a[0]) for a, b in zip(TAIL, TAIL[1:])]
    lengths = [math.dist(a, b) for a, b in zip(TAIL, TAIL[1:])]
    bone_ids = [ids.id() for _ in range(3)]
    parent = knot
    for i in range(3):
        rel = angles[i] - (angles[i - 1] if i else 0)
        attrs = {"id": bone_ids[i], "name": f"scarf{i}", "length": f"{lengths[i]:.4f}", "rotation": f"{rel:.6f}"}
        if i == 0:
            attrs.update({"x": f"{TAIL[0][0] - kx:g}", "y": f"{TAIL[0][1] - ky:g}"})
        parent = ET.SubElement(parent, "RootBone" if i == 0 else "Bone", attrs)
        obj[f"scarf{i}"] = bone_ids[i]
        REST.update({(f"scarf{i}", ROT): rel})
    # imagen, insertada en el torso justo detrás del nudo
    tx, ty = world["torso"]
    asset_id = assets.setdefault("scarfTail", ids.id())
    img = ET.Element("Image", {"id": ids.id(), "name": "scarfTailImage", "assetId": asset_id,
                               "x": f"{W / 2 - tx:g}", "y": f"{H / 2 - ty:g}"})
    torso.insert(list(torso).index(knot) + 1, img)
    mesh = ET.SubElement(img, "Mesh", {"id": ids.id(), "name": "TailMesh", "triangleIndexBytes": tri_bytes})
    for (vx, vy), weights in verts:
        v = ET.SubElement(mesh, "ContourMeshVertex", {"x": f"{vx - W / 2:.3f}", "y": f"{vy - H / 2:.3f}",
                                                      "u": f"{vx / W:.5f}", "v": f"{vy / H:.5f}"})
        indices, values = pack(weights)
        ET.SubElement(v, "Weight", {"indices": indices, "values": values})
    # matrices de enlace en coordenadas de mundo (incluye la escala del escenario)
    k = STAGE_SCALE
    sx, sy = to_world((W / 2, H / 2))
    skin = ET.SubElement(mesh, "Skin", {"name": "TailSkin", "xx": f"{k:g}", "yy": f"{k:g}", "tx": f"{sx:.4f}", "ty": f"{sy:.4f}"})
    for i in range(3):
        c, s = math.cos(angles[i]), math.sin(angles[i])
        bx, by = to_world(TAIL[i])
        ET.SubElement(skin, "Tendon", {"name": f"t{i}", "boneId": bone_ids[i], "xx": f"{k * c:.6f}", "xy": f"{k * s:.6f}",
                                       "yx": f"{-k * s:.6f}", "yy": f"{k * c:.6f}", "tx": f"{bx:.4f}", "ty": f"{by:.4f}"})
    print(f"bufanda: {len(verts)} vértices, semiancho {half}px")


if __name__ == "__main__":
    main()
