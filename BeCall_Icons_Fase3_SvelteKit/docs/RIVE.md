# Rive: alcance real de esta entrega

Rive queda preparado como **punto de extensión opcional**, mediante `RiveSlot.svelte` y el contrato `RiveDriver` (`src/lib/becall-icons/rive-contract.ts`). La biblioteca funciona completamente sin Rive gracias al respaldo SVG/CSS.

**No se han creado archivos `.riv` ni fuentes `.rev`**. Los diseños aprobados tienen animación CSS suficiente para los casos actuales; no existe acceso al editor oficial ni a un flujo verificable de creación de `.riv` en este entorno. No se han incluido archivos falsos. Para introducir Rive, primero se debe editar un personaje/icono y exportar un `.riv` real desde el editor, instalar y verificar un runtime compatible en el proyecto consumidor, e implementar el adaptador con sus llamadas de limpieza y gestión de estados.

Candidatos justificados para Rive en una iteración posterior: transición de traducción (escucha→procesamiento→habla) y micrófono expresivo. No se debe imponer Rive a los 47 iconos estándar ni a la bandeja de Windows. Esta decisión puede tomarla el agente integrador de la fase 4 si se crea un recurso y se valida explícitamente; no es una dependencia de la biblioteca entregada.

`RiveSlot` monta su `driver` solo en cliente; con `driver` ausente o `reducedMotion=true` muestra el `BeCallIcon` aprobado. El adaptador debe respetar la preferencia del usuario y no iniciarse cuando no hay actividad real.
