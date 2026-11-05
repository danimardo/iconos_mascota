# Entrega Rive · BeCall

## Contenido

- [`riv/iconos/`](riv/iconos/): **47 archivos `.riv`**, uno por familia del catálogo aprobado. Cada archivo tiene artboards `compact`, `standard` y `large` y animaciones nombradas.
- [`riv/mascota/beca.riv`](riv/mascota/beca.riv): Beca con 14 animaciones y un View Model `BecaControls` (`motion` y `audioLevel`).
- [`manifest.json`](manifest.json): nombres, estados, variantes, tamaños y SHA-256 de cada binario.
- [`preview/`](preview/): catálogo de iconos y fotogramas capturados por el renderizador de Rive.
- [`visor/index.html`](visor/index.html): galería interactiva local con los `.riv` reales. Se abre directamente en el navegador, sin servidor ni conexión.
- [`proyectos/`](proyectos/): fuentes RML y capas PNG editables de cada `.riv`.
- [`generar.py`](generar.py), [`generar_beca.py`](generar_beca.py), [`validar.py`](validar.py), [`capturar.py`](capturar.py): generación y comprobación reproducible.
- [`INTEGRACION.md`](INTEGRACION.md): instrucciones para el agente integrador.
- [`ONBOARDING_Y_TUTORIAL.md`](ONBOARDING_Y_TUTORIAL.md): propuesta de uso de Beca en el asistente de siete pasos y tutorial posterior.

## Construcción y verificación

Esta entrega se generó con Rive CLI **1.7.0**, disponible aquí en `/home/danimardo/.rive/bin/rive`. La CLI no está en el `PATH` actual. La generación requiere Python 3, Pillow y `ffmpeg` con soporte SVG. Para reconstruir:

```bash
/home/danimardo/miniforge3/bin/python rive_entrega/generar.py
/home/danimardo/miniforge3/bin/python rive_entrega/generar_beca.py
/home/danimardo/miniforge3/bin/python rive_entrega/validar.py
/home/danimardo/miniforge3/bin/python rive_entrega/capturar.py
/home/danimardo/miniforge3/bin/python rive_entrega/preparar_visor.py
```

`validar.py` exige 47 `.riv`, 141 artboards, las animaciones esperadas y cero problemas de `rive inspect`. `--once` crea archivos sin firma; estos proyectos no contienen scripts, por lo que la firma de scripts no se necesita para reproducirlos. Las capturas son fotogramas, no pruebas en la aplicación Tauri ni en Windows 11.

Los generadores llevan la ruta de esta instalación en la constante `CLI`; si se ejecutan en otra máquina, hay que apuntarla a su Rive CLI. Los `.riv` entregados no dependen de esa ruta.

Después de cambiar cualquier `.riv`, ejecutar `preparar_visor.py` para actualizar los datos embebidos del visor. Abre [`visor/index.html`](visor/index.html) con un navegador moderno para recorrer todas las animaciones. Consulta [`visor/README.md`](visor/README.md) para los controles.

## Naturaleza de las imágenes

Los `.riv` contienen **capas PNG embebidas** generadas a partir de los SVG existentes. Las animaciones, las capas, las transformaciones y los artboards son editables en RML; las curvas originales se editan en los SVG de `BeCall_Icons_Fase3_SvelteKit` y `Beca_SVG` y luego se regeneran. Los iconos se rasterizaron a 240 × 240 px para un artboard de 24 × 24 y Beca a 512 × 552 px. El resultado conserva el dibujo aprobado a los tamaños de interfaz previstos, pero el interior de cada capa no es vector nativo de Rive. No se generó `.rev`, que requiere autenticación de Rive CLI; las fuentes RML quedan en este paquete.

## Rig de Beca (v2, más expresivo)

`generar_beca.py` construye a Beca como un personaje articulado, no como capas sueltas:

- **Jerarquía**: `stage > character > front > torso > headRig > face`. La cabeza arrastra ojos, boca, mofletes, auriculares y antena; los brazos y la bufanda siguen al torso.
- **Bufanda**: nudo rígido más cola con una malla de 26 vértices deformada por tres huesos (`scarf0..2`). Ondea con retraso entre huesos, como tela.
- **Expresiones y poses** sacadas de `Beca_SVG/02_expresiones`: guiño, sorprendida, pensando, satisfecha y error; brazo saludando, índice arriba y mano en la barbilla o en el auricular; destellos, «?», check y aviso.
- **Movimiento**: curvas cubic/elastic, anticipación, estiramiento y compresión en saltos, parpadeos y movimiento secundario de antena y bufanda.
- Beca se dibuja al **90 %** sobre la base del artboard (512 × 552, sin cambios) para que los saltos no se corten.

| Gesto | Tipo | Duración | Qué hace |
|---|---|---|---|
| `idle` | bucle | 8 s | respira, mira a los lados, parpadea |
| `wait` | bucle | 4 s | mira alrededor, cara pensativa con «?», golpea el pie |
| `listen` | bucle | 2 s | inclina la cabeza con la mano en el auricular |
| `receive` | bucle | 2 s | la antena vibra, mira arriba, los auriculares laten |
| `translate` | bucle | 2 s | pose pensativa, balanceo rítmico |
| `speak` | bucle | 1 s | asiente y gesticula; la boca sigue a `audioLevel` |
| `conversation` | bucle | 2 s | escucha a un lado y responde al otro |
| `walk` | bucle | 0,67 s | pasos con rebote; la bufanda vuela |
| `explain` | una vez | 1,6 s | levanta el índice con rebote y guiña |
| `wave` | una vez | 1,67 s | saluda con la mano abierta, destellos y guiño |
| `turn` | una vez | 1,83 s | salta, gira a tres cuartos y vuelve |
| `celebrate` | una vez | 2 s | dos saltos con brazos en V, ojos felices y check |
| `error` | una vez | 1,67 s | sobresalto, ojos en X, aviso y sacudida |
| `blink` | una vez | 0,27 s | parpadeo |

Los gestos de una vez terminan en la pose de reposo; después, el anfitrión debe volver a poner `motion = 0` (`idle`). Los nombres, los códigos `motion` y el View Model no cambian respecto a la versión anterior.

**Requisitos para regenerar**: el ffmpeg de miniforge no decodifica SVG, así que `generar_beca.py` antepone `/usr/bin` al `PATH` para usar el ffmpeg del sistema. Las capturas necesitan una pantalla; sin escritorio, ejecutar `xvfb-run -a /home/danimardo/miniforge3/bin/python rive_entrega/capturar.py`.

## Estado de integración

La aplicación [`RealTime-Translate`](/Apps/RealTime-Translate/README.md) sigue sin código de producto en el clon revisado: contiene especificaciones, diseños y experimentos. Esta entrega no escribe en ese repositorio. El documento de integración se basa en el diseño vigente v3, el contrato de estados y las reglas de `AGENTS.md`; el agente integrador deberá verificar el código real cuando exista.
