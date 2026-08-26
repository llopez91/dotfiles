"""Crea la estructura de carpetas de un cliente nuevo."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import profiles

SUBCARPETAS = [
    "marca",          # logo, variantes, iconos, tipografias
    "marca/iconos",
    "fotos",          # originales que llegan del cliente
    "out",            # piezas generadas
]

LEEME = """# {nombre}

Carpeta de cliente de Studio Creative.

## Estructura

- `marca.json` — colores, logo, contacto y perfil de rubro. **El motor lo lee solo.**
- `marca/` — logo y sus variantes, iconos, tipografías propias
- `fotos/` — originales tal como llegan del cliente
- `out/` — piezas generadas, una subcarpeta por campaña

## Uso

Apunta a una foto de dentro de esta carpeta y la marca se aplica sola:

```bash
python "{engine}\\pipeline.py" "fotos/corte.jpg" --todos-formatos
```

No hace falta pasar `--marca`: el motor busca `marca.json` subiendo desde la imagen.

## Pendiente

Rellena en `marca.json` los campos de `contacto` y coloca el logo real en
`marca/logo.png`. Compruébalo con:

```bash
python "{engine}\\marca.py" {cid}
```
"""


def crear(cid: str, nombre: str, perfil: str = "barberia",
          raiz: str | Path | None = None) -> Path:
    profiles.load(perfil)  # falla pronto si el rubro no existe

    base = Path(raiz) if raiz else Path.cwd() / "clientes"
    destino = base / cid
    if (destino / "marca.json").exists():
        raise FileExistsError(f"El cliente '{cid}' ya existe en {destino}")

    for sub in SUBCARPETAS:
        (destino / sub).mkdir(parents=True, exist_ok=True)

    marca = {
        "id": cid,
        "nombre": nombre,
        "perfil": perfil,
        "colores": {
            "acento": "#E8B23A",
            "titular": "#E8B23A",
            "texto": "#FFFFFF",
            "cta_texto": "#101010",
        },
        "logo": "marca/logo.png",
        "contacto": {
            "instagram": "",
            "telefono": "",
            "ciudad": "",
        },
        "copy": {
            "hashtags_locales": [],
        },
        "look": {},
        "fondos": {},
    }
    (destino / "marca.json").write_text(
        json.dumps(marca, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (destino / "README.md").write_text(
        LEEME.format(nombre=nombre, cid=cid,
                     engine=Path(__file__).resolve().parent),
        encoding="utf-8",
    )
    return destino


def _cli() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Crea la carpeta de un cliente nuevo")
    p.add_argument("id", help="Identificador corto, en kebab-case")
    p.add_argument("-n", "--nombre", help="Nombre comercial. Por defecto, el id")
    p.add_argument("-p", "--perfil", default="barberia",
                   choices=profiles.disponibles())
    p.add_argument("-r", "--raiz", help="Carpeta de clientes. Por defecto ./clientes")

    a = p.parse_args()
    destino = crear(a.id, a.nombre or a.id, a.perfil, a.raiz)
    print(f"Cliente creado en {destino}\n")
    for sub in SUBCARPETAS:
        print(f"  {sub}/")
    print(f"  marca.json")
    print("\nSiguiente paso: pon el logo en marca/logo.png y rellena el contacto.")


if __name__ == "__main__":
    _cli()
