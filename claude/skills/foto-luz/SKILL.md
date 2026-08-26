---
name: foto-luz
description: Corrige luminosidad, exposición, balance de blancos, sombras y color de una foto sin usar IA. Úsalo cuando el usuario pida "dar luz", "aclarar", "se ve oscura", "corregir el color", "quitar el amarillo", "levantar sombras", "mejorar la luz" o "retocar el tono" de una imagen. No cambia el fondo ni el encuadre.
---

# Foto — luz y color

Corrección tonal determinista con Pillow. **No gasta créditos, no toca la red, no puede alterar la identidad del sujeto.**

`ENGINE` = `C:\Users\llope\.claude\skills\studio-creative\engine`

## Qué hace

1. **Balance de blancos** por gray-world atenuado — quita el tinte de interior (amarillo, verde, naranja de bombilla) sin lavar los tonos de piel.
2. **Levanta sombras** con curva gamma que protege las altas luces por encima de 0.65, para que la piel iluminada no se vaya a blanco.
3. **Contraste, saturación y brillo** según el perfil de rubro.

## Uso

```bash
python "ENGINE\prep.py" "foto.jpg" --perfil barberia --angulo 0
```

Sale a `<carpeta de la foto>/out/foto__01-prep.png`.

Si la foto ya está derecha y bien encuadrada, usa `--relleno blur` para que no queden esquinas grises:

```bash
python "ENGINE\prep.py" "foto.jpg" --perfil barberia --relleno blur
```

## Elegir el perfil

El perfil define la intensidad de cada corrección, y no son intercambiables:

| Perfil | Balance de blancos | Por qué |
|---|---|---|
| `barberia`, `fitness` | 0.6 | Neutraliza el interior sin desaturar la piel |
| `comida` | 0.35 | El tinte cálido es apetecible; corregirlo del todo enfría el plato |
| `producto` | 0.85 | El color tiene que ser fiel al artículo real |
| `inmobiliaria` | 0.75, sombras +1.35 | Los interiores llegan subexpuestos frente a las ventanas |

Ver todos: `python "ENGINE\profiles.py"`

## Ajustar a mano

Si el resultado no convence, edita el bloque `look` del perfil en
`ENGINE\profiles\<perfil>.json`:

- `gamma_sombras` — sube para abrir más las sombras (1.0 = sin cambio)
- `wb_strength` — 0 desactiva la corrección de color, 1.0 es completa
- `contraste`, `saturacion`, `brillo` — 1.0 = sin cambio
- `enfoque` — se aplica en la etapa de export, no aquí

Después de tocar un perfil, comprueba que sigue siendo válido:
`python "ENGINE\profiles.py"`

## Límite honesto

Esto corrige el tono de la luz que ya había. **No puede crear luz que no existe**: no inventa un rim light ni relumbra una cara que quedó en sombra plana. Para eso hace falta `foto-fondo`, que sí usa IA.

Si el usuario pide "luz de estudio" o "que parezca fotografía profesional", esta skill sola no basta — dilo y ofrece `foto-fondo`.
