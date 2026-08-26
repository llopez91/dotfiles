"""Apertura de imagenes tolerante al formato.

Las fotos de iPhone llegan en HEIC, y a menudo con extension .png o .jpg que
miente. Pillow no lo decodifica sin pillow-heif. Aqui se detecta por la
cabecera real (no por la extension) y se convierte con ffmpeg.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

# Marcas ISO-BMFF que Pillow no abre por si solo.
MARCAS_ISOBMFF = {b"heic", b"heix", b"hevc", b"hevx", b"mif1", b"msf1",
                  b"heim", b"heis", b"avif", b"avis"}

_TEMPORALES: list[Path] = []


def es_isobmff(ruta: Path) -> bool:
    """Detecta HEIC/AVIF por la cabecera, ignorando la extension."""
    try:
        with open(ruta, "rb") as f:
            cab = f.read(12)
    except OSError:
        return False
    return len(cab) >= 12 and cab[4:8] == b"ftyp" and cab[8:12] in MARCAS_ISOBMFF


def _convertir(ruta: Path) -> Path:
    """Convierte a PNG con ffmpeg. El temporal se limpia al salir."""
    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            f"{ruta.name} es HEIC/AVIF y hace falta ffmpeg para leerlo.\n"
            "Instalalo con:  winget install Gyan.FFmpeg\n"
            "O convierte la foto a JPG antes de pasarla."
        )
    destino = Path(tempfile.mkdtemp(prefix="studio-creative-")) / f"{ruta.stem}.png"
    r = subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(ruta), str(destino)],
        capture_output=True, text=True,
    )
    if r.returncode != 0 or not destino.exists():
        raise RuntimeError(f"ffmpeg no pudo convertir {ruta.name}: {r.stderr.strip()[:300]}")
    _TEMPORALES.append(destino)
    print(f"  convertida desde HEIC/AVIF: {ruta.name}")
    return destino


def ruta_legible(ruta: str | Path) -> Path:
    """Devuelve una ruta que Pillow sepa abrir, convirtiendo si hace falta."""
    ruta = Path(ruta)
    if not ruta.exists():
        raise FileNotFoundError(f"No existe la imagen: {ruta}")
    return _convertir(ruta) if es_isobmff(ruta) else ruta


def abrir(ruta: str | Path) -> Image.Image:
    """Abre cualquier imagen como RGB, incluidas las HEIC de iPhone."""
    return Image.open(ruta_legible(ruta)).convert("RGB")


if __name__ == "__main__":
    import sys

    for arg in sys.argv[1:]:
        p = Path(arg)
        print(f"{p.name}: isobmff={es_isobmff(p)}", end="")
        try:
            im = abrir(p)
            print(f"  -> {im.size} {im.mode}")
        except Exception as e:
            print(f"  -> ERROR: {e}")
