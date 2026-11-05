# BeCall Icons — API y equivalencias

Este fichero documenta el registro generado a partir del catálogo aprobado de la fase 2. **No renombra ni reinterpretada** las funciones especiales de audio.

## Correspondencia Lucide y nuevos iconos

| Original en aplicación | Nuevo nombre BeCall | Significado | Estados funcionales |
|---|---|---|---|
| `activity` / `Activity` | `activity` | Sesión — Pantalla principal de traducción | listening, processing, speaking |
| `app-window` / `AppWindow` | `app-window` | Ventana principal — Abrir la ventana completa | — |
| `arrow-down` / `ArrowDown` | `arrow-down` | Abajo — Ordenación descendente | — |
| `arrow-left` / `ArrowLeft` | `arrow-left` | Anterior — Navegar hacia la izquierda | — |
| `arrow-right` / `ArrowRight` | `arrow-right` | Siguiente — Navegar hacia la derecha | — |
| `arrow-up` / `ArrowUp` | `arrow-up` | Arriba — Ordenación ascendente | — |
| `audio-lines` / `AudioLines` | `audio-lines` | Audio directo — Tu voz se emite sin traducir | speaking, muted |
| `cable` / `Cable` | `cable` | Cable virtual — Dispositivos CABLE-A/B | connecting, disconnected, error |
| `captions` / `Captions` | `captions` | Subtítulos — Mostrar u ocultar subtítulos | processing, success |
| `chevron-down` / `ChevronDown` | `chevron-down` | Desplegar — Expandir o bajar | — |
| `chevron-up` / `ChevronUp` | `chevron-up` | Contraer — Subir o ampliar | — |
| `circle-x` / `CircleX` | `circle-x` | Descartar — Error o cerrar | error |
| `coins` / `Coins` | `coins` | Consumo — Consumo de servicio y límite de gasto | — |
| `wifi-off` / `WifiOff` | `connection` | Sin conexión — Servicio desconectado | connecting, disconnected, success, error |
| `crosshair` / `Crosshair` | `crosshair` | Posicionar — Selector de posición | — |
| `download` / `Download` | `download` | Actualizar — Descargar una actualización | processing, success, error |
| `ellipsis` / `Ellipsis` | `ellipsis` | Más acciones — Menú contextual | — |
| `circle-alert` / `CircleAlert` | `error` | Error — Error general de sesión | error |
| `file-text` / `FileText` | `file-text` | Plantillas — Documentos de contexto o glosario | — |
| `gauge` / `Gauge` | `gauge` | Diagnóstico — Medidores técnicos | — |
| `headphones` / `Headphones` | `headphones` | Auriculares — Escuchando el audio de entrada | listening, error |
| `history` / `History` | `history` | Histórico — Reuniones y transcripciones previas | — |
| `info` / `Info` | `info` | Información — Información general | selected |
| `key-round` / `KeyRound` | `key-round` | Clave de API — Falta clave de API | — |
| `keyboard` / `Keyboard` | `keyboard` | Teclado — Atajos de teclado | — |
| `ear` / `Ear` | `language` | Idioma entendido — Audio entrante en el mismo idioma | listening, success |
| `loader` / `Loader` | `loader` | Conectando — Actividad de conexión o detención | processing, connecting |
| `loader-circle` / `LoaderCircle` | `loader-circle` | Cargando — Actividad de componente | processing, connecting |
| `mic-off` / `MicOff` | `mic-off` | Micrófono silenciado — Audio de salida silenciado | muted, error |
| `mic` / `Mic` | `microphone` | Micrófono — Audio de salida y control de silencio | listening, muted, error |
| `pause` / `Pause` | `pause` | Pausa — Pausar una grabación | paused |
| `pin` / `Pin` | `pin` | Fijar — Fijar posición de subtítulos | — |
| `play` / `Play` | `play` | Reproducir — Reproducir una grabación | speaking, paused |
| `plus` / `Plus` | `plus` | Añadir — Crear un elemento nuevo | — |
| `radio` / `Radio` | `radio` | Transmitiendo — Emitiendo voz traducida | speaking, muted, error |
| `scale` / `Scale` | `scale` | Comparar — Comparación o ponderación | — |
| `settings` / `Settings` | `settings` | Ajustes — Configuración | processing |
| `sliders-horizontal` / `SlidersHorizontal` | `sliders-horizontal` | Ajustar — Ajustes de la superposición | — |
| `square` / `Square` | `square` | Detener — Detener sesión | — |
| `circle-check` / `CircleCheck` | `success` | Correcto — Estado de éxito | success |
| `languages` / `Languages` | `translation` | Traducción — Traducción entre idiomas | processing, success, error |
| `triangle-alert` / `TriangleAlert` | `triangle-alert` | Advertencia — Dispositivo ausente o precaución | warning, error |
| `user-round` / `UserRound` | `user-round` | Perfiles — Perfiles de configuración | — |
| `waypoints` / `Waypoints` | `waypoints` | Enrutamiento — Router de audio listo | connecting, success, error |
| `x` / `X` | `x` | Cerrar — Cerrar modo edición | — |
| `zoom-in` / `ZoomIn` | `zoom-in` | Ampliar — Aumentar zoom | — |
| `zoom-out` / `ZoomOut` | `zoom-out` | Reducir — Disminuir zoom | — |

## Contrato de interacción

- Estados generales: `idle`, `hover`, `pressed`, `selected`, `disabled`, `focus`.
- Estados funcionales: `listening`, `processing`, `speaking`, `success`, `error`, `warning`, `muted`, `connecting`, `disconnected`, `paused`, `completed`.
- El laboratorio limita los estados funcionales al catálogo `functionalStates` de cada icono; en otros casos retorna a `idle`.
- En el componente directo, el desarrollador debe enviar estados con significado real; no inferir que `animated=true` significa actividad.
- `interfaz/ear.svg` significa **mismo idioma de entrada**, no selector de idioma.
- `interfaz/audio-lines.svg` indica **mismo idioma de salida**.
- `interfaz/headphones.svg`: audio entrante; `mic.svg`: audio saliente local; `radio.svg`: audio traducido emitido.
- La bandeja de Windows utiliza exclusivamente recursos PNG/SVG **estáticos** (seis estados × dos temas); ninguna animación web se transfiere a Windows automáticamente.
