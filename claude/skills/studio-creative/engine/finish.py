"""Etapa 3: grade final y export a los formatos de cada plataforma.

Todos los formatos salen de UN solo render maestro. Pedirle cada formato a la
IA costaria 4x y produciria versiones inconsistentes del mismo post.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Permite invocar el script por ruta absoluta desde cualquier carpeta.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

import imagenes

# (ancho, alto, como se deriva del maestro)
FORMATOS = {
    "ig-feed":   (1080, 1350, "recorte"),
    "ig-square": (1080, 1080, "recorte"),
    "story":     (1080, 1920, "recorte"),
    "wide":      (1920, 1080, "lienzo"),
}

USOS = {
    "ig-feed": "Feed de Instagram y Facebook",
    "ig-square": "Feed cuadrado, cuadricula del perfil",
    "story": "Story, Reel, TikTok, estado de WhatsApp",
    "wide": "Portada de Facebook, YouTube, web",
}


def enfocar(im: Image.Image, cantidad: float = 1.25) -> Image.Image:
    """Enfoque de salida. Se aplica al final, tras el reescalado."""
    if cantidad <= 1.0:
        return im
    porcentaje = int((cantidad - 1.0) * 100)
    return im.filter(ImageFilter.UnsharpMask(radius=1.6, percent=porcentaje, threshold=3))


def grade(im: Image.Image, look: dict) -> Image.Image:
    """Ajuste final ligero. El grueso del tono ya se hizo en la etapa 1."""
    im = ImageEnhance.Contrast(im).enhance(1.0 + (look["contraste"] - 1.0) * 0.4)
    im = ImageEnhance.Color(im).enhance(1.0 + (look["saturacion"] - 1.0) * 0.5)
    return im


def _recortar_a(im: Image.Image, ancho: int, alto: int,
                sujeto: tuple[float, float, float, float] | None) -> Image.Image:
    """Recorta al ratio destino manteniendo al sujeto dentro."""
    objetivo = ancho / alto
    W, H = im.size
    actual = W / H

    if actual > objetivo:
        nuevo_w = int(H * objetivo)
        if sujeto:
            centro = (sujeto[0] + sujeto[2]) / 2
            izq = int(centro - nuevo_w / 2)
        else:
            izq = (W - nuevo_w) // 2
        izq = max(0, min(W - nuevo_w, izq))
        caja = (izq, 0, izq + nuevo_w, H)
    else:
        nuevo_h = int(W / objetivo)
        if sujeto:
            # Sesgo hacia arriba: en un retrato lo prescindible esta abajo.
            arr = int(sujeto[1] - nuevo_h * 0.12)
        else:
            arr = (H - nuevo_h) // 2
        arr = max(0, min(H - nuevo_h, arr))
        caja = (0, arr, W, arr + nuevo_h)

    return im.crop(caja).resize((ancho, alto), Image.LANCZOS)


def _extender_lienzo(im: Image.Image, ancho: int, alto: int,
                     lado: str = "derecha") -> Image.Image:
    """Pasa un retrato a formato apaisado extendiendo el lienzo, no recortando.

    De 4:5 (0.80) a 16:9 (1.78) recortando habria que decapitar al sujeto. En
    su lugar se coloca el retrato a un lado y se rellena el resto con un
    degradado muestreado del propio fondo del render. El espacio negativo que
    queda es donde va el titular: el formato sale listo para publicidad.
    """
    escala = alto / im.height
    sujeto = im.resize((max(1, int(im.width * escala)), alto), Image.LANCZOS)

    # Muestrea columnas de los bordes del render para construir el degradado.
    a = np.asarray(im.convert("RGB")).astype(np.float32)
    margen = max(1, im.width // 12)
    col_izq = a[:, :margen, :].mean(axis=(0, 1))
    col_der = a[:, -margen:, :].mean(axis=(0, 1))

    filas = np.asarray(im.convert("RGB").resize((1, alto), Image.LANCZOS)).astype(np.float32)
    filas = filas.reshape(alto, 3)

    # Degradado vertical (del propio render) por horizontal (de borde a borde).
    t = np.linspace(0.0, 1.0, ancho, dtype=np.float32).reshape(1, ancho, 1)
    base_h = col_izq.reshape(1, 1, 3) * (1 - t) + col_der.reshape(1, 1, 3) * t
    base_v = filas.reshape(alto, 1, 3)
    lienzo_arr = np.clip(base_h * 0.55 + base_v * 0.45, 0, 255).astype(np.uint8)
    lienzo = Image.fromarray(lienzo_arr).filter(ImageFilter.GaussianBlur(radius=alto // 14))

    # Oscurece el lado LIBRE (el opuesto al sujeto): ahi va el titular y
    # necesita contraste. Con el sujeto a la derecha, el hueco es la izquierda.
    oscuro = np.linspace(0.68, 1.0, ancho, dtype=np.float32)
    if lado == "izquierda":
        oscuro = oscuro[::-1]
    arr = np.asarray(lienzo).astype(np.float32) * oscuro.reshape(1, ancho, 1)
    lienzo = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

    x = ancho - sujeto.width if lado == "derecha" else 0
    if sujeto.width >= ancho:
        # Cabe justo o de sobra: recorta al centro del sujeto.
        sujeto = sujeto.crop(((sujeto.width - ancho) // 2, 0,
                              (sujeto.width - ancho) // 2 + ancho, alto))
        x = 0

    # Pluma ancha en el borde interior: con una estrecha la costura canta.
    pluma = max(24, sujeto.width // 6)
    grad = np.ones((sujeto.height, sujeto.width), dtype=np.float32)
    rampa = np.linspace(0, 1, pluma, dtype=np.float32)
    if lado == "derecha":
        grad[:, :pluma] = rampa
    else:
        grad[:, -pluma:] = rampa[::-1]
    mascara = Image.fromarray((grad * 255).astype(np.uint8))

    lienzo.paste(sujeto, (x, 0), mascara)
    return lienzo


ANCLAS = ("arriba-derecha", "arriba-izquierda", "arriba-centro",
          "abajo-derecha", "abajo-izquierda", "abajo-centro")


def con_espacio(im: Image.Image, ancho: int, alto: int,
                escala: float = 0.78, ancla: str = "arriba-derecha",
                oscurecer: float = 0.55) -> Image.Image:
    """Coloca el sujeto en un lienzo mayor, dejando espacio limpio para el texto.

    Un render de retrato viene encuadrado cerca del sujeto: no hay hueco donde
    poner un titular sin taparle la cara. Recortar no lo resuelve, porque quita
    justo lo que el post quiere enseñar.

    Aqui el sujeto se escala y se ancla a una esquina, y el resto del lienzo se
    rellena con el propio fondo del render muy desenfocado, oscurecido. Como el
    fondo de estudio ya es un degradado suave, la extension es indistinguible.
    Y no toca un solo pixel del sujeto.
    """
    if ancla not in ANCLAS:
        raise ValueError(f"ancla debe ser una de {ANCLAS}")
    if not 0.2 <= escala <= 1.0:
        raise ValueError("escala debe estar entre 0.2 y 1.0")

    # Fondo: el propio render cubriendo el lienzo, muy desenfocado.
    escala_cover = max(ancho / im.width, alto / im.height)
    fondo = im.resize((max(1, int(im.width * escala_cover)),
                       max(1, int(im.height * escala_cover))), Image.LANCZOS)
    izq = (fondo.width - ancho) // 2
    arr = (fondo.height - alto) // 2
    fondo = fondo.crop((izq, arr, izq + ancho, arr + alto))
    fondo = fondo.filter(ImageFilter.GaussianBlur(radius=max(ancho, alto) // 9))

    a = np.asarray(fondo).astype(np.float32) * (1.0 - oscurecer)
    fondo = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

    # Sujeto escalado.
    nuevo_alto = max(1, int(alto * escala))
    nuevo_ancho = max(1, int(im.width * nuevo_alto / im.height))
    if nuevo_ancho > ancho:
        nuevo_ancho = ancho
        nuevo_alto = max(1, int(im.height * nuevo_ancho / im.width))
    sujeto = im.resize((nuevo_ancho, nuevo_alto), Image.LANCZOS)

    vert, horiz = ancla.split("-")
    y = 0 if vert == "arriba" else alto - nuevo_alto
    if horiz == "derecha":
        x = ancho - nuevo_ancho
    elif horiz == "izquierda":
        x = 0
    else:
        x = (ancho - nuevo_ancho) // 2

    # Pluma solo en los bordes que quedan por dentro del lienzo. Los que van
    # pegados a un borde del lienzo no se difuminan: alli no hay costura.
    grad = np.ones((nuevo_alto, nuevo_ancho), dtype=np.float32)
    pl_x = max(16, nuevo_ancho // 7)
    pl_y = max(16, nuevo_alto // 7)
    rampa_x = np.linspace(0, 1, pl_x, dtype=np.float32)
    rampa_y = np.linspace(0, 1, pl_y, dtype=np.float32).reshape(pl_y, 1)

    if x > 0:
        grad[:, :pl_x] = np.minimum(grad[:, :pl_x], rampa_x)
    if x + nuevo_ancho < ancho:
        grad[:, -pl_x:] = np.minimum(grad[:, -pl_x:], rampa_x[::-1])
    if y > 0:
        grad[:pl_y, :] = np.minimum(grad[:pl_y, :], rampa_y)
    if y + nuevo_alto < alto:
        grad[-pl_y:, :] = np.minimum(grad[-pl_y:, :], rampa_y[::-1])

    fondo.paste(sujeto, (x, y), Image.fromarray((grad * 255).astype(np.uint8)))
    return fondo


def exportar(src: str | Path, formatos: list[str], look: dict,
             out_dir: str | Path | None = None,
             sujeto: tuple[float, float, float, float] | None = None,
             lado_wide: str = "derecha",
             base: str | None = None,
             espacio_texto: str | None = None,
             escala_sujeto: float = 0.78) -> dict[str, Path]:
    """Genera todos los formatos pedidos desde el render maestro.

    `espacio_texto` es un ancla de `con_espacio`: reserva hueco limpio para el
    titular en vez de recortar. Se ignora en el formato `wide`, que ya lo hace
    por su cuenta.
    """
    src = Path(src)
    out_dir = Path(out_dir) if out_dir else src.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    base = base or src.stem.split("__")[0]

    maestro = imagenes.abrir(src)
    print(f"  maestro {maestro.size[0]}x{maestro.size[1]}")

    resultados: dict[str, Path] = {}
    for nombre in formatos:
        if nombre not in FORMATOS:
            raise ValueError(
                f"Formato desconocido '{nombre}'. Disponibles: {', '.join(FORMATOS)}"
            )
        ancho, alto, metodo = FORMATOS[nombre]

        if metodo == "lienzo":
            im = _extender_lienzo(maestro, ancho, alto, lado_wide)
        elif espacio_texto:
            im = con_espacio(maestro, ancho, alto, escala_sujeto, espacio_texto)
        else:
            im = _recortar_a(maestro, ancho, alto, sujeto)

        im = grade(im, look)
        im = enfocar(im, look["enfoque"])

        dest = out_dir / f"{base}__{nombre}.png"
        im.save(dest)
        resultados[nombre] = dest
        print(f"  {nombre:10} {ancho}x{alto}  {USOS[nombre]}")

    return resultados


def _cli() -> None:
    import argparse
    import profiles

    p = argparse.ArgumentParser(description="Etapa 3: grade final y packs por plataforma")
    p.add_argument("src", help="Render maestro")
    p.add_argument("-p", "--perfil", default="barberia")
    p.add_argument("-f", "--formatos", help="Coma-separados. Por defecto los del perfil")
    p.add_argument("-o", "--out-dir")
    p.add_argument("-s", "--sujeto", help="Caja del sujeto x0,y0,x1,y1 en el maestro")
    p.add_argument("--lado-wide", choices=("derecha", "izquierda"), default="derecha",
                   help="A que lado va el sujeto en el formato apaisado")
    p.add_argument("--todos", action="store_true", help="Exportar los cuatro formatos")
    p.add_argument("--espacio-texto", choices=ANCLAS,
                   help="Reserva hueco limpio para el titular en vez de recortar")
    p.add_argument("--escala-sujeto", type=float, default=0.78,
                   help="Cuanto del alto ocupa el sujeto al reservar espacio")

    a = p.parse_args()
    perfil = profiles.load(a.perfil)

    if a.todos:
        formatos = list(FORMATOS)
    elif a.formatos:
        formatos = [x.strip() for x in a.formatos.split(",")]
    else:
        formatos = perfil["formatos"]

    sujeto = None
    if a.sujeto:
        sujeto = tuple(float(x) for x in a.sujeto.replace(" ", "").split(","))

    exportar(a.src, formatos, perfil["look"], a.out_dir, sujeto, a.lado_wide,
             espacio_texto=a.espacio_texto, escala_sujeto=a.escala_sujeto)


if __name__ == "__main__":
    _cli()
