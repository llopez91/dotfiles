---
name: arte-social
description: Compone arte publicitario sobre una foto ya editada — titular, subtítulo, precio, botón de CTA, logo y datos de contacto. Úsalo cuando el usuario pida "ponerle texto", "hacer un flyer", "añadir el precio", "poner el logo", "un banner", "arte para la promo" o "que diga X en la imagen". No usa IA: el texto se compone localmente y sale nítido.
---

# Arte social

Composición publicitaria con Pillow. **No gasta créditos.**

`ENGINE` = `C:\Users\llope\.claude\skills\studio-creative\engine`

## Por qué local y no con IA

Los modelos de imagen siguen deformando el texto pequeño, y en un anuncio el número de teléfono tiene que estar bien. Compuesto localmente sale nítido, alineado y **dice exactamente lo que escribiste**.

Nunca pidas texto dentro del prompt de `foto-fondo` ni `foto-escena`. Pídeles espacio limpio, y pon el texto aquí.

## Uso

```bash
python "ENGINE\compose.py" "imagen.png" \
  -t "Fade + barba" \
  -s "Reserva tu turno esta semana" \
  -c "Agenda por WhatsApp" \
  --contacto "@tubarberia  ·  555 123 4567" \
  --posicion abajo
```

Sale a `imagen__arte.png`.

## Anatomía

| Elemento | Flag | Notas |
|---|---|---|
| Titular | `-t` | Se pone en mayúsculas y se ajusta solo hasta caber en 3 líneas |
| Subtítulo | `-s` | Cuerpo normal |
| CTA | `-c` | Pastilla redondeada con el color de acento |
| Contacto | `--contacto` | Línea fina al pie |
| Logo | `--logo ruta.png` | PNG con transparencia; va a una esquina |

Todo es opcional. Un titular y un CTA suelen bastar.

## Posición

`--posicion abajo|arriba|izquierda|derecha`

- **`abajo`** — por defecto. Va bien en retratos verticales donde la cara está arriba.
- **`izquierda` / `derecha`** — para el formato `wide`. **El texto va al lado contrario del sujeto**: si generaste el wide con `--lado-wide derecha`, aquí usa `--posicion izquierda`.

El scrim (degradado oscuro que garantiza la lectura) se coloca automáticamente en el borde donde va el texto. Ajústalo con `--scrim 0` a `1`.

## Escribir el titular

- **Corto.** Dos o tres palabras. Se lee en el scroll o no se lee.
- **Concreto sobre genérico.** "Fade + barba" gana a "Calidad profesional".
- El precio, si va, en el subtítulo — no en el titular.
- El CTA es una acción: "Agenda tu cita", no "Información".

## Colores de marca

| Flag | Qué tiñe |
|---|---|
| `--acento` | Pastilla del CTA. Por defecto `#E8B23A` |
| `--color-titular` | El titular. Por defecto, igual que el texto |
| `--color-texto` | Subtítulo y contacto. Por defecto blanco |
| `--color-cta-texto` | Texto dentro de la pastilla. Por defecto casi negro |

**Comprueba el contraste antes de usar un color de marca.** El acento lleva texto oscuro encima: si el acento es oscuro, el CTA no se lee. Un dorado tipo `#D2BC54` da 10.5:1 contra negro y funciona tanto de titular como de fondo de pastilla; un azul marino no serviría para lo segundo.

Para sacar los colores de un logo, míralo y muestrea los píxeles dominantes — no los adivines a ojo desde una captura, que el brillo de pantalla los desvía.

## El sitio del texto

**El texto nunca puede tapar la cara ni el corte.** En un post de barbería eso es justo lo que se está vendiendo.

Si el render viene encuadrado cerca del sujeto no habrá hueco. No lo resuelvas encogiendo la tipografía: reserva espacio al exportar el formato.

```bash
python "ENGINE\finish.py" render.png --formatos ig-feed,story \
  --espacio-texto arriba-derecha --escala-sujeto 0.74
```

Eso coloca al sujeto arriba a la derecha y deja limpia la franja inferior izquierda, rellenándola con el propio fondo del render. No toca un píxel del sujeto y no cuesta créditos. Anclas: `arriba-derecha`, `arriba-izquierda`, `arriba-centro` y sus equivalentes `abajo-`.

Con espacio reservado, baja el scrim a `--scrim 0.5`: la zona ya está limpia y un scrim fuerte la ensucia.

## Márgenes por formato

`--margen 0.07` va bien en feed. **En story sube a `0.16`–`0.20`**: Instagram tapa los bordes con su interfaz y el CTA quedaría debajo de los botones.

## Titulares que caben

El titular se ajusta solo hasta caber en 3 líneas, pero tres líneas rara vez se leen bien. Un titular de una línea con el dato fuerte (`30% DTO`) y el detalle en el subtítulo gana casi siempre a meterlo todo arriba.

Evita que una palabra corta quede sola empezando línea. El motor ya sube los separadores (`·`, `y`, `de`, `en`) al renglón anterior, pero un titular más corto sigue siendo mejor solución.

## Antes de componer

El texto va **al final**, sobre la pieza ya en su formato definitivo. Si compones antes de exportar los formatos, el recorte de cada plataforma partirá el texto.

Orden correcto: editar → exportar formatos (con espacio si lleva titular) → componer sobre cada formato.
