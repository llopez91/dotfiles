---
name: copy-social
description: Escribe el texto del post para redes sociales — gancho, caption, llamada a la acción y hashtags, adaptado al rubro y a la plataforma. Úsalo cuando el usuario pida "el texto del post", "la descripción", "un caption", "qué escribo", "hashtags" o "el copy" para Instagram, Facebook, TikTok o WhatsApp.
---

# Copy social

El texto del post. No hay script: lo escribes tú, con el tono del perfil del negocio.

`ENGINE` = `C:\Users\llope\.claude\skills\studio-creative\engine`

## Antes de escribir

Lee el bloque `copy` del perfil: `python "ENGINE\profiles.py"` y el JSON en `ENGINE\profiles\<perfil>.json`. Trae el tono, si lleva emojis, los hashtags base y ejemplos de CTA.

**Si la imagen está a mano, míralas.** El caption tiene que hablar de lo que se ve — el fade concreto, el plato concreto — no de generalidades intercambiables.

## Estructura

1. **Gancho** (primera línea) — es lo único que se ve sin pulsar "más". Concreto y con algo en juego.
2. **Cuerpo** — dos o tres líneas. Qué es, por qué importa.
3. **CTA** — una acción clara.
4. **Hashtags** — al final, separados del cuerpo.

## Reglas

- **Escribe en español natural**, del país del usuario si lo sabes. Nada de traducciones literales del inglés.
- **Concreto sobre adjetivo.** "Fade a cero con la barba perfilada a navaja" gana a "Un trabajo de calidad profesional".
- **Frases cortas.** Se lee en el móvil, a medio scroll.
- **Un solo CTA.** Dos compiten y no se cumple ninguno.
- **Nada de promesas que el negocio no puede cumplir** — ni descuentos, horarios o precios que no te hayan dado. Si te falta el dato, deja `[precio]` y dilo.
- **Emojis solo si el perfil los activa**, y pocos. En `producto` e `inmobiliaria` van desactivados a propósito.

## Hashtags

- **8 a 15.** Más no ayuda y se lee como spam.
- Mezcla: los base del perfil + los específicos de la pieza + los locales (`#barberiabogota`, el barrio, la ciudad).
- **El local es el que más trabaja** para un negocio de barrio. Pregunta la ciudad si no la sabes.

## Por plataforma

| Plataforma | Longitud | Nota |
|---|---|---|
| Instagram feed | 3–6 líneas + hashtags | El gancho lo es todo |
| Story | 1 frase | Va sobre la imagen, no debajo |
| TikTok | 1–2 líneas | Hashtags dentro del texto |
| Facebook | Puede ser más largo | Menos hashtags, 3–5 |
| WhatsApp estado | 1 frase + teléfono | Sin hashtags |

## Entrega

Escribe el copy **listo para pegar**, en un bloque de código para que se copie de una. Si el usuario pidió varias plataformas, un bloque por cada una. Ofrece dos versiones de gancho si la pieza es importante — elegir es más fácil que redactar.

Si el pipeline generó piezas, guarda el copy junto a ellas en `out/<base>__copy.md`.
