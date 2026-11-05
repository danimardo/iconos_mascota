# BeCall Icons — Fase 3 · Kit independiente SvelteKit

Estado: **entrega técnica para revisión y para otro agente**. Se ha construido una biblioteca basada en los **63 SVG aprobados** de la fase 2; **no** se ha integrado ni modificado la aplicación de traducción real.

## Contenido

- `src/lib/becall-icons`: 47 iconos UI con tres variantes ópticas, componente Svelte y adaptador Lucide, 16 recursos SVG estáticos, tokens CSS, CSS de estados, opción de Rive con respaldo SVG.
- `src/routes/+page.svelte`: laboratorio que usa **los propios componentes de la biblioteca**; búsqueda, categorías, 6 tamaños, temas, estados, animación, comparar original y movimiento reducido.
- `assets-windows/`: PNG/ICO existentes, que corresponden a los 12 estados de bandeja SVG y recursos de aplicación.
- `static/originales`: 63 SVG originales para el comparador y documentación de migración.
- `tests/lab.spec.ts`: pruebas de ejemplo para Playwright (requieren instalar dependencias).
- `scripts/validate-assets.mjs`: control offline real de 63 mapeos y 157 SVG.
- `docs/HANDOFF_FASE4_PARA_OTRO_AGENTE.md`: instrucciones para un agente diferente, sin ejecutar la fase 4.

## Cómo iniciar el laboratorio

Requisitos: Node.js >=20, npm, acceso a registro de paquetes npm.

```bash
npm install
npm run dev
# abre http://127.0.0.1:5173
npm run check
npm run build
npx playwright install chromium
npm run test:e2e
```

Validación que NO requiere instalar dependencias:

```bash
npm run test:assets
```

**Limitación del entorno original de creación:** no fue posible acceder al registro npm (`EAI_AGAIN`). Por tanto, no se afirma haber ejecutado `npm install`, `svelte-check`, `vite build` ni Playwright E2E en este ambiente. La verificación estructural offline está disponible y ejecutada de forma independiente.

## Uso del componente

```svelte
<script lang="ts">
  import { BeCallIcon, LucideCompat } from '$lib/becall-icons';
  let state: 'idle' | 'listening' = 'listening';
</script>
<BeCallIcon name="microphone" size={32} {state} animated label="Micrófono activo" />
<LucideCompat name="Settings" size={24} decorative />
```

Importa una vez `tokens.css` y `motion.css` en el layout global (ya configurado en el laboratorio). `decorative` se usa si el control padre tiene etiqueta accesible; en caso contrario, usa `label`. Este icono **no es un botón**: el componente de la aplicación gestiona click/focus/teclado.

## Recursos estáticos

- `<BeCallAsset name="bandeja-escuchando-oscuro" size={32} />` para vista web de recursos nativos (en tray real usar `assets-windows`).
- `<BeCallAsset name="icono-app" size={64} />`.
- `<BeCallAsset name="guia-smartscreen" size={220} />`; preserva los `data-key` del SVG.

## SVG y temas

Las variables CSS (`--bc-primary`, `--bc-accent`, etc.) se aplican a SVG **inline**. Los SVG cargados como `<img>` o un recurso Windows/PNG/ICO no heredan las variables CSS del documento. El código `src/lib/becall-icons/svg-source.ts` importa únicamente archivos locales auditados con Vite `?raw`.

## Animaciones y Rive

Los estados `idle` no activan bucles. `listening`, `speaking`, `processing`, `connecting` activan movimientos suaves, cuando se envían desde el estado real de la app. Se respeta `prefers-reduced-motion`. `RiveSlot` ofrece un contrato opcional y usa respaldo SVG; **no se incluyen `.riv` reales**. Consulta `docs/RIVE.md`.

## Alcance explícito

- Sí: biblioteca de iconos, contrato de estados, adaptador, laboratorio, documentación y pruebas reproducibles.
- No: cambios al código de la app principal, sustitución de importaciones Lucide, pruebas Tauri/Windows ni fase 4.
