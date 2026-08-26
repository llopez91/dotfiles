"""Carga y validacion de perfiles de rubro."""
from __future__ import annotations

import json
from pathlib import Path

PROFILES_DIR = Path(__file__).resolve().parent / "profiles"

NIVELES_IDENTITY = ("estricto", "moderado", "libre")

CAMPOS_LOOK = ("wb_strength", "gamma_sombras", "contraste", "saturacion", "brillo", "enfoque")


class ProfileError(ValueError):
    """Perfil de rubro invalido o inexistente."""


def disponibles() -> list[str]:
    """Ids de todos los perfiles instalados."""
    return sorted(p.stem for p in PROFILES_DIR.glob("*.json"))


def load(profile_id: str) -> dict:
    """Carga un perfil por id y lo valida."""
    ruta = PROFILES_DIR / f"{profile_id}.json"
    if not ruta.exists():
        raise ProfileError(
            f"No existe el perfil '{profile_id}'. Disponibles: {', '.join(disponibles())}"
        )
    try:
        perfil = json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise ProfileError(f"El perfil '{profile_id}' no es JSON valido: {e}") from e

    _validar(perfil, profile_id)
    return perfil


def _validar(perfil: dict, profile_id: str) -> None:
    for campo in ("id", "nombre", "identity_lock", "look", "fondos", "formatos", "copy"):
        if campo not in perfil:
            raise ProfileError(f"El perfil '{profile_id}' no tiene el campo '{campo}'")

    if perfil["identity_lock"] not in NIVELES_IDENTITY:
        raise ProfileError(
            f"identity_lock de '{profile_id}' es '{perfil['identity_lock']}'; "
            f"debe ser uno de {NIVELES_IDENTITY}"
        )

    faltantes = [c for c in CAMPOS_LOOK if c not in perfil["look"]]
    if faltantes:
        raise ProfileError(f"El look de '{profile_id}' no tiene: {', '.join(faltantes)}")

    if not perfil["fondos"]:
        raise ProfileError(f"El perfil '{profile_id}' no define ningun fondo")

    if not perfil["formatos"]:
        raise ProfileError(f"El perfil '{profile_id}' no define ningun formato")


def fondo(perfil: dict, nombre: str | None = None) -> tuple[str, str]:
    """Devuelve (nombre, prompt) del fondo pedido, o el primero del perfil."""
    fondos = perfil["fondos"]
    if nombre is None:
        nombre = next(iter(fondos))
    if nombre not in fondos:
        raise ProfileError(
            f"El perfil '{perfil['id']}' no tiene el fondo '{nombre}'. "
            f"Disponibles: {', '.join(fondos)}"
        )
    return nombre, fondos[nombre]


def escena(perfil: dict, nombre: str | None = None) -> tuple[str, str]:
    """Devuelve (nombre, prompt) de la escena publicitaria pedida."""
    escenas = perfil.get("escenas") or {}
    if not escenas:
        raise ProfileError(f"El perfil '{perfil['id']}' no define escenas publicitarias")
    if nombre is None:
        nombre = next(iter(escenas))
    if nombre not in escenas:
        raise ProfileError(
            f"El perfil '{perfil['id']}' no tiene la escena '{nombre}'. "
            f"Disponibles: {', '.join(escenas)}"
        )
    return nombre, escenas[nombre]


if __name__ == "__main__":
    for pid in disponibles():
        p = load(pid)
        print(f"{pid:14} {p['nombre']:34} identity_lock={p['identity_lock']:9} "
              f"fondos={len(p['fondos'])} formatos={','.join(p['formatos'])}")
