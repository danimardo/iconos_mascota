# HANDOFF · BeCall Icons · Fase 4 para un agente distinto

**Esta entrega NO modifica el proyecto principal Tauri/SvelteKit.** El otro agente será responsable de la integración real y de validar el entorno final.

## Material a recibir

1. Proyecto independiente completo (`src/lib/becall-icons/` + laboratorio SvelteKit).
2. 157 SVG, 63 correspondencias, 24 PNG de bandeja, ICO y PNG de app en `assets-windows/`.
3. `docs/EQUIVALENCIAS_Y_ESTADOS.md`, contratos de componentes, tokens CSS y tests.
4. `static/originales/` para comparación (no se debe enviar a producción si no es necesario).

## Procedimiento recomendado (sin ejecutar en fase 3)

1. Analizar el repositorio real: versiones de Svelte, SvelteKit, Tauri, importaciones Lucide, claves de sistema, eventos de audio y arquitectura CSS.
2. Copiar o empaquetar `src/lib/becall-icons` dentro del proyecto consumidor; importar `tokens.css` y `motion.css` en su layout global.
3. Empezar por un subconjunto de iconos, usando `LucideCompat` cuando la migración progresiva tenga sentido.
4. Sustituir los usos de iconos manteniendo ARIA labels, focus, tamaños, tooltips y los flujos existentes; comprobar a11y y claves de estado real.
5. Mapear `listening`, `processing`, `speaking` etc. a eventos reales (no a timers simulados).
6. Probar los iconos de Windows con Tauri en un Windows 11 real, especialmente DPI, modo oscuro, estado del tray y eventos de clic. Las rutas de bandeja tienen 6 estados × 2 temas × 16/32 px.
7. Ejecutar pruebas E2E y de regresión de la aplicación principal, revisar Tauri builds y perfiles CPU/memoria.
8. Definir qué hacer con Lucide no cubiertos por las 47 equivalencias. No modificar lógica de traducción ni layout sin aprobación separada.

## Advertencias

- La propiedad `className` permite clases Svelte; no implica sustitución transparente de `class` en todas las importaciones Lucide.
- Los estilos de tema funcionan porque SVG se inyecta **inline**, no con `<img>` externo. Las variables CSS de un SVG independiente en `<img>` no heredan del tema de la app.
- Los SVG van incluidos en el código por imports `?raw` de Vite; **no permitir SVG externos o creados por usuarios**.
- El adaptador asigna nombres Lucide antiguos a IDs nuevos; no reexporta todos los componentes de `lucide-svelte`.
- Para cambiar de versión óptica usa tamaño numérico: <=20 compacto, 24–32 estándar, >=48 grande; 33–47 estándar por diseño.
- No hay pruebas en Tauri/Windows ni `.riv` real. Resolver estos puntos en el entorno de destino, sin afirmarlos como verificados.
- La fase 3 no contiene cambios a la app original. El handoff del agente integrador empieza después de aprobar este paquete.
