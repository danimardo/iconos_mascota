# Beca en el asistente de primera configuración y el tutorial

Esta es una **propuesta de contenido y movimiento** para integrar en el flujo S4 de `docs/diseno/entrega/v3/pantallas/S4-asistente.md`. Conserva sus siete pasos, la posibilidad de terminar más tarde, los estados completado/pendiente/omitido y las validaciones existentes. Los textos deben aprobarse e incorporarse a `es.json` y `en.json` de la app; los de abajo son borradores en español.

## Primera configuración, S4

| Pantalla existente | Aparición y animación de Beca | Borrador de ayuda breve | Reacción funcional |
|---|---|---|---|
| 1 · Idioma | `wave`, luego `idle` | «Hola, soy Beca. Vamos a preparar BeCall paso a paso.» | Cambiar de idioma actualiza texto; Beca no tapa las tarjetas. |
| 2 · Clave | `explain` junto al panel de ayuda; `translate` solo mientras se valida | «Aquí se comprueba tu clave. No se envía audio durante esta prueba.» | `celebrate` tras validación correcta; `error` en fallo, sin sustituir el mensaje de error. Nunca mostrar la clave. |
| 3 · Auriculares | `listen` durante la prueba de sonido | «Elige dónde quieres oír la reunión y prueba si llega el sonido.» | Al confirmar que se oye, `celebrate` breve. No reproducir voz de Beca por el canal de la reunión. |
| 4 · Micrófono | `receive` mientras se comprueba el nivel; `listen` durante la grabación local | «Prueba tu micrófono y escucha la grabación. Esta prueba se queda en tu equipo.» | Beca no toma el micrófono ni graba por sí misma. |
| 5 · Cables | `explain` al señalar CABLE-A/B; `translate` durante la verificación | «CABLE-A trae la reunión; CABLE-B lleva tu voz a la llamada.» | `error` si falta uno; respetar el aviso previo a verificar CABLE-B y no minimizarlo. |
| 6 · Teams/Zoom | `walk` breve hacia la ilustración y `explain` | «En Teams o Zoom, el altavoz será CABLE-A Input y el micrófono CABLE-B Output.» | `listen` en la comprobación de llegada de sonido; `celebrate` solo tras resultados reales. |
| 7 · Privacidad | `idle` sin bucle adicional; gesto `explain` al entrar | «Antes de usarla, lee el recordatorio de privacidad.» | No pronunciar ni resumir de modo que sustituya el texto completo o la casilla obligatoria. |
| Final | `celebrate`, luego `idle` | «Ya puedes empezar. Si dejaste algún paso pendiente, podrás retomarlo en Ajustes.» | Solo celebrar lo realmente completado; mostrar pendientes como hace S4. |

Beca ocupa una zona reservada dentro del cuerpo del asistente, con tamaño adaptable y sin alterar orden de foco, ancho mínimo ni el pie fijo. En 960 × 640 y con escalado 200 %, puede reducirse a avatar o desaparecer si el contenido funcional necesita espacio. El `Stepper`, los controles y los avisos mantienen la prioridad visual y de accesibilidad. `prefers-reduced-motion` usa pose estática.

## Tutorial posterior opcional

Propuesta de **cinco tarjetas**, repetibles desde Ayuda, separadas de la configuración técnica. Se muestran solo las funciones disponibles en la versión instalada; el botón «Omitir» y la salida están siempre disponibles. Cada tarjeta debe poder recorrerse con teclado y leerse sin animación.

| Tarjeta | Idea que explica | Beca | Acción de aprendizaje |
|---|---|---|---|
| 1 · La isla | La isla muestra el estado del enrutador aun sin traducir. | `explain` | Identificar «Sin traducir» y abrir la ventana completa. |
| 2 · Escuchar | Iniciar la escucha de la reunión; confirmar por el estado real, no por el movimiento. | `listen` | Localizar el control Escuchar y reconocer el indicador activo. |
| 3 · Traducción | El audio entrante pasa por escucha, procesamiento y resultado. | `receive` → `translate` → `celebrate` | Reconocer la diferencia entre original y traducción; mostrar subtítulos si están disponibles. |
| 4 · Tu voz | El habla traducida usa la salida configurada; al detenerla puede volver la voz real. | `speak` con `audioLevel`, luego `explain` | Localizar silenciar y detener; explicar el estado «te oyen» sin prometer aislamiento que la app no garantice. |
| 5 · Ayuda y control | La configuración y los avisos se pueden consultar; Beca contextual es opcional. | `wave` | Elegir si Beca aparecerá como asistente contextual y cómo volver a abrir este tutorial. |

En la versión que aún no incluya Hablar, Perfiles o Histórico, la tarjeta correspondiente se omite o explica su disponibilidad real. No simular en una demostración que una traducción o un dispositivo funciona si no hay sesión activa; para un ejemplo didáctico usar una muestra claramente etiquetada como tal.

## Beca contextual, elegida por el usuario

La preferencia «Mostrar a Beca como asistente» controla apariciones fuera de S4 y del tutorial. Si está activa, Beca puede ofrecer ayuda contextual en errores recuperables, configuración incompleta y funciones recién descubiertas. Cada aparición tiene cierre inmediato, no cubre controles ni subtítulos y no roba el foco. Las esperas largas usan `wait` con pausas; al iniciarse una sesión o llegar un aviso importante se interrumpen. El usuario puede desactivar estas apariciones desde Ajustes o el menú de Beca y seguir usando toda la app.

La decisión de activar a Beca después del onboarding debe ser explícita. Recomendación: desactivada hasta que el usuario la elija en la tarjeta final del tutorial o en Ajustes. No agregar una ventana flotante permanente sin revisar el diseño de ventanas, la exclusión de captura y la prioridad de la isla.
