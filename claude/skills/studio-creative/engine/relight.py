"""Etapa 2: fondo y luz fotografica con bloqueo de identidad.

Lo unico que se delega a la IA es lo que no se puede hacer con pixeles.

El texto de IDENTITY_LOCK no es decorativo: es la diferencia medida entre un
render que conserva al cliente y uno que devuelve a otra persona parecida. Ver
spec seccion 2. No lo suavices ni lo resumas.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Permite invocar el script por ruta absoluta desde cualquier carpeta.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import kie
import profiles

# Prompt quirurgico validado. La clave es tratar a la persona como capa
# recortada intocable, en vez de pedir preservacion dentro de un encargo amplio.
IDENTITY_LOCK = (
    "Edit ONLY the background of this photograph. Do NOT modify the person in any way "
    "whatsoever: keep every pixel of their face, head, hair, haircut, beard, ears, neck, "
    "jewellery, shoulders and clothing exactly identical to the input, including the exact "
    "same head angle, the exact same pose and the exact same facial expression. Do not "
    "re-render, re-pose, rotate, slim, reshape or beautify the person. Treat the person as a "
    "locked, untouchable cut-out layer that must be preserved pixel for pixel. "
)

# Las esquinas grises las deja el enderezado de la etapa 1. Hay que decirle
# explicitamente que son lienzo vacio, o las interpreta como parte de la escena.
RELLENO_GRIS = (
    "The flat grey filler areas at the corners and edges of the frame are empty canvas and "
    "MUST be filled in with the new background so that no grey remains. "
)

# Sin esto el recorte canta: el borde queda duro y se ve pegado.
INTEGRACION = (
    "Match the direction and quality of the light on the new background to the existing light "
    "on the subject so the composite is physically believable, and add a subtle soft rim of "
    "light along the outline of the hair, ears and shoulders where they meet the new "
    "background, so the edge does not look like a hard cut-out. The final image must look like "
    "a single photograph taken in a real photography studio, not a composite."
)

# Version relajada para sujetos que no son personas identificables.
LOCK_MODERADO = (
    "Preserve the main subject faithfully: keep its shape, proportions, colours, texture and "
    "position essentially unchanged, and do not replace it with a different object or person. "
)


def construir_prompt(prompt_fondo: str, identity_lock: str = "estricto",
                     hay_relleno_gris: bool = True) -> str:
    """Ensambla el prompt final segun el nivel de bloqueo de identidad."""
    partes = []
    if identity_lock == "estricto":
        partes.append(IDENTITY_LOCK)
    elif identity_lock == "moderado":
        partes.append(LOCK_MODERADO)
    # 'libre' no antepone bloqueo alguno.

    partes.append(prompt_fondo.strip())
    if hay_relleno_gris:
        partes.append(RELLENO_GRIS)
    if identity_lock in ("estricto", "moderado"):
        partes.append(INTEGRACION)
    return " ".join(p.strip() for p in partes if p.strip())


def relight(src: str | Path, dest: str | Path, perfil: dict,
            fondo: str | None = None,
            modelo: str = kie.MODEL_PRO,
            resolucion: str = "2K",
            ratio: str = "4:5",
            hay_relleno_gris: bool = True,
            identity_lock: str | None = None,
            prompt_extra: str = "") -> Path:
    """Reemplaza el fondo y la luz conservando al sujeto."""
    nombre_fondo, prompt_fondo = profiles.fondo(perfil, fondo)
    nivel = identity_lock or perfil["identity_lock"]

    prompt = construir_prompt(prompt_fondo, nivel, hay_relleno_gris)
    if prompt_extra:
        prompt = f"{prompt} {prompt_extra.strip()}"

    print(f"  fondo '{nombre_fondo}', identity_lock={nivel}, modelo={modelo}")

    url = kie.upload_image(src)

    if modelo == kie.MODEL_PRO:
        entrada = {
            "prompt": prompt,
            "image_input": [url],
            "aspect_ratio": ratio,
            "resolution": resolucion,
            "output_format": "png",
        }
    else:
        entrada = {
            "prompt": prompt,
            "image_urls": [url],
            "aspect_ratio": ratio,
            "output_format": "png",
        }

    return kie.run(modelo, entrada, dest, label="fondo")


def _cli() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Etapa 2: fondo y luz con identity lock")
    p.add_argument("src")
    p.add_argument("-o", "--out")
    p.add_argument("-p", "--perfil", default="barberia")
    p.add_argument("-f", "--fondo", help="Nombre del fondo dentro del perfil")
    p.add_argument("-m", "--modelo", default=kie.MODEL_PRO,
                   choices=(kie.MODEL_PRO, kie.MODEL_EDIT))
    p.add_argument("--resolucion", default="2K", choices=("1K", "2K", "4K"))
    p.add_argument("-r", "--ratio", default="4:5")
    p.add_argument("--identity-lock", choices=profiles.NIVELES_IDENTITY,
                   help="Sobreescribe el nivel del perfil")
    p.add_argument("--sin-relleno-gris", action="store_true",
                   help="La entrada no viene de un enderezado con esquinas grises")
    p.add_argument("--extra", default="", help="Instruccion adicional para el prompt")
    p.add_argument("--dry-run", action="store_true", help="Mostrar el prompt y no llamar a la API")

    a = p.parse_args()
    src = Path(a.src)
    perfil = profiles.load(a.perfil)

    if a.dry_run:
        nombre, prompt_fondo = profiles.fondo(perfil, a.fondo)
        nivel = a.identity_lock or perfil["identity_lock"]
        print(f"--- fondo '{nombre}', identity_lock={nivel} ---")
        print(construir_prompt(prompt_fondo, nivel, not a.sin_relleno_gris))
        return

    dest = Path(a.out) if a.out else src.parent / f"{src.stem.split('__')[0]}__02-render.png"
    relight(src, dest, perfil,
            fondo=a.fondo,
            modelo=a.modelo,
            resolucion=a.resolucion,
            ratio=a.ratio,
            hay_relleno_gris=not a.sin_relleno_gris,
            identity_lock=a.identity_lock,
            prompt_extra=a.extra)
    print(f"  guardado {dest}")


if __name__ == "__main__":
    _cli()
