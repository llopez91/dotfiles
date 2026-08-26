"""Etapa 1: correcciones deterministas de geometria y tono.

Todo lo que se puede resolver con pixeles se resuelve aqui, antes de gastar un
solo credito de IA. Es exacto, gratis, instantaneo y no puede alterar la
identidad del sujeto.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

# Permite invocar el script por ruta absoluta desde cualquier carpeta.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

import imagenes

GRIS_RELLENO = (128, 128, 128)

# Valores validados sobre la foto de referencia (ver spec, seccion 9).
FILL_POR_DEFECTO = 0.52       # fraccion del alto que ocupa el sujeto
HEADROOM_POR_DEFECTO = 0.15   # aire sobre la cabeza, fraccion del alto


# --------------------------------------------------------------------------
# Tono
# --------------------------------------------------------------------------
def gray_world(im: Image.Image, strength: float = 0.6) -> tuple[Image.Image, tuple]:
    """Corrige la dominante de color con gray-world atenuado.

    A fuerza 1.0 el metodo desatura la piel; 0.6 quita el tinte de interior
    sin lavar los tonos de piel.
    """
    a = np.asarray(im).astype(np.float32)
    medias = a.reshape(-1, 3).mean(axis=0)
    objetivo = medias.mean()
    ganancias = objetivo / np.clip(medias, 1e-6, None)
    ganancias = 1.0 + (ganancias - 1.0) * strength
    a = np.clip(a * ganancias, 0, 255)
    return Image.fromarray(a.astype(np.uint8)), tuple(np.round(ganancias, 3))


def curva_sombras(gamma: float = 1.30, umbral_altas: float = 0.65) -> list[int]:
    """LUT que levanta sombras sin quemar las altas luces.

    Por encima de `umbral_altas` la curva se mezcla hacia la identidad, para
    que la piel iluminada no se vaya a blanco.
    """
    x = np.arange(256, dtype=np.float32) / 255.0
    lut = np.power(x, 1.0 / gamma)
    peso = np.clip((x - umbral_altas) / (1.0 - umbral_altas), 0, 1)
    lut = lut * (1 - peso) + x * peso
    return np.clip(lut * 255, 0, 255).astype(np.uint8).tolist()


def lift_shadows(im: Image.Image, gamma: float = 1.30) -> Image.Image:
    return im.point(curva_sombras(gamma) * 3)


def aplicar_look(im: Image.Image, look: dict, verbose: bool = True) -> Image.Image:
    """Aplica el bloque `look` de un perfil de rubro."""
    im, ganancias = gray_world(im, look["wb_strength"])
    if verbose:
        print(f"  balance de blancos R,G,B = {ganancias}")
    im = lift_shadows(im, look["gamma_sombras"])
    im = ImageEnhance.Contrast(im).enhance(look["contraste"])
    im = ImageEnhance.Color(im).enhance(look["saturacion"])
    im = ImageEnhance.Brightness(im).enhance(look["brillo"])
    return im


# --------------------------------------------------------------------------
# Geometria
# --------------------------------------------------------------------------
def mapear_punto(x: float, y: float, angulo: float,
                 tam_origen: tuple[int, int], tam_destino: tuple[int, int]) -> tuple[float, float]:
    """Mapea un punto de la imagen original a la rotada con expand=True.

    PIL rota en sentido antihorario para angulos positivos.
    """
    a = math.radians(angulo)
    cx, cy = tam_origen[0] / 2, tam_origen[1] / 2
    nx, ny = tam_destino[0] / 2, tam_destino[1] / 2
    dx, dy = x - cx, y - cy
    return (nx + dx * math.cos(a) + dy * math.sin(a),
            ny - dx * math.sin(a) + dy * math.cos(a))


def enderezar(im: Image.Image, angulo: float, relleno: str = "gris") -> Image.Image:
    """Rota la imagen. `relleno` decide que pasa con las esquinas vacias.

    gris  -> gris plano, pensado para que la IA lo reemplace despues
    blur  -> version desenfocada de la propia foto, para uso sin IA
    """
    if abs(angulo) < 0.01:
        return im

    rot = im.rotate(angulo, resample=Image.BICUBIC, expand=True, fillcolor=GRIS_RELLENO)
    if relleno != "blur":
        return rot

    # Fondo: la foto ampliada y muy desenfocada, para que las esquinas no canten.
    escala = max(rot.width / im.width, rot.height / im.height) * 1.35
    fondo = im.resize((int(im.width * escala), int(im.height * escala)), Image.LANCZOS)
    fondo = fondo.filter(ImageFilter.GaussianBlur(radius=max(rot.size) // 25))
    izq = (fondo.width - rot.width) // 2
    arr = (fondo.height - rot.height) // 2
    fondo = fondo.crop((izq, arr, izq + rot.width, arr + rot.height))

    # Mascara: donde la rotacion dejo contenido real.
    mascara = Image.new("L", im.size, 255).rotate(
        angulo, resample=Image.BICUBIC, expand=True, fillcolor=0
    )
    fondo.paste(rot, (0, 0), mascara)
    return fondo


def encuadrar(im: Image.Image, ratio: tuple[int, int] = (4, 5),
              sujeto: tuple[float, float, float, float] | None = None,
              fill: float = FILL_POR_DEFECTO,
              headroom: float = HEADROOM_POR_DEFECTO) -> tuple[Image.Image, tuple]:
    """Recorta al ratio pedido componiendo alrededor del sujeto.

    `sujeto` es (x0, y0, x1, y1) en coordenadas de ESTA imagen. Si se omite,
    recorta centrado.
    """
    W, H = im.size

    if sujeto is None:
        alto = H
        ancho = int(alto * ratio[0] / ratio[1])
        if ancho > W:
            ancho = W
            alto = int(ancho * ratio[1] / ratio[0])
        izq = (W - ancho) // 2
        arr = (H - alto) // 2
    else:
        x0, y0, x1, y1 = sujeto
        alto_sujeto = max(1.0, y1 - y0)
        alto = int(alto_sujeto / fill)
        ancho = int(alto * ratio[0] / ratio[1])

        # No pedir mas lienzo del que hay.
        if ancho > W:
            ancho = W
            alto = int(ancho * ratio[1] / ratio[0])
        if alto > H:
            alto = H
            ancho = int(alto * ratio[0] / ratio[1])

        centro_x = (x0 + x1) / 2
        izq = int(centro_x - ancho / 2)
        arr = int(y0 - headroom * alto)

    izq = max(0, min(W - ancho, izq))
    arr = max(0, min(H - alto, arr))
    caja = (izq, arr, izq + ancho, arr + alto)
    return im.crop(caja), caja


# --------------------------------------------------------------------------
# Ayuda para elegir el angulo
# --------------------------------------------------------------------------
def hoja_de_contacto(src: str | Path, dest: str | Path,
                     angulos: list[float] | None = None) -> Path:
    """Genera una hoja con varios angulos, para elegir mirandola.

    El angulo correcto no sale de una formula: sale de ver cual deja la cabeza
    natural. Esta hoja existe para tomar esa decision.
    """
    angulos = angulos or [0, 15, 25, 35, 45, 55]
    im = imagenes.abrir(src)

    miniaturas = []
    for a in angulos:
        r = im.rotate(a, resample=Image.BICUBIC, expand=True, fillcolor=(40, 40, 40))
        r.thumbnail((380, 380), Image.LANCZOS)
        miniaturas.append((a, r))

    cols = 3
    filas = math.ceil(len(miniaturas) / cols)
    cw, ch = 400, 420
    hoja = Image.new("RGB", (cols * cw, filas * ch), (20, 20, 20))
    d = ImageDraw.Draw(hoja)
    for i, (a, t) in enumerate(miniaturas):
        x = (i % cols) * cw + (cw - t.width) // 2
        y = (i // cols) * ch + 30
        hoja.paste(t, (x, y))
        d.text(((i % cols) * cw + 12, (i // cols) * ch + 10), f"{a} grados", fill=(255, 210, 0))

    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    hoja.save(dest)
    return dest


# --------------------------------------------------------------------------
# Pipeline de la etapa
# --------------------------------------------------------------------------
def enderezar_a_disco(src: str | Path, dest: str | Path, look: dict,
                      angulo: float, relleno: str = "gris") -> Path:
    """Tono + enderezado, sin recortar.

    Existe para el caso de fotos muy inclinadas: la caja del sujeto se lee
    sobre ESTA imagen, no sobre el original. Ver la nota de `prep`.
    """
    im = imagenes.abrir(src)
    rot = enderezar(aplicar_look(im, look), angulo, relleno)
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    rot.save(dest)
    print(f"  enderezada {angulo} grados -> {rot.size[0]}x{rot.size[1]}")
    print(f"  guardada {dest}")
    print("  Lee la caja del sujeto SOBRE ESTA IMAGEN y pasala con")
    print("  --sujeto x0,y0,x1,y1 --sujeto-espacio enderezada")
    return dest


def prep(src: str | Path, dest: str | Path, look: dict,
         angulo: float = 0.0,
         sujeto: tuple[float, float, float, float] | None = None,
         sujeto_espacio: str = "original",
         ratio: tuple[int, int] = (4, 5),
         salida: tuple[int, int] | None = (1080, 1350),
         relleno: str = "gris",
         fill: float = FILL_POR_DEFECTO,
         headroom: float = HEADROOM_POR_DEFECTO
         ) -> tuple[Path, tuple[float, float, float, float] | None]:
    """Tono + enderezado + encuadre.

    Devuelve (ruta, caja del sujeto en coordenadas de la imagen de salida).

    `sujeto_espacio` decide como se interpreta `sujeto`:

    - "original"   -> coordenadas de la foto de entrada. Se mapean rotando las
                      cuatro esquinas. Correcto solo si el angulo es pequeno:
                      con inclinaciones fuertes el rectangulo alineado a los
                      ejes se hincha al rotar y el encuadre sale inservible.
    - "enderezada" -> coordenadas de la imagen YA enderezada. Es lo correcto
                      cuando el angulo es grande. Usa `enderezar_a_disco` para
                      generarla y leer ahi la caja.

    Con angulo 0 los dos espacios son el mismo.
    """
    if sujeto_espacio not in ("original", "enderezada"):
        raise ValueError("sujeto_espacio debe ser 'original' o 'enderezada'")

    im = imagenes.abrir(src)
    print(f"  original {im.size[0]}x{im.size[1]}")

    im_tono = aplicar_look(im, look)

    rot = enderezar(im_tono, angulo, relleno)
    if angulo:
        print(f"  enderezada {angulo} grados -> {rot.size[0]}x{rot.size[1]} (relleno {relleno})")

    sujeto_rot = None
    if sujeto is not None:
        if sujeto_espacio == "enderezada" or not angulo:
            sujeto_rot = sujeto
        else:
            x0, y0, x1, y1 = sujeto
            esquinas = [mapear_punto(x, y, angulo, im.size, rot.size)
                        for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
            xs = [p[0] for p in esquinas]
            ys = [p[1] for p in esquinas]
            sujeto_rot = (min(xs), min(ys), max(xs), max(ys))
            if abs(angulo) > 12:
                print(f"  aviso: con {angulo} grados la caja dada en coordenadas del "
                      f"original se ensancha al rotar.")
                print("         Para un encuadre ajustado usa --sujeto-espacio enderezada.")

    recorte, caja = encuadrar(rot, ratio, sujeto_rot, fill, headroom)
    print(f"  encuadre {ratio[0]}:{ratio[1]} en {caja} -> {recorte.size[0]}x{recorte.size[1]}")

    # La caja del sujeto, ahora en coordenadas del recorte.
    sujeto_salida = None
    if sujeto_rot is not None:
        sx0, sy0, sx1, sy1 = sujeto_rot
        sujeto_salida = (sx0 - caja[0], sy0 - caja[1], sx1 - caja[0], sy1 - caja[1])

    if salida:
        fx = salida[0] / recorte.width
        fy = salida[1] / recorte.height
        recorte = recorte.resize(salida, Image.LANCZOS)
        if sujeto_salida:
            sujeto_salida = (sujeto_salida[0] * fx, sujeto_salida[1] * fy,
                             sujeto_salida[2] * fx, sujeto_salida[3] * fy)

    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    recorte.save(dest)
    print(f"  guardado {dest}")
    return dest, sujeto_salida


def _parse_caja(txt: str) -> tuple[float, float, float, float]:
    partes = [float(p) for p in txt.replace(" ", "").split(",")]
    if len(partes) != 4:
        raise ValueError("El sujeto se indica como x0,y0,x1,y1")
    return tuple(partes)  # type: ignore[return-value]


def _cli() -> None:
    import argparse
    import profiles

    p = argparse.ArgumentParser(description="Etapa 1: geometria y tono deterministas")
    p.add_argument("src")
    p.add_argument("-o", "--out", help="Ruta de salida")
    p.add_argument("-p", "--perfil", default="barberia")
    p.add_argument("-a", "--angulo", type=float, default=0.0,
                   help="Grados de enderezado (antihorario)")
    p.add_argument("-s", "--sujeto", help="Caja del sujeto x0,y0,x1,y1")
    p.add_argument("--sujeto-espacio", choices=("original", "enderezada"), default="original",
                   help="En que imagen se leyo la caja. Con angulos > 12 grados usa 'enderezada'")
    p.add_argument("-r", "--ratio", default="4:5")
    p.add_argument("--relleno", choices=("gris", "blur"), default="gris",
                   help="gris si despues pasa por IA, blur si es la salida final")
    p.add_argument("--fill", type=float, default=FILL_POR_DEFECTO)
    p.add_argument("--headroom", type=float, default=HEADROOM_POR_DEFECTO)
    p.add_argument("--contact-sheet", action="store_true",
                   help="Solo generar la hoja de angulos y salir")
    p.add_argument("--angulos", default="0,15,25,35,45,55")
    p.add_argument("--solo-enderezar", action="store_true",
                   help="Enderezar sin recortar, para leer ahi la caja del sujeto")

    a = p.parse_args()
    src = Path(a.src)
    out_dir = src.parent / "out"

    if a.contact_sheet:
        dest = hoja_de_contacto(
            src, out_dir / f"{src.stem}__angulos.png",
            [float(x) for x in a.angulos.split(",")],
        )
        print(f"Hoja de contacto: {dest}")
        print("Mirala y elige el angulo que deje al sujeto natural.")
        return

    perfil = profiles.load(a.perfil)

    if a.solo_enderezar:
        enderezar_a_disco(src, out_dir / f"{src.stem}__00-enderezada.png",
                          perfil["look"], a.angulo, a.relleno)
        return

    rw, rh = (int(x) for x in a.ratio.split(":"))
    dest = Path(a.out) if a.out else out_dir / f"{src.stem}__01-prep.png"

    prep(src, dest, perfil["look"],
         angulo=a.angulo,
         sujeto=_parse_caja(a.sujeto) if a.sujeto else None,
         sujeto_espacio=a.sujeto_espacio,
         ratio=(rw, rh),
         relleno=a.relleno,
         fill=a.fill,
         headroom=a.headroom)


if __name__ == "__main__":
    _cli()
