"""Identidad de marca por cliente.

La herramienta es global; lo que cambia entre trabajos son los datos del
cliente. Cada cliente vive en su carpeta con un `marca.json` que fija colores,
logo, contacto y perfil de rubro.

La resolucion es por cercania: se busca `marca.json` subiendo desde la propia
imagen. Asi basta apuntar a la foto y la marca sale sola, sin flags.
"""
from __future__ import annotations

import json
from pathlib import Path

import profiles

NOMBRE_ARCHIVO = "marca.json"
CARPETA_CLIENTES = "clientes"
NIVELES_BUSQUEDA = 6

COLORES_POR_DEFECTO = {
    "acento": "#E8B23A",
    "titular": None,      # None => usa el color de texto
    "texto": "#FFFFFF",
    "cta_texto": "#101010",
}


class MarcaError(ValueError):
    """Marca de cliente inexistente o mal formada."""


# --------------------------------------------------------------------------
# Resolucion
# --------------------------------------------------------------------------
def detectar(ruta: str | Path) -> Path | None:
    """Busca `marca.json` subiendo desde una ruta. Devuelve el archivo o None."""
    p = Path(ruta).resolve()
    if p.is_file():
        p = p.parent
    for _ in range(NIVELES_BUSQUEDA):
        candidato = p / NOMBRE_ARCHIVO
        if candidato.exists():
            return candidato
        if p.parent == p:
            break
        p = p.parent
    return None


def _raices_clientes() -> list[Path]:
    """Carpetas `clientes/` visibles desde el directorio actual, hacia arriba."""
    raices = []
    p = Path.cwd().resolve()
    for _ in range(NIVELES_BUSQUEDA):
        c = p / CARPETA_CLIENTES
        if c.is_dir():
            raices.append(c)
        if p.parent == p:
            break
        p = p.parent
    return raices


def disponibles() -> list[tuple[str, Path]]:
    """Clientes encontrados: (id, ruta de su marca.json)."""
    vistos: dict[str, Path] = {}
    for raiz in _raices_clientes():
        for d in sorted(raiz.iterdir()):
            archivo = d / NOMBRE_ARCHIVO
            if d.is_dir() and archivo.exists() and d.name not in vistos:
                vistos[d.name] = archivo
    return list(vistos.items())


def resolver(ref: str | Path) -> Path:
    """Convierte una referencia en la ruta de un `marca.json`.

    Acepta: la ruta del propio marca.json, la carpeta del cliente, o su id.
    """
    p = Path(ref)
    if p.is_file() and p.name == NOMBRE_ARCHIVO:
        return p
    if p.is_dir() and (p / NOMBRE_ARCHIVO).exists():
        return p / NOMBRE_ARCHIVO

    for raiz in _raices_clientes():
        candidato = raiz / str(ref) / NOMBRE_ARCHIVO
        if candidato.exists():
            return candidato

    ids = [i for i, _ in disponibles()]
    raise MarcaError(
        f"No encuentro la marca '{ref}'.\n"
        f"Clientes disponibles: {', '.join(ids) if ids else '(ninguno)'}\n"
        f"Crea uno con:  python -m engine.nuevo_cliente <id>"
    )


# --------------------------------------------------------------------------
# Carga
# --------------------------------------------------------------------------
def cargar(ref: str | Path | None = None, junto_a: str | Path | None = None) -> dict | None:
    """Carga la marca. Sin `ref`, la detecta subiendo desde `junto_a`.

    Devuelve None si no hay marca y no se pidio ninguna explicitamente.
    """
    if ref is not None:
        archivo = resolver(ref)
    elif junto_a is not None:
        archivo = detectar(junto_a)
        if archivo is None:
            return None
    else:
        return None

    try:
        m = json.loads(Path(archivo).read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise MarcaError(f"{archivo} no es JSON valido: {e}") from e

    m["_archivo"] = str(archivo)
    m["_raiz"] = str(Path(archivo).parent)
    _validar(m, archivo)
    return m


def _validar(m: dict, archivo: Path | str) -> None:
    for campo in ("id", "nombre", "perfil"):
        if campo not in m:
            raise MarcaError(f"{archivo} no tiene el campo '{campo}'")

    # El perfil de rubro tiene que existir: de el salen el look y los prompts.
    profiles.load(m["perfil"])

    colores = m.setdefault("colores", {})
    for clave, valor in COLORES_POR_DEFECTO.items():
        colores.setdefault(clave, valor)

    for clave, valor in colores.items():
        if valor is None:
            continue
        if not (isinstance(valor, str) and valor.startswith("#") and len(valor) in (4, 7)):
            raise MarcaError(
                f"{archivo}: el color '{clave}' es '{valor}'; debe ser hex tipo #D2BC54"
            )


# --------------------------------------------------------------------------
# Accesores
# --------------------------------------------------------------------------
def raiz(m: dict) -> Path:
    return Path(m["_raiz"])


def logo(m: dict) -> Path | None:
    """Ruta absoluta del logo, o None si no hay o el archivo falta."""
    rel = m.get("logo")
    if not rel:
        return None
    p = raiz(m) / rel
    return p if p.exists() else None


def linea_contacto(m: dict) -> str:
    """La linea de contacto para el pie de la pieza."""
    c = m.get("contacto") or {}
    if c.get("linea"):
        return c["linea"]
    partes = [c.get("instagram"), c.get("telefono")]
    return "  ·  ".join(p for p in partes if p)


def colores(m: dict) -> dict:
    return m["colores"]


def perfil(m: dict) -> dict:
    """El perfil de rubro, con el `look` sobreescrito por el de la marca."""
    p = profiles.load(m["perfil"])
    if m.get("look"):
        p = {**p, "look": {**p["look"], **m["look"]}}
    if m.get("fondos"):
        p = {**p, "fondos": {**p["fondos"], **m["fondos"]}}
    return p


def datos_pendientes(m: dict) -> list[str]:
    """Campos que siguen siendo marcador de posicion.

    Publicar un anuncio con el telefono de ejemplo es un fallo caro, asi que
    conviene detectarlo antes y no despues.
    """
    pendientes = []
    c = m.get("contacto") or {}
    sospechosas = ("tu telefono", "tuinstagram", "@tuinstagram", "[", "xxx",
                   "000", "ejemplo", "placeholder")
    for clave in ("instagram", "telefono", "ciudad", "linea"):
        v = str(c.get(clave, "")).lower()
        if v and any(s in v for s in sospechosas):
            pendientes.append(f"contacto.{clave} = {c[clave]!r}")
    if not c.get("instagram") and not c.get("telefono") and not c.get("linea"):
        pendientes.append("contacto (vacio)")
    if "lorem" in str(m.get("nombre", "")).lower():
        pendientes.append(f"nombre = {m['nombre']!r} (parece texto de plantilla)")
    if not logo(m) and m.get("logo"):
        pendientes.append(f"logo = {m['logo']!r} (el archivo no existe)")
    return pendientes


def _cli() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Marcas de cliente")
    p.add_argument("ref", nargs="?", help="Id, carpeta o marca.json. Sin nada, lista todas")
    a = p.parse_args()

    if not a.ref:
        encontradas = disponibles()
        if not encontradas:
            print("No hay clientes. Crea uno con:  python nuevo_cliente.py <id>")
            return
        for cid, archivo in encontradas:
            m = cargar(archivo)
            print(f"{cid:22} {m['nombre']:32} perfil={m['perfil']:12} "
                  f"acento={m['colores']['acento']}")
        return

    m = cargar(a.ref)
    print(json.dumps({k: v for k, v in m.items() if not k.startswith("_")},
                     indent=2, ensure_ascii=False))
    print(f"\nraiz  : {raiz(m)}")
    print(f"logo  : {logo(m) or '(sin logo)'}")
    print(f"perfil: {m['perfil']}")
    pend = datos_pendientes(m)
    if pend:
        print("\nPENDIENTE antes de publicar:")
        for x in pend:
            print(f"  - {x}")


if __name__ == "__main__":
    _cli()
