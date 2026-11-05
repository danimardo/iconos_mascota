# Guía para integrar los recursos Rive en RealTime-Translate

## Fuentes de autoridad y alcance

Leer primero `AGENTS.md`, `.specify/memory/constitution.md`, `historias.md`, `ARCHITECTURE.md`, las specs aplicables y `docs/diseno/entrega/v3/` del repositorio de la app. La entrega actual es un **paquete de recursos y propuesta de integración**. Incorporar a Beca y los `.riv` a la app cambia el diseño y el comportamiento: actualizar los documentos de producto y obtener la aprobación de sesión exigida por ese repositorio antes de implementar allí. Este paquete no altera esos documentos.

El clon revisado de `/Apps/RealTime-Translate` (commit `545aa30`, rama `main`) aún no contiene `src/` ni `src-tauri/` de la app. Por eso los nombres de componentes y eventos que siguen son objetivos de integración, no afirmaciones de una implementación existente.

## Inventario y semántica

`manifest.json` contiene las 47 familias y sus nombres públicos. Cada `.riv` tiene los artboards `compact`, `standard`, `large`, correspondientes a las tres variantes ópticas de los SVG. Los nombres de animación comunes son `idle`, `hover`, `pressed`, `selected`, `focus`, `disabled`. Las animaciones funcionales solo aparecen donde `functionalStates` las permite en el catálogo original: `listening`, `processing`, `speaking`, `success`, `error`, `warning`, `muted`, `connecting`, `disconnected`, `paused`, `completed`.

El estado `idle` de los iconos es estático. `hover`, `pressed`, `selected` y `focus` son movimientos breves. `processing`, `connecting`, `listening` y `speaking` son bucles cuando el estado real persiste. Los demás estados son cambios breves o poses. **No inferir actividad de `animated=true`**: un icono de micrófono solo debe escuchar cuando el núcleo indica escucha real. Al salir de un estado funcional, reproducir `idle` o mostrar la pose estática correspondiente.

| Recurso | Estado visual | Fuente de verdad que debe consultar el integrador |
|---|---|---|
| `activity` | `listening`, `processing`, `speaking` | Estado de la sesión, presentado por el núcleo Rust. |
| `microphone`, `headphones`, `language` | `listening` | Canal de entrada activo y su rol; `language` significa audio entrante en el mismo idioma. |
| `radio`, `audio-lines` | `speaking` | Salida traducida frente a voz real; no intercambiar los dos significados. |
| `translation`, `captions` | `processing` | Trabajo real de traducción o subtítulos. |
| `cable`, `waypoints`, `connection` | `connecting`, `disconnected`, `error`, `success` | Estado del enrutador, CABLE-A/B y red; preservar la prioridad de S1 y S6. |
| `download` | `processing`, `success`, `error` | Ciclo real de actualización. |

El icono de bandeja de Windows, el icono de ejecutable y el instalador **siguen siendo recursos estáticos**. Un `.riv` dentro de una WebView no anima automáticamente la bandeja nativa. Usar los PNG/ICO existentes y el mapa de estados de S6.

## Adaptador Svelte 5 / Tauri 2

1. Seleccionar y fijar una versión del runtime web oficial de Rive en el plan de la app; comprobar su compatibilidad con WebView2 y su licencia antes de incorporarla. Cargar `.riv` locales desde los recursos de la aplicación. No cargar archivos Rive externos ni contenido de usuarios.
2. Crear un componente Svelte 5 en `src/shared/ui/` con `runes` y un adaptador del contrato `name`, `variant`, `state`, `size`, `reducedMotion`. El `RiveSlot.svelte` del laboratorio usa sintaxis Svelte 4 y **no debe copiarse sin adaptación**. Mantener los SVG existentes como respaldo.
3. Elegir `compact`, `standard` o `large` según la regla óptica del catálogo: hasta 20 px compacto; de 24 a 32 estándar; desde 48 grande; de 33 a 47 estándar. El artboard se escala al tamaño solicitado. Al cambiar `name` o artboard, desmontar el anterior y liberar runtime, canvas y listeners.
4. Traducir el estado funcional del núcleo a una animación nombrada del `manifest.json`. Si falta el nombre o el `.riv` falla, mostrar el SVG equivalente. No iniciar bucles cuando la sesión no esté activa. No reproducir animación alguna cuando Windows active «reducir movimiento»; mostrar una imagen estática significativa.
5. El componente que contiene el icono conserva `button`, foco, teclado, tooltip, etiqueta y anuncio de estado. El canvas Rive es decorativo si el control padre ya tiene nombre accesible. Nunca anunciar el nombre técnico del archivo como descripción de la acción.
6. Montar solo los Rive visibles. En listas largas y superficies de alto uso, medir CPU, memoria, tiempo de arranque y frecuencia de repintado en Windows 11. Comparar con los SVG actuales. El integrador decide qué animaciones activar por contexto, pero mantiene disponibles los 47 archivos.
7. Probar en Tauri 2 / WebView2 con ambas apariencias, escalado 100–200 %, cambio de tema, ventanas ocultas, dispositivos que cambian de estado y la preferencia «reducir movimiento». Verificar también CSP, empaquetado de `.riv` y limpieza al desmontar.

La app usa Svelte 5, Tauri 2 y Windows 11; el laboratorio de iconos es SvelteKit y sus componentes actuales usan Svelte 4. La integración debe respetar los límites de `AGENTS.md`: IPC en `src/shared/ipc`, textos en `src/shared/i18n/es.json` y `en.json`, y estados de negocio procedentes de Rust.

## Beca

Archivo: `riv/mascota/beca.riv`; artboard: `Beca`; máquina por defecto: `BecaMachine`. Animaciones: `idle`, `wait`, `listen`, `receive`, `translate`, `speak`, `conversation`, `explain`, `wave`, `walk`, `turn`, `celebrate`, `error`, `blink`. El View Model `BecaControls` expone `motion` (códigos en `manifest.json` y `beca-motion-codes.json`) y `audioLevel` entre **0 y 1**. Cambiar `motion` selecciona el gesto en la máquina de estados; la boca cambia con `audioLevel`. El anfitrión debe suavizar y limitar la señal para que la boca no tiemble; enviar `0` cuando termine la voz. `speak` y `conversation` animan cabeza y brazos; la boca depende de `audioLevel`. Si no hay nivel de audio disponible, un envolvente local de voz puede alimentar ese valor mientras se reproduce voz; no usar la señal de micrófono de la reunión para fingir que Beca habla.

El estado visual debe seguir una sola prioridad: `error` > `speak/conversation` > `translate` > `receive/listen` > `explain` > `walk` > `wait/idle`. Interrumpir esperas cuando llega actividad real. `turn` usa la vista tres cuartos del pack y vuelve a frontal. `walk` es una caminata en el sitio; el desplazamiento por la interfaz, si se desea, lo controla el contenedor Svelte, con límites de ventana y sin cubrir controles.

La opción de Beca como asistente contextual debe pertenecer a la configuración del usuario de la app. Puede ocultarse, silenciar sus intervenciones contextuales y volver a mostrarse desde Ayuda/Ajustes. La presencia de Beca en el asistente inicial no obliga al usuario a mantenerla activa después. No activar conversaciones o audio por la mera presencia de Beca; cualquier texto y voz proceden de la lógica y permisos de la app.

## Comprobaciones realizadas en este paquete

- `rive --once` construyó los 48 proyectos con cero errores de compilación.
- `validar.py` inspeccionó 47 archivos de icono, 141 artboards y el de Beca, sin problemas de `rive inspect`.
- `capturar.py` obtuvo seis fotogramas de animaciones reales desde el renderizador Rive y dos capturas de `audioLevel`; `preview/beca-audio-0.png` y `preview/beca-audio-1.png` muestran que el valor del View Model modifica la boca.
- No se probó el runtime dentro de la app, porque el clon contiene documentación y experimentos, aún sin código de producto.
