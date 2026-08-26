---
name: foto-escena
description: Genera con IA una escena o escenario completo alrededor del sujeto para campañas publicitarias — promociones, temporadas, lanzamientos. Úsalo cuando el usuario pida "ponerlo en otro lugar", "crear un escenario", "una escena para la promo", "ambientar la foto", "fondo de campaña" o "imagen para el anuncio de X". Usa IA y cuesta créditos. Para solo limpiar el fondo real, usa foto-fondo.
---

# Foto — escena de campaña

Modo creativo: aquí la IA **sí** construye un escenario nuevo. Lo que se libera es el entorno, nunca el sujeto.

`ENGINE` = `C:\Users\llope\.claude\skills\studio-creative\engine`

**Cuesta 18 créditos por imagen.**

## Diferencia con `foto-fondo`

| | `foto-fondo` | `foto-escena` |
|---|---|---|
| Encargo | Limpiar y relightear lo que hay detrás | Inventar un entorno nuevo |
| Riesgo de identidad | Bajo | **Alto** — el encargo amplio es justo donde el modelo recompone a la persona |
| Bloqueo | Estándar | Estándar **+ refuerzo específico** |

Por eso `scene.py` añade una instrucción extra: *si no puedes colocarlo en la escena nueva sin alterarlo, déjalo intacto y adapta la escena*. Revisa siempre el resultado contra el original antes de darlo por bueno.

## Uso

Escena del perfil:

```bash
python "ENGINE\scene.py" "foto.jpg" --perfil barberia --escena promo
```

Escena a medida:

```bash
python "ENGINE\scene.py" "foto.jpg" --perfil barberia \
  --brief "Coloca al sujeto en una barbería premium con luz cálida de neón azul al fondo, muy desenfocada, ambiente nocturno"
```

Ver el prompt sin gastar: `--dry-run`

## Espacio para el titular

Por defecto el prompt pide dejar espacio negativo limpio donde luego irá el titular y el CTA. Es lo que quieres casi siempre, porque la pieza sigue a `arte-social`.

Desactívalo con `--sin-espacio-texto` solo si la imagen es final y no lleva texto.

## Escenas por perfil

`python "ENGINE\profiles.py"` lista las disponibles.

**barberia:** `promo`, `antes-despues`, `temporada`
**fitness:** `promo`, `reto`
**comida:** `promo`, `menu-nuevo`
**producto:** `lanzamiento`, `estilo-de-vida`
**inmobiliaria:** `promo`

## Escribir un buen brief

Lo que funciona, en este orden:

1. **Dónde** — el tipo de espacio, concreto.
2. **La luz** — dirección, temperatura, dureza. Es lo que más cambia el resultado.
3. **La profundidad** — casi siempre "muy desenfocado", para que el sujeto mande.
4. **Qué eliminar** — "sin desorden, sin carteles, sin gente al fondo".

Lo que no funciona: adjetivos sueltos ("bonito", "profesional", "moderno") y pedir texto dentro de la imagen. **El texto va con `arte-social`**, que lo compone localmente y sale nítido; los modelos de imagen todavía deforman las letras.

## Perfiles con `identity_lock: libre`

En `comida`, `producto` e `inmobiliaria` la IA tiene mano libre sobre el entorno. Aun así, en inmobiliaria los prompts prohíben mover o añadir muebles: enseñar una casa con mobiliario que no existe es engañoso, y eso no lo decide el modelo.
