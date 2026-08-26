---
name: foto-encuadre
description: Endereza, recorta y reencuadra fotos, y genera los packs de tamaños por plataforma (Instagram feed 4:5, story/reel 9:16, cuadrado 1:1, portada 16:9). Úsalo cuando el usuario pida "enderezar", "está torcida", "recortar", "reencuadrar", "centrar", "ponerla vertical", "adaptarla para story" o "sacar todos los tamaños" de una imagen. No usa IA.
---

# Foto — encuadre y formatos

Geometría determinista con Pillow. **No gasta créditos.**

`ENGINE` = `C:\Users\llope\.claude\skills\studio-creative\engine`

## Enderezar

El ángulo correcto no sale de una fórmula. Genera la hoja de contacto y **elige mirándola**:

```bash
python "ENGINE\prep.py" "foto.jpg" --contact-sheet
```

Ábrela (`out/foto__angulos.png`) y escoge el que deje al sujeto natural. Ángulos por defecto: 0, 15, 25, 35, 45, 55. Para afinar entre dos:

```bash
python "ENGINE\prep.py" "foto.jpg" --contact-sheet --angulos "30,33,35,37,40"
```

Luego:

```bash
python "ENGINE\prep.py" "foto.jpg" --angulo 35 --relleno blur
```

`--relleno blur` rellena las esquinas que deja la rotación con una versión desenfocada de la propia foto. Usa `--relleno gris` **solo** si después va a pasar por `foto-fondo`, que reemplaza esas zonas.

## Encuadrar alrededor del sujeto

Sin `--sujeto` recorta al centro, que casi nunca es lo que quieres en un retrato.

```bash
python "ENGINE\prep.py" "foto.jpg" --sujeto "x0,y0,x1,y1" --ratio 4:5
```

**Cómo obtener la caja: mira la imagen y lee las coordenadas del sujeto.** Encierra la parte que debe mandar en la composición — en un retrato, la cabeza (y barba si la hay), no el cuerpo entero.

### Cuidado con las fotos muy inclinadas

Si el ángulo pasa de 12°, una caja alineada a los ejes en el original se ensancha al rotar y el encuadre sale inservible. En ese caso, endereza primero y lee la caja sobre la imagen enderezada:

```bash
python "ENGINE\prep.py" "foto.jpg" --angulo 35 --solo-enderezar
# abre out/foto__00-enderezada.png, lee ahí la caja, y luego:
python "ENGINE\prep.py" "foto.jpg" --angulo 35 --sujeto "376,272,830,836" --sujeto-espacio enderezada
```

El script avisa cuando estás en ese caso.

### Afinar la composición

- `--fill` (0.52) — cuánto del alto ocupa el sujeto. Sube para un plano más cerrado.
- `--headroom` (0.15) — aire sobre la cabeza.

## Packs por plataforma

Desde una imagen ya editada:

```bash
python "ENGINE\finish.py" "imagen.png" --perfil barberia --todos
```

| Formato | Tamaño | Uso |
|---|---|---|
| `ig-feed` | 1080×1350 | Feed de Instagram y Facebook |
| `ig-square` | 1080×1080 | Feed cuadrado, cuadrícula del perfil |
| `story` | 1080×1920 | Story, Reel, TikTok, estado de WhatsApp |
| `wide` | 1920×1080 | Portada de Facebook, YouTube, web |

Solo algunos: `--formatos ig-feed,story`

### Si la pieza va a llevar titular

Un render de retrato viene encuadrado cerca del sujeto y no deja hueco para el texto. Recortar no sirve: quita justo lo que el post quiere enseñar.

```bash
python "ENGINE\finish.py" render.png --formatos ig-feed,story \
  --espacio-texto arriba-derecha --escala-sujeto 0.74
```

Escala el sujeto, lo ancla a una esquina y rellena el resto con el propio fondo del render desenfocado y oscurecido. Como el fondo de estudio ya es un degradado suave, la extensión es indistinguible — y no toca un píxel del sujeto.

Anclas: `arriba-derecha`, `arriba-izquierda`, `arriba-centro`, `abajo-derecha`, `abajo-izquierda`, `abajo-centro`. El texto va en el hueco opuesto.

### `wide` no recorta, extiende

Pasar un retrato 4:5 a 16:9 recortando decapitaría al sujeto. En su lugar se coloca el retrato a un lado y se rellena el resto con un degradado muestreado del propio fondo. El hueco oscuro que queda **es para el titular** — la pieza sale lista para `arte-social`.

Elige el lado con `--lado-wide derecha|izquierda`. El texto va al lado contrario.

## Regla importante

Si la imagen va a pasar por IA, **no generes los formatos antes**. Genera el render maestro primero y deriva los formatos de él: una sola llamada en vez de cuatro.
