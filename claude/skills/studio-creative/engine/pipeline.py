"""Pipeline completo: prep -> IA -> finish, en un solo comando.

Las etapas intermedias se conservan en disco. Si el render de IA sale mal se
reintenta desde el prep sin repetir el trabajo determinista ni gastar de mas.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Permite invocar el script por ruta absoluta desde cualquier carpeta.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import finish
import kie
import marca
import prep
import profiles
import relight
import scene as scene_mod


def _caja_maestro(maestro: Path, sujeto_prep: tuple | None,
                  tam_prep: tuple[int, int]) -> tuple | None:
    """Reescala la caja del sujeto del prep a las dimensiones del render."""
    if sujeto_prep is None:
        return None
    from PIL import Image

    with Image.open(maestro) as m:
        fx = m.width / tam_prep[0]
        fy = m.height / tam_prep[1]
    x0, y0, x1, y1 = sujeto_prep
    return (x0 * fx, y0 * fy, x1 * fx, y1 * fy)


def ejecutar(src: str | Path, perfil_id: str | None = None,
             angulo: float = 0.0,
             sujeto: tuple[float, float, float, float] | None = None,
             sujeto_espacio: str = "original",
             fondo: str | None = None,
             escena: str | None = None,
             brief: str = "",
             modelo: str = kie.MODEL_PRO,
             resolucion: str = "2K",
             formatos: list[str] | None = None,
             ratio: str = "4:5",
             identity_lock: str | None = None,
             lado_wide: str = "derecha",
             sin_ia: bool = False,
             out_dir: str | Path | None = None,
             marca_ref: str | Path | None = None,
             sin_marca: bool = False) -> dict:
    """Corre el pipeline completo y devuelve las rutas de todo lo generado.

    Sin `perfil_id`, lo toma de la marca del cliente; sin marca, de barberia.
    """
    src = Path(src)

    m = None if sin_marca else marca.cargar(marca_ref, junto_a=src)
    if m:
        print(f"  marca '{m['nombre']}' ({m['_archivo']})")
        perfil = marca.perfil(m)
        perfil_id = perfil_id or m["perfil"]
    else:
        perfil_id = perfil_id or "barberia"
        perfil = profiles.load(perfil_id)

    # Con marca, la salida va a su carpeta out/ salvo que se pida otra cosa.
    if out_dir:
        out = Path(out_dir)
    elif m:
        out = marca.raiz(m) / "out"
    else:
        out = src.parent / "out"
    out.mkdir(parents=True, exist_ok=True)
    base = src.stem

    rw, rh = (int(x) for x in ratio.split(":"))
    salida_prep = (1080, int(1080 * rh / rw))

    generado: dict = {"perfil": perfil_id, "marca": m}

    # --- Etapa 1: determinista -------------------------------------------
    print("[1/3] prep (determinista, 0 creditos)")
    ruta_prep = out / f"{base}__01-prep.png"
    ruta_prep, sujeto_prep = prep.prep(
        src, ruta_prep, perfil["look"],
        angulo=angulo, sujeto=sujeto, sujeto_espacio=sujeto_espacio,
        ratio=(rw, rh), salida=salida_prep,
        relleno="gris" if not sin_ia else "blur",
    )
    generado["prep"] = ruta_prep

    # --- Etapa 2: IA ------------------------------------------------------
    if sin_ia:
        print("[2/3] IA omitida (--sin-ia)")
        maestro = ruta_prep
        generado["render"] = None
    else:
        saldo = kie.credits()
        costo = kie.COSTO.get(modelo, 0)
        if saldo < costo:
            raise kie.KieError(
                f"Saldo insuficiente: {saldo:.1f} creditos, hacen falta {costo}"
            )
        if saldo < 100:
            print(f"  aviso: quedan {saldo:.1f} creditos")

        print(f"[2/3] IA ({modelo}, ~{costo} creditos, saldo {saldo:.1f})")
        maestro = out / f"{base}__02-render.png"
        if escena or brief:
            scene_mod.escena(ruta_prep, maestro, perfil,
                             nombre_escena=escena, brief=brief,
                             modelo=modelo, resolucion=resolucion, ratio=ratio,
                             identity_lock=identity_lock, hay_relleno_gris=True)
        else:
            relight.relight(ruta_prep, maestro, perfil,
                            fondo=fondo, modelo=modelo, resolucion=resolucion,
                            ratio=ratio, hay_relleno_gris=True,
                            identity_lock=identity_lock)
        generado["render"] = maestro

    # --- Etapa 3: determinista -------------------------------------------
    print("[3/3] finish (determinista, 0 creditos)")
    formatos = formatos or perfil["formatos"]
    caja = _caja_maestro(Path(maestro), sujeto_prep, salida_prep)
    generado["formatos"] = finish.exportar(
        maestro, formatos, perfil["look"], out, caja, lado_wide, base=base
    )

    return generado


def _cli() -> None:
    import argparse

    p = argparse.ArgumentParser(
        description="Pipeline completo de edicion para redes: prep -> IA -> finish"
    )
    p.add_argument("src")
    p.add_argument("-p", "--perfil", help="Por defecto, el de la marca del cliente")
    p.add_argument("--marca", help="Id o carpeta del cliente. Por defecto se detecta sola")
    p.add_argument("--sin-marca", action="store_true")
    p.add_argument("-a", "--angulo", type=float, default=0.0)
    p.add_argument("-s", "--sujeto", help="Caja del sujeto x0,y0,x1,y1")
    p.add_argument("--sujeto-espacio", choices=("original", "enderezada"), default="original",
                   help="En que imagen se leyo la caja. Con angulos > 12 grados usa 'enderezada'")
    p.add_argument("-f", "--fondo")
    p.add_argument("-e", "--escena", help="Modo campana: usa una escena del perfil")
    p.add_argument("-b", "--brief", default="", help="Modo campana: descripcion libre")
    p.add_argument("-m", "--modelo", default=kie.MODEL_PRO,
                   choices=(kie.MODEL_PRO, kie.MODEL_EDIT))
    p.add_argument("--resolucion", default="2K", choices=("1K", "2K", "4K"))
    p.add_argument("-r", "--ratio", default="4:5")
    p.add_argument("--formatos", help="Coma-separados. Por defecto los del perfil")
    p.add_argument("--todos-formatos", action="store_true")
    p.add_argument("--identity-lock", choices=profiles.NIVELES_IDENTITY)
    p.add_argument("--lado-wide", choices=("derecha", "izquierda"), default="derecha")
    p.add_argument("--sin-ia", action="store_true",
                   help="Solo etapas deterministas: no gasta creditos")
    p.add_argument("-o", "--out-dir")

    a = p.parse_args()

    if a.todos_formatos:
        formatos = list(finish.FORMATOS)
    elif a.formatos:
        formatos = [x.strip() for x in a.formatos.split(",")]
    else:
        formatos = None

    sujeto = None
    if a.sujeto:
        sujeto = tuple(float(x) for x in a.sujeto.replace(" ", "").split(","))

    res = ejecutar(a.src, a.perfil, a.angulo, sujeto, a.sujeto_espacio,
                   a.fondo, a.escena, a.brief,
                   a.modelo, a.resolucion, formatos, a.ratio, a.identity_lock,
                   a.lado_wide, a.sin_ia, a.out_dir, a.marca, a.sin_marca)

    print("\nGenerado:")
    if res.get("prep"):
        print(f"  prep    {res['prep']}")
    if res.get("render"):
        print(f"  render  {res['render']}")
    for nombre, ruta in res["formatos"].items():
        print(f"  {nombre:9} {ruta}")


if __name__ == "__main__":
    _cli()
