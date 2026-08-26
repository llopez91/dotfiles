---
name: studio-creative
description: Motor experto de edición fotográfica y publicidad para redes sociales. Úsalo cuando el usuario quiera dejar una foto lista para publicar, mejorarla para Instagram/Facebook/TikTok, hacer un anuncio o pieza publicitaria a partir de una foto, o pida "retocar", "editar", "mejorar", "dar luz", "cambiar el fondo", "encuadrar" o "hacer un post" con una imagen. Es la skill orquestadora del kit: diagnostica la foto y encadena foto-luz, foto-encuadre, foto-fondo, foto-escena, arte-social y copy-social.
---

# Studio Creative

Convierte fotos de negocio tomadas con celular en piezas publicables, sin traicionar al sujeto real.

`ENGINE` = `C:\Users\llope\.claude\skills\studio-creative\engine`

## La regla que gobierna todo

**La IA solo toca lo que los píxeles no pueden hacer.**

| Tarea | Quién | Costo |
|---|---|---|
| Enderezar, encuadrar, exposición, balance de blancos, grade, formatos, texto | Pillow, local | 0 créditos |
| Fondo, luz fotográfica, escenas de campaña | Kie AI | 18 créditos |

Esto no es economía, es fidelidad. Medido el 2026-08-14: pedirle a nano-banana un retrato de estudio con un prompt creativo amplio devuelve una foto preciosa **de otra persona** — le cambió la cara, el corte, la barba y la pose al cliente. Con el trabajo repartido así, el sujeto queda intacto.

## Bloqueo de identidad

Antes de llamar a la IA, decide el nivel:

- **Hay una persona real identificable** → `estricto`. Es el caso de barbería, fitness, retrato, equipo. Nunca lo bajes por conseguir una imagen más vistosa.
- **Persona secundaria** (de espaldas, lejana, silueta) → `moderado`.
- **Producto, comida, espacio sin personas** → `libre`.

El perfil de rubro ya trae el nivel correcto. Sobreescríbelo solo con motivo.

**Nunca adelgaces, rejuvenezcas ni "mejores" el cuerpo o la cara de una persona real sin que el usuario lo pida explícitamente.** Si lo pide sobre un cliente suyo y no sobre sí mismo, señálalo antes de hacerlo.

## Tu trabajo: mirar la foto

Los scripts ejecutan con precisión; el criterio lo pones tú. **Abre la imagen y obsérvala antes de decidir nada.**

Diagnóstico, en orden:

1. **¿Está torcida?** → hace falta enderezar. Si dudas del ángulo, genera la hoja de contacto.
2. **¿Subexpuesta, con dominante de color, sombras tapadas?** → el prep lo arregla solo.
3. **¿El fondo distrae, está sucio o delata que es un celular?** → hace falta la etapa de IA. Si el fondo ya está limpio, sáltatela y ahórrate los créditos.
4. **¿Hay una persona real?** → identity lock estricto.
5. **¿Es para publicar o para anunciar?** → si es anuncio, añade `arte-social` y `copy-social`.
6. **¿A qué plataformas va?** → determina los formatos.

## Clientes y marca

La herramienta es global; lo que cambia entre trabajos son los datos del cliente. Cada cliente vive en su carpeta:

```
<proyecto>/clientes/<id>/
├─ marca.json     ← colores, logo, contacto, perfil de rubro
├─ marca/         ← logo y variantes, iconos, tipografías
├─ fotos/         ← originales que llegan del cliente
└─ out/           ← piezas generadas, una subcarpeta por campaña
```

**La marca se resuelve sola.** El motor busca `marca.json` subiendo desde la propia imagen, así que basta apuntar a una foto de dentro de la carpeta del cliente:

```bash
python "ENGINE\pipeline.py" "clientes/lorem-barberia/fotos/corte.jpg" --todos-formatos
```

De ahí salen el perfil de rubro, los colores de marca, el logo, la línea de contacto y la carpeta de salida. Los flags que pases a mano siempre ganan sobre la marca.

```bash
python "ENGINE\marca.py"                    # lista los clientes
python "ENGINE\marca.py" lorem-barberia     # ver una marca y qué le falta
python "ENGINE\nuevo_cliente.py" <id> -n "Nombre" -p barberia
```

`--marca <id>` fuerza una marca concreta; `--sin-marca` la ignora.

### Antes de entregar, revisa lo pendiente

`marca.py` y `compose.py` avisan de los campos que siguen siendo marcador de posición (`@tuinstagram`, `tu telefono`, nombres con "lorem", logo que no existe). **Nunca des por buena una pieza con avisos PENDIENTE sin decírselo al usuario**: publicar un anuncio con el teléfono de ejemplo es un fallo caro y visible.

## Uso

### Pipeline completo

```bash
python "ENGINE\pipeline.py" "foto.jpg" --perfil barberia --angulo 35 \
  --sujeto "376,272,830,836" --sujeto-espacio enderezada \
  --fondo estudio-oscuro --todos-formatos
```

Sale todo a `<carpeta de la foto>/out/`: el prep, el render maestro y cada formato.

### Sin gastar créditos

```bash
python "ENGINE\pipeline.py" "foto.jpg" --perfil barberia --angulo 35 --sin-ia
```

Solo las etapas deterministas. Úsalo para probar encuadre y luz antes de pagar el render.

### Elegir el ángulo

```bash
python "ENGINE\prep.py" "foto.jpg" --contact-sheet
```

Genera una hoja con varios ángulos. **Ábrela y elige mirándola**, no calcules.

### La caja del sujeto

`--sujeto x0,y0,x1,y1` encuadra alrededor del sujeto en vez de recortar al centro.

- **Foto derecha o poco inclinada** (< 12°): lee la caja sobre el original. `--sujeto-espacio original` (por defecto).
- **Foto muy inclinada**: la caja del original se deforma al rotar. Primero endereza y lee la caja ahí:

```bash
python "ENGINE\prep.py" "foto.jpg" --angulo 35 --solo-enderezar
# abre out/foto__00-enderezada.png, lee la caja, y luego:
python "ENGINE\pipeline.py" "foto.jpg" --angulo 35 --sujeto "376,272,830,836" --sujeto-espacio enderezada
```

### Perfiles

```bash
python "ENGINE\profiles.py"     # lista los perfiles y sus fondos
```

`barberia` (validado), `comida`, `producto`, `inmobiliaria`, `fitness`.

### Créditos

```bash
python "ENGINE\kie.py" creditos
```

## Reglas de costo

- **Una sola llamada a IA por pieza.** Los formatos se derivan del mismo render maestro. Pedirle cada formato a la IA cuesta 4× y produce versiones inconsistentes del mismo post.
- Antes de un lote, comprueba el saldo.
- Si el usuario solo quiere luz o encuadre, no llames a la IA en absoluto.

## Si el render sale mal

Los intermedios quedan en disco. Reintenta desde el prep, no desde la foto:

```bash
python "ENGINE\relight.py" "out/foto__01-prep.png" --perfil barberia --fondo barberia-bokeh
```

Para ver el prompt sin gastar nada: añade `--dry-run`.

## Skills del kit

| Skill | Cuándo |
|---|---|
| `foto-luz` | Solo luz, exposición, color |
| `foto-encuadre` | Solo enderezar, recortar, formatos |
| `foto-fondo` | Reemplazar el fondo conservando al sujeto |
| `foto-escena` | Escena inventada para campaña |
| `arte-social` | Titular, CTA, logo sobre la pieza |
| `copy-social` | Caption y hashtags |

## Al terminar

Muestra al usuario las piezas generadas y di qué formato es cada una. Si gastaste créditos, di cuántos.
