# Galería HTML de BeCall

Abre `index.html` directamente en Chrome, Edge o Firefox. La página usa datos locales embebidos en `data.js`, así que no requiere servidor, conexión ni cuenta de Rive. Los archivos que se reproducen son los 48 `.riv` de `../riv/`, empaquetados por `../preparar_visor.py`.

## Controles

- Beca recorre automáticamente 14 gestos. «Detener recorrido» deja escoger uno. «Nivel de voz» modifica el View Model `BecaControls.audioLevel`; durante «Hablar» y «Conversar» el recorrido mueve la boca automáticamente.
- Los iconos visibles reproducen un estado de ejemplo. Cada tarjeta permite escoger todas las animaciones de su archivo y repetir el gesto. Los movimientos breves se repiten con una pausa para poder verlos.
- La barra del catálogo filtra por nombre, cambia entre las tres variantes ópticas y pausa o reanuda las animaciones. Los iconos fuera de pantalla se pausan para ahorrar recursos.
- Si el sistema solicita «reducir movimiento», la página inicia en estado estático.

## Archivos locales y licencia

`vendor/rive.js` y `vendor/rive.wasm` proceden de `@rive-app/canvas` **2.47.0**, paquete con licencia MIT de [Rive](https://github.com/rive-app/rive-wasm). `vendor/package.json` conserva su identificación. `data.js` contiene copias codificadas de los 48 `.riv`, el manifiesto y el WASM para poder abrir el HTML con `file://`; no editarlo a mano. El visor usa la API de animaciones nombradas disponible en esa versión para los iconos. Beca se controla mediante su máquina de estados y el View Model.

Si se regeneran recursos:

```bash
/home/danimardo/miniforge3/bin/python rive_entrega/validar.py
/home/danimardo/miniforge3/bin/python rive_entrega/preparar_visor.py
```

La construcción de recursos Rive y las capturas de Rive CLI están verificadas. El sandbox de esta sesión bloqueó la apertura de navegadores y servidores locales, por lo que la reproducción interactiva del HTML debe comprobarse al abrirlo en un navegador del equipo.
