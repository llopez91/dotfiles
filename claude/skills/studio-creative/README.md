# Studio Creative — kit de edición fotográfica y publicidad

Motor para dejar fotos de negocio listas para redes sociales, y para construir
publicidad a partir de ellas.

## Instalación

Ya está instalado. Requisitos verificados: Python 3.14, Pillow 12.3, numpy 2.4.
No hace falta ImageMagick, OpenCV, requests ni ningún MCP.

La API key de Kie AI se lee de la variable de entorno `KIE_API_KEY` o del
archivo `.env` de esta carpeta.

## Las skills

| Skill | Qué hace | Créditos |
|---|---|---|
| `studio-creative` | Orquestadora: diagnostica y encadena las demás | según |
| `foto-luz` | Luminosidad, exposición, balance de blancos, sombras | 0 |
| `foto-encuadre` | Enderezar, recortar, packs por plataforma | 0 |
| `foto-fondo` | Fondo de estudio con bloqueo de identidad | 18 |
| `foto-escena` | Escena generada para campaña | 18 |
| `arte-social` | Titular, CTA, logo sobre la pieza | 0 |
| `copy-social` | Caption y hashtags | 0 |

## Dónde vive cada cosa

| | Ubicación | Por qué |
|---|---|---|
| **Herramienta** (motor + skills) | `~/.claude/skills/` | Es genérica: funciona desde cualquier carpeta |
| **Datos del cliente** (logo, colores, fotos) | `<proyecto>/clientes/<id>/` | Es lo único que cambia entre trabajos |

```
<proyecto>/clientes/<id>/
├─ marca.json     ← colores, logo, contacto, perfil de rubro
├─ marca/         ← logo y variantes, iconos, tipografías
├─ fotos/         ← originales que llegan del cliente
└─ out/           ← piezas generadas, una subcarpeta por campaña
```

El motor busca `marca.json` subiendo desde la imagen, así que apuntando a una
foto del cliente ya sabe colores, logo, contacto y dónde escribir. Sin flags.

```bash
python "$E\nuevo_cliente.py" mi-cliente -n "Nombre Comercial" -p barberia
python "$E\marca.py"                  # lista los clientes
python "$E\marca.py" mi-cliente       # ver una marca y qué le falta
```

`marca.json` puede sobreescribir el `look` y añadir `fondos` propios sin tocar
el perfil de rubro compartido.

## Uso rápido

```bash
E="C:\Users\llope\.claude\skills\studio-creative\engine"

# Saldo
python "$E\kie.py" creditos

# Perfiles disponibles
python "$E\profiles.py"

# Elegir el ángulo de enderezado (míralo y decide)
python "$E\prep.py" "foto.jpg" --contact-sheet

# Solo etapas deterministas, sin gastar
python "$E\pipeline.py" "foto.jpg" --perfil barberia --angulo 35 --sin-ia

# Pipeline completo
python "$E\pipeline.py" "foto.jpg" --perfil barberia --angulo 35 \
  --sujeto "376,272,830,836" --sujeto-espacio enderezada \
  --fondo estudio-oscuro --todos-formatos

# Arte publicitario encima
python "$E\compose.py" "out/foto__wide.png" \
  -t "Fade + barba" -c "Agenda por WhatsApp" --posicion izquierda
```

## Arquitectura

```
FOTO ──▶ [1] PREP        ──▶ [2] IA          ──▶ [3] FINISH      ──▶ PIEZAS
         Pillow, local        Kie AI              Pillow, local
         geometría + tono     fondo + luz         grade, packs, texto
         exacto, 0 créditos   18 créditos         exacto, 0 créditos
```

**La IA solo toca lo que los píxeles no pueden hacer.** No es economía, es
fidelidad: un prompt creativo amplio hace que nano-banana re-renderice al
sujeto y devuelva a otra persona. Ver el spec para las mediciones.

Una sola llamada a IA por pieza: los cuatro formatos salen del mismo render
maestro.

## Módulos

| Archivo | Responsabilidad |
|---|---|
| `kie.py` | Cliente de la API. CLI: `creditos`, `estado`, `subir` |
| `profiles.py` | Carga y valida perfiles de rubro |
| `prep.py` | Etapa 1: tono, enderezado, encuadre, hoja de contacto |
| `relight.py` | Etapa 2: fondo con bloqueo de identidad |
| `scene.py` | Etapa 2 en modo campaña |
| `finish.py` | Etapa 3: grade y formatos por plataforma |
| `compose.py` | Texto, CTA y logo |
| `pipeline.py` | Las tres etapas en un comando |

## Perfiles

`barberia` (validado), `comida`, `producto`, `inmobiliaria`, `fitness`.

Cada uno define el look tonal, los prompts de fondo y escena, los formatos
prioritarios, el tono del copy y el nivel de bloqueo de identidad. Están en
`engine/profiles/*.json` y son editables.

Para añadir un rubro: copia un JSON existente, cámbiale el `id`, ajusta los
valores y comprueba con `python profiles.py`.

## Pruebas

```bash
python engine/test_engine.py     # 43 pruebas, 0 créditos
python engine/smoke_test.py      # conectividad real, 4 créditos
```

La fidelidad de identidad no es verificable automáticamente. Tras tocar los
prompts de `relight.py`, regenera la foto de referencia y compárala contra
`out/motor/*__ig-feed.png`: el corte, la línea de barba, la pose y los rasgos
tienen que seguir siendo los del original.

## Gotchas de la API de Kie AI

Verificados contra el servidor el 2026-08-14, ya encapsulados en `kie.py`:

1. El host de upload es `kieai.redpandaai.co`, **no** `api.kie.ai` como dice la
   documentación oficial. Con el de la doc, 404.
2. El User-Agent por defecto de `urllib` recibe **403**. Hay que enviar uno propio.
3. Las URLs del resultado están en `data.resultJson`, que es un **string JSON**:
   hay que parsearlo otra vez para llegar a `resultUrls`.
4. Nombres de modelo: `nano-banana-pro` (sin prefijo, campo `image_input`) y
   `google/nano-banana-edit` (con prefijo, campo `image_urls`).
