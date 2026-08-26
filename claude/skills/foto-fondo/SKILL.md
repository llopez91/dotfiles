---
name: foto-fondo
description: Reemplaza el fondo de una foto por uno de estudio con luz fotográfica profesional, conservando al sujeto intacto. Úsalo cuando el usuario pida "cambiar el fondo", "fondo de estudio", "fondo de luz fotográfica", "quitar lo de atrás", "que parezca de estudio", "luz profesional" o "limpiar el fondo". Usa IA (Kie AI) y cuesta créditos.
---

# Foto — fondo y luz fotográfica

Lo único que se delega a la IA: la luz y el entorno que los píxeles no pueden inventar.

`ENGINE` = `C:\Users\llope\.claude\skills\studio-creative\engine`

**Cuesta 18 créditos por imagen** (`nano-banana-pro` 2K). Comprueba el saldo con `python "ENGINE\kie.py" creditos`.

## El bloqueo de identidad no es opcional

Medido el 2026-08-14 sobre una foto de barbería: un prompt creativo amplio del tipo *"conviértelo en retrato de estudio"* devuelve una imagen preciosa **de otra persona** — cara, corte, barba y pose cambiados. Añadir frases de preservación dentro de ese prompt amplio **no basta**; se probó y falló igual.

Lo que sí funciona es un prompt quirúrgico que trata a la persona como capa recortada intocable y edita únicamente lo que está detrás. Eso ya está en `relight.py` y se aplica según el nivel del perfil.

**No lo bajes a `libre` para obtener una imagen más vistosa cuando hay una persona real.** En barbería, el corte que muestras tiene que ser el corte que hiciste.

## Uso

```bash
python "ENGINE\relight.py" "foto.jpg" --perfil barberia --fondo estudio-oscuro
```

Ver el prompt sin gastar nada:

```bash
python "ENGINE\relight.py" "foto.jpg" --perfil barberia --fondo estudio-oscuro --dry-run
```

## Antes de llamar

**Endereza y corrige la luz primero**, con `foto-encuadre` y `foto-luz`. Dos razones:

1. La IA re-renderiza al sujeto si le pides que además lo enderece. La rotación hazla con píxeles.
2. Con la luz ya corregida, el render parte de mejor material.

Si la entrada viene de un enderezado con `--relleno gris`, el prompt ya le dice a la IA que rellene esas esquinas. Si no, añade `--sin-relleno-gris`.

Pipeline completo en un comando: usa la skill `studio-creative`.

## Fondos disponibles

Cada perfil trae los suyos. Lista: `python "ENGINE\profiles.py"`

**barberia:** `estudio-oscuro` (validado), `estudio-claro`, `barberia-bokeh`, `degradado-negro`
**fitness:** `gimnasio-oscuro`, `estudio-oscuro`, `humo-dramatico`
**producto:** `blanco-puro`, `gris-estudio`, `podio-minimal`, `oscuro-premium`
**comida:** `mesa-rustica`, `marmol-claro`, `restaurante-bokeh`, `fondo-oscuro`
**inmobiliaria:** `luz-natural`, `cielo-limpio`, `atardecer`

En inmobiliaria los "fondos" relightean el espacio sin mover un solo mueble: el prompt lo prohíbe explícitamente, porque enseñar una casa con muebles que no existen es engañoso.

## Opciones

- `--modelo google/nano-banana-edit` — 4 créditos en vez de 18, notablemente peor. Para pruebas.
- `--resolucion 4K` — más detalle, mismo precio de tarea.
- `--ratio` — `4:5` por defecto. `auto` conserva el del original.
- `--extra "..."` — instrucción adicional al final del prompt.
- `--identity-lock estricto|moderado|libre` — sobreescribe el perfil.

## Si sale mal

Reintenta desde el prep, no desde la foto original: el trabajo determinista ya está hecho y no hay que repetirlo. Prueba otro fondo del perfil antes de tocar el prompt.

Señales de que el bloqueo falló y hay que reintentar: la cara cambió, el corte no es el mismo, la pose se movió, el sujeto adelgazó. Si pasa con `estricto`, baja la ambición del fondo (prueba `degradado-negro`, que es el más simple) antes que forzar el prompt.
