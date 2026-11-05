# Beca — Pack de mascota BeCall en SVG editables

Beca es la mascota de estilo simpático 2.5D para una aplicación de traducción simultánea. Basada en el concepto mostrado en la hoja original de propuestas de BeCall.

Este paquete ofrece **24 SVG independientes y vectoriales** con elementos editables: formas, grupos, curvas y degradados. No son imágenes PNG incrustadas dentro de SVG.

## Contenido

- `01_personaje/` (5 SVG): personaje principal y vistas frontal, tres cuartos, perfil y trasera.
- `02_expresiones/` (6 SVG): alegre, guiño, sorprendida, pensando, satisfecha y error.
- `03_estados/` (4 SVG): escuchando, traduciendo, hablando y completado.
- `04_interfaz/` (6 SVG): avatar de cabeza, iconos de app claro/oscuro, avatar compacto y estados escuchando/hablando animados.
- `05_marca/` (3 SVG): los dos logos originales de BeCall aportados y recreación del isotipo.
- `referencias/`: imagen original aprobada por el usuario para comparar.

## Fidelidad y edición

- Son **redibujos vectoriales 2.5D** inspirados en el render original, no una vectorización exacta del dibujo 3D ni una extracción de la malla 3D.
- El personaje conserva: casco turquesa con asta de la “b”, cabeza blanca de mejillas rosadas, ojos negros, auriculares naranjas, bufanda naranja, guantes blancos y marca b en el torso.
- Se pueden editar en Inkscape, Illustrator y Figma; los SVG utilizan trazados y gradientes. Vista tres cuartos y perfil son **interpretaciones estilizadas**, no vistas geométricamente exactas de un modelo tridimensional.
- Los grupos incluyen `cabeza`, `rostro-expresion`, `auriculares`, `bufanda`, `cuerpo`, `piernas`, `brazo-izquierdo`, `brazo-derecho` y `marca-becall-pecho`.
- Los dos SVG animados usan CSS, respetando `prefers-reduced-motion` del sistema, y funcionan en navegadores/WebViews compatibles.
- Para **Rive**: se importan las formas SVG y se configura el rig y las máquinas de estados dentro de Rive; no se entrega un archivo `.riv`.

## Ejemplo para SvelteKit o Tauri

Copiar las carpetas SVG a `static/mascotas/beca/` y usar:

```svelte
<img
  src="/mascotas/beca/03_estados/01_escuchando.svg"
  alt="Beca escuchando el audio"
  width="160"
  height="173"
/>
```

## Paleta orientativa

| Uso | Color |
| --- | --- |
| Turquesa corporativo | `#007D8A` |
| Turquesa luminoso | `#1599A9` |
| Naranja BeCall | `#F57C1F` |
| Azul tinta | `#243B4C` |
| Blanco | `#FFFFFF` |
| Rubor | `#F8B9AE` |

**Marca:** Los dos SVG originales de BeCall se incluyen intactos. Los personajes, poses y el isotipo recreado no sustituyen las versiones oficiales del logotipo.
