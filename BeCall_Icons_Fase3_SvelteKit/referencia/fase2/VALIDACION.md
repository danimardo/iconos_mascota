# Validación automática y revisión pendiente · fase 2

| Comprobación | Resultado de la generación |
|---|---|
| Inventario de origen | 63 SVG = 35 interfaz + 12 design system + 12 bandeja + 2 app + 2 guías |
| Mapeo total sin duplicados | 63/63, `docs/manifest.json` y `docs/coverage.csv` |
| SVG generados | 157, todos parseables con ElementTree y con `viewBox` |
| SVG sin raster embebido ni scripts | Validación estática sin `<image>`, `<script>`, eventos ni URL externa |
| Reutilización de prototipo | 8 iconos × 3 tamaños, comprobación binaria (24 archivos) |
| Bandeja | 12 SVG de apariencia fija + 24 PNG de 16/32 px |
| App | SVG de app/instalador, PNG 16–512, ICO multirresolución |
| Vista previa | HTML que muestra los 63 recursos con búsqueda/tema/tamaño/comparación |
| Prueba de navegador | Chromium: 63 tarjetas, tema claro/oscuro, filtrado y búsqueda; sin errores de página reportados |

**No afirmar WCAG AA superado ni regresión funcional certificada:** faltan pruebas manuales y automáticas de contraste en la UI real, una auditoría en Windows/Tauri, ensayos de accesibilidad en lectores de pantalla y revisión del comportamiento con cargas de audio reales. Esas tareas pertenecen a fases 3–4.

**Rive pendiente:** no hay archivos `.riv` porque crear archivos Rive genuinos y comprobar su runtime requiere herramientas específicas que todavía no se han utilizado; el paquete incluye SVG/CSS funcionales sin atribuirles capacidades Rive inexistentes.

**Inspección visual pendiente de aprobación humana:** formas, colores y representaciones pueden ajustarse antes de automatizar la migración. Conservar nombres y semántica no sustituye esa aprobación.

Ejecuta `python tests/validar.py` desde la raíz del paquete para repetir la validación estática. Para la vista HTML, utiliza Edge o Chrome y confirma que puede ejecutar el JavaScript local según tu política de seguridad.
