"""Composicion publicitaria: titular, subtitulo, CTA, logo y contacto.

El texto se compone localmente y no con IA, a proposito: la tipografia sale
nitida, alineada y con el texto exactamente escrito, sin las deformaciones que
los modelos de imagen siguen produciendo en letras pequenas.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import imagenes

FUENTES_DIR = Path("C:/Windows/Fonts")

# En orden de preferencia. La primera que exista gana.
FUENTES_TITULAR = ["seguibl.ttf", "impact.ttf", "arialbd.ttf", "segoeuib.ttf", "DejaVuSans-Bold.ttf"]
FUENTES_TEXTO = ["segoeui.ttf", "arial.ttf", "DejaVuSans.ttf"]
FUENTES_TEXTO_BOLD = ["segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"]

POSICIONES = ("abajo", "arriba", "izquierda", "derecha")


def _buscar_fuente(candidatas: list[str], tam: int) -> ImageFont.FreeTypeFont:
    for nombre in candidatas:
        ruta = FUENTES_DIR / nombre
        if ruta.exists():
            try:
                return ImageFont.truetype(str(ruta), tam)
            except OSError:
                continue
        try:
            return ImageFont.truetype(nombre, tam)
        except OSError:
            continue
    return ImageFont.load_default(size=tam)


def _ancho(d: ImageDraw.ImageDraw, txt: str, f: ImageFont.FreeTypeFont) -> int:
    caja = d.textbbox((0, 0), txt, font=f)
    return caja[2] - caja[0]


# Separadores que nunca deben quedar solos al principio de una linea.
SEPARADORES = {"·", "-", "|", "/", "•", "–", "—", "y", "e", "o", "u", "de", "en", "a"}


def _sin_huerfanos(lineas: list[str]) -> list[str]:
    """Sube al renglon anterior los separadores y palabras cortas huerfanas.

    `textwrap` trata el punto medio como una palabra mas y lo deja empezando
    linea, que se lee como una errata.
    """
    salida: list[str] = []
    for linea in lineas:
        partes = linea.split(" ", 1)
        if salida and partes[0].lower() in SEPARADORES:
            salida[-1] += " " + partes[0]
            resto = partes[1] if len(partes) > 1 else ""
            if resto:
                salida.append(resto)
        else:
            salida.append(linea)
    return salida


def _envolver(d: ImageDraw.ImageDraw, texto: str, f: ImageFont.FreeTypeFont,
              ancho_max: int) -> list[str]:
    """Parte el texto midiendo pixeles de verdad, palabra a palabra.

    Estimar el ancho medio a partir de la 'M' parte antes de tiempo: la M es la
    letra mas ancha del alfabeto, asi que el calculo sobra siempre y un titular
    que cabia de sobra acababa en dos lineas.
    """
    palabras = texto.split()
    if not palabras:
        return [texto]

    lineas: list[str] = []
    actual = ""
    for palabra in palabras:
        prueba = f"{actual} {palabra}".strip()
        if not actual or _ancho(d, prueba, f) <= ancho_max:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def _ajustar(d: ImageDraw.ImageDraw, texto: str, candidatas: list[str],
             ancho_max: int, tam_inicial: int, lineas_max: int = 3
             ) -> tuple[list[str], ImageFont.FreeTypeFont]:
    """Reduce el cuerpo hasta que el texto quepa en `lineas_max` lineas."""
    tam = tam_inicial
    while tam > 12:
        f = _buscar_fuente(candidatas, tam)
        lineas = _sin_huerfanos(_envolver(d, texto, f, ancho_max))
        if len(lineas) <= lineas_max and all(_ancho(d, l, f) <= ancho_max for l in lineas):
            return lineas, f
        tam = int(tam * 0.92)

    # Suelo: una palabra sola mas ancha que la columna. Se deja que sobresalga
    # antes que reducirla hasta lo ilegible.
    f = _buscar_fuente(candidatas, 12)
    return _sin_huerfanos(_envolver(d, texto, f, ancho_max)), f


def _scrim(im: Image.Image, posicion: str, fuerza: float = 0.78,
           extension: float = 0.46) -> Image.Image:
    """Oscurece progresivamente la zona del texto para que se lea siempre."""
    W, H = im.size
    a = np.asarray(im.convert("RGB")).astype(np.float32)

    # La rampa va de 1.0 (sin tocar) a 1.0-fuerza (lo mas oscuro). El extremo
    # oscuro tiene que caer en el borde donde va el texto, no en el interior.
    if posicion in ("abajo", "arriba"):
        largo = max(1, int(H * extension))
        rampa = np.linspace(1.0, 1.0 - fuerza, largo, dtype=np.float32)
        mult = np.ones(H, dtype=np.float32)
        if posicion == "abajo":
            mult[H - largo:] = rampa          # oscurece hacia el borde inferior
        else:
            mult[:largo] = rampa[::-1]        # oscurece hacia el borde superior
        a *= mult.reshape(H, 1, 1)
    else:
        largo = max(1, int(W * extension))
        rampa = np.linspace(1.0, 1.0 - fuerza, largo, dtype=np.float32)
        mult = np.ones(W, dtype=np.float32)
        if posicion == "izquierda":
            mult[:largo] = rampa[::-1]        # oscurece hacia el borde izquierdo
        else:
            mult[W - largo:] = rampa          # oscurece hacia el borde derecho
        a *= mult.reshape(1, W, 1)

    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def _pastilla(d: ImageDraw.ImageDraw, xy: tuple[int, int], texto: str,
              f: ImageFont.FreeTypeFont, color_fondo: str, color_texto: str,
              pad_x: int, pad_y: int) -> tuple[int, int]:
    """Dibuja el CTA como pastilla redondeada. Devuelve su tamano."""
    caja = d.textbbox((0, 0), texto, font=f)
    tw, th = caja[2] - caja[0], caja[3] - caja[1]
    w, h = tw + pad_x * 2, th + pad_y * 2
    x, y = xy
    d.rounded_rectangle((x, y, x + w, y + h), radius=h // 2, fill=color_fondo)
    d.text((x + pad_x - caja[0], y + pad_y - caja[1]), texto, font=f, fill=color_texto)
    return w, h


def componer(src: str | Path, dest: str | Path,
             titular: str = "", subtitulo: str = "", cta: str = "",
             contacto: str = "", logo: str | Path | None = None,
             posicion: str = "abajo",
             color_acento: str = "#E8B23A",
             color_texto: str = "#FFFFFF",
             color_titular: str | None = None,
             color_cta_texto: str = "#101010",
             scrim: float = 0.78,
             margen: float = 0.07) -> Path:
    """Compone la pieza publicitaria sobre una imagen ya editada."""
    if posicion not in POSICIONES:
        raise ValueError(f"posicion debe ser una de {POSICIONES}")

    im = imagenes.abrir(src)
    W, H = im.size

    if scrim > 0 and (titular or subtitulo or cta or contacto):
        im = _scrim(im, posicion, scrim)

    d = ImageDraw.Draw(im)
    m = int(min(W, H) * margen)

    if posicion in ("izquierda", "derecha"):
        ancho_col = int(W * 0.44)
        x0 = m if posicion == "izquierda" else W - ancho_col - m
    else:
        ancho_col = W - m * 2
        x0 = m

    base = min(W, H)
    bloques: list[tuple[list[str], ImageFont.FreeTypeFont, int, str]] = []

    if titular:
        lineas, f = _ajustar(d, titular.upper(), FUENTES_TITULAR,
                             ancho_col, int(base * 0.115), lineas_max=3)
        bloques.append((lineas, f, int(f.size * 1.06), color_titular or color_texto))
    if subtitulo:
        lineas, f = _ajustar(d, subtitulo, FUENTES_TEXTO, ancho_col,
                             int(base * 0.045), lineas_max=3)
        bloques.append((lineas, f, int(f.size * 1.34), color_texto))

    alto_texto = sum(len(l) * lh for l, _, lh, _ in bloques)
    if bloques:
        alto_texto += int(base * 0.022) * (len(bloques) - 1)

    f_cta = _buscar_fuente(FUENTES_TEXTO_BOLD, int(base * 0.042))
    alto_cta = int(base * 0.042 * 2.5) + int(base * 0.03) if cta else 0

    f_contacto = _buscar_fuente(FUENTES_TEXTO, int(base * 0.032))
    alto_contacto = int(base * 0.055) if contacto else 0

    total = alto_texto + alto_cta + alto_contacto

    if posicion == "abajo":
        y = H - m - total
    elif posicion == "arriba":
        y = m
    else:
        y = (H - total) // 2

    # Titular y subtitulo, con sombra suave para separarlos del fondo.
    for lineas, f, lh, color in bloques:
        for linea in lineas:
            d.text((x0 + 2, y + 2), linea, font=f, fill=(0, 0, 0))
            d.text((x0, y), linea, font=f, fill=color)
            y += lh
        y += int(base * 0.022)

    if cta:
        _, h = _pastilla(d, (x0, y), cta.upper(), f_cta,
                         color_acento, color_cta_texto,
                         int(base * 0.035), int(base * 0.020))
        y += h + int(base * 0.03)

    if contacto:
        d.text((x0 + 1, y + 1), contacto, font=f_contacto, fill=(0, 0, 0))
        d.text((x0, y), contacto, font=f_contacto, fill=color_texto)

    if logo:
        ruta_logo = Path(logo)
        if not ruta_logo.exists():
            raise FileNotFoundError(f"No existe el logo: {ruta_logo}")
        lg = Image.open(imagenes.ruta_legible(ruta_logo)).convert("RGBA")
        alto_logo = int(base * 0.10)
        lg = lg.resize(
            (max(1, int(lg.width * alto_logo / lg.height)), alto_logo), Image.LANCZOS
        )
        esquina = (m, m) if posicion != "arriba" else (m, H - m - lg.height)
        im.paste(lg, esquina, lg)

    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest)
    return dest


def _cli() -> None:
    import argparse

    import marca

    p = argparse.ArgumentParser(description="Composicion de arte publicitario")
    p.add_argument("src")
    p.add_argument("-o", "--out")
    p.add_argument("-t", "--titular", default="")
    p.add_argument("-s", "--subtitulo", default="")
    p.add_argument("-c", "--cta", default="")
    p.add_argument("--contacto", default="")
    p.add_argument("--logo")
    p.add_argument("--posicion", choices=POSICIONES, default="abajo")
    p.add_argument("--acento", default="#E8B23A", help="Color del CTA y de la marca")
    p.add_argument("--color-titular", help="Por defecto, el mismo que el texto")
    p.add_argument("--color-texto", default="#FFFFFF")
    p.add_argument("--color-cta-texto", default="#101010")
    p.add_argument("--scrim", type=float, default=0.78)
    p.add_argument("--margen", type=float, default=0.07,
                   help="Margen relativo. Sube a 0.20 en story: abajo la tapa la UI de Instagram")
    p.add_argument("--marca", help="Id o carpeta del cliente. Por defecto se detecta sola")
    p.add_argument("--sin-marca", action="store_true",
                   help="Ignorar la marca aunque haya una cerca")

    a = p.parse_args()
    src = Path(a.src)

    # La marca rellena lo que no se haya pasado a mano: los flags siempre ganan.
    m = None if a.sin_marca else marca.cargar(a.marca, junto_a=src)
    logo_final, contacto_final = a.logo, a.contacto
    acento = a.acento
    color_titular, color_texto, color_cta_texto = a.color_titular, a.color_texto, a.color_cta_texto

    if m:
        c = marca.colores(m)
        print(f"  marca '{m['nombre']}' ({m['_archivo']})")
        if acento == "#E8B23A":
            acento = c["acento"]
        if color_titular is None:
            color_titular = c.get("titular")
        if color_texto == "#FFFFFF":
            color_texto = c["texto"]
        if color_cta_texto == "#101010":
            color_cta_texto = c["cta_texto"]
        if not logo_final:
            ruta = marca.logo(m)
            logo_final = str(ruta) if ruta else None
        if not contacto_final:
            contacto_final = marca.linea_contacto(m)

        for pendiente in marca.datos_pendientes(m):
            print(f"  PENDIENTE: {pendiente}")

    dest = Path(a.out) if a.out else src.parent / f"{src.stem}__arte.png"
    salida = componer(src, dest, a.titular, a.subtitulo, a.cta, contacto_final,
                      logo_final, a.posicion, acento,
                      color_texto=color_texto,
                      color_titular=color_titular,
                      color_cta_texto=color_cta_texto,
                      scrim=a.scrim, margen=a.margen)
    print(f"  guardado {salida}")


if __name__ == "__main__":
    _cli()
