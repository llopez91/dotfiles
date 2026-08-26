"""Escenas generadas para campana: modo creativo.

A diferencia de relight.py, aqui la IA SI puede construir un escenario nuevo.
Sigue habiendo bloqueo de identidad cuando hay una persona real: lo que se
libera es el entorno, nunca el sujeto.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Permite invocar el script por ruta absoluta desde cualquier carpeta.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import kie
import profiles
from relight import IDENTITY_LOCK, INTEGRACION, LOCK_MODERADO

# En modo escena el encargo es mas amplio, asi que el bloqueo tiene que ser mas
# insistente todavia: es justo donde el modelo tiende a recomponer a la persona.
REFUERZO_ESCENA = (
    "Even though the scene around them changes completely, the person themselves must remain "
    "byte-for-byte the same individual: same face, same haircut, same facial hair, same body, "
    "same clothing, same pose and same expression as the input. If you cannot place them in the "
    "new scene without altering them, keep them unaltered and adapt the scene instead. "
)

ESPACIO_TEXTO = (
    "Leave clean, uncluttered negative space in the composition where a headline and a call to "
    "action can be placed later without covering the subject. "
)


def construir_prompt(prompt_escena: str, identity_lock: str = "estricto",
                     dejar_espacio: bool = True, hay_relleno_gris: bool = False) -> str:
    partes = [prompt_escena.strip()]

    if identity_lock == "estricto":
        partes.append(IDENTITY_LOCK)
        partes.append(REFUERZO_ESCENA)
    elif identity_lock == "moderado":
        partes.append(LOCK_MODERADO)

    if hay_relleno_gris:
        partes.append(
            "The flat grey filler areas at the edges of the frame are empty canvas and must be "
            "filled in with the new scene so that no grey remains. "
        )
    if dejar_espacio:
        partes.append(ESPACIO_TEXTO)
    if identity_lock in ("estricto", "moderado"):
        partes.append(INTEGRACION)

    return " ".join(p.strip() for p in partes if p.strip())


def escena(src: str | Path, dest: str | Path, perfil: dict,
           nombre_escena: str | None = None,
           brief: str = "",
           modelo: str = kie.MODEL_PRO,
           resolucion: str = "2K",
           ratio: str = "4:5",
           identity_lock: str | None = None,
           dejar_espacio: bool = True,
           hay_relleno_gris: bool = False) -> Path:
    """Genera una escena publicitaria alrededor del sujeto."""
    if brief:
        nombre, prompt_escena = "brief", brief
    else:
        nombre, prompt_escena = profiles.escena(perfil, nombre_escena)

    nivel = identity_lock or perfil["identity_lock"]
    prompt = construir_prompt(prompt_escena, nivel, dejar_espacio, hay_relleno_gris)

    print(f"  escena '{nombre}', identity_lock={nivel}, modelo={modelo}")

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

    return kie.run(modelo, entrada, dest, label="escena")


def _cli() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Escenas generadas para campana")
    p.add_argument("src")
    p.add_argument("-o", "--out")
    p.add_argument("-p", "--perfil", default="barberia")
    p.add_argument("-e", "--escena", help="Nombre de la escena dentro del perfil")
    p.add_argument("-b", "--brief", default="",
                   help="Descripcion libre de la escena; sustituye a --escena")
    p.add_argument("-m", "--modelo", default=kie.MODEL_PRO,
                   choices=(kie.MODEL_PRO, kie.MODEL_EDIT))
    p.add_argument("--resolucion", default="2K", choices=("1K", "2K", "4K"))
    p.add_argument("-r", "--ratio", default="4:5")
    p.add_argument("--identity-lock", choices=profiles.NIVELES_IDENTITY)
    p.add_argument("--sin-espacio-texto", action="store_true")
    p.add_argument("--relleno-gris", action="store_true")
    p.add_argument("--dry-run", action="store_true")

    a = p.parse_args()
    src = Path(a.src)
    perfil = profiles.load(a.perfil)

    if a.dry_run:
        if a.brief:
            nombre, prompt_escena = "brief", a.brief
        else:
            nombre, prompt_escena = profiles.escena(perfil, a.escena)
        nivel = a.identity_lock or perfil["identity_lock"]
        print(f"--- escena '{nombre}', identity_lock={nivel} ---")
        print(construir_prompt(prompt_escena, nivel,
                               not a.sin_espacio_texto, a.relleno_gris))
        return

    dest = Path(a.out) if a.out else src.parent / f"{src.stem.split('__')[0]}__02-escena.png"
    escena(src, dest, perfil,
           nombre_escena=a.escena, brief=a.brief,
           modelo=a.modelo, resolucion=a.resolucion, ratio=a.ratio,
           identity_lock=a.identity_lock,
           dejar_espacio=not a.sin_espacio_texto,
           hay_relleno_gris=a.relleno_gris)
    print(f"  guardado {dest}")


if __name__ == "__main__":
    _cli()
