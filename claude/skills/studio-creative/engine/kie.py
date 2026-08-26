"""Cliente de la API de Kie AI.

Encapsula tres comportamientos reales del servidor que la documentacion oficial
no refleja (verificados contra el servidor el 2026-08-14):

1. El host de upload es kieai.redpandaai.co, NO api.kie.ai (la doc da 404).
2. El User-Agent por defecto de urllib recibe 403. Hay que mandar uno propio.
3. Las URLs del resultado vienen en data.resultJson, que es un STRING JSON
   que hay que parsear otra vez para llegar a resultUrls.
"""
from __future__ import annotations

import base64
import io
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

UPLOAD_URL = "https://kieai.redpandaai.co/api/file-base64-upload"
CREATE_URL = "https://api.kie.ai/api/v1/jobs/createTask"
RECORD_URL = "https://api.kie.ai/api/v1/jobs/recordInfo"
CREDIT_URL = "https://api.kie.ai/api/v1/chat/credit"

# Sin esto la API responde 403. No es opcional.
USER_AGENT = "curl/8.7.1"

MODEL_PRO = "nano-banana-pro"
MODEL_EDIT = "google/nano-banana-edit"

# Costo medido por imagen, en creditos.
COSTO = {MODEL_PRO: 18, MODEL_EDIT: 4}

# El endpoint base64 no admite mas de 10 MB.
MAX_UPLOAD_BYTES = 9 * 1024 * 1024

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class KieError(RuntimeError):
    """Fallo al hablar con la API de Kie AI."""


def api_key() -> str:
    """Resuelve la API key: primero el entorno, luego el .env del skill."""
    key = os.environ.get("KIE_API_KEY", "").strip()
    if key:
        return key
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("KIE_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                if key:
                    return key
    raise KieError(
        "Falta la API key de Kie AI.\n"
        "Ponla en la variable de entorno KIE_API_KEY, o escribe la linea\n"
        f"    KIE_API_KEY=tu_key\n"
        f"en el archivo {ENV_FILE}"
    )


def _headers(extra: dict | None = None) -> dict:
    h = {
        "Authorization": f"Bearer {api_key()}",
        "User-Agent": USER_AGENT,
        "Accept": "*/*",
    }
    if extra:
        h.update(extra)
    return h


def _call(url: str, payload: dict | None = None, timeout: int = 180) -> dict:
    """POST si hay payload, GET si no. Devuelve el JSON parseado."""
    if payload is None:
        req = urllib.request.Request(url, headers=_headers(), method="GET")
    else:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=_headers({"Content-Type": "application/json"}),
            method="POST",
        )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detalle = ""
        try:
            detalle = e.read().decode("utf-8", "replace")[:400]
        except Exception:
            pass
        if e.code == 403:
            detalle += (
                "\n(403 suele significar User-Agent bloqueado; el cliente ya manda uno, "
                "revisa que no lo hayan sobreescrito)"
            )
        raise KieError(f"HTTP {e.code} en {url}: {detalle}") from e
    except urllib.error.URLError as e:
        raise KieError(f"No se pudo conectar a {url}: {e.reason}") from e


def credits() -> float:
    """Saldo de creditos de la cuenta."""
    res = _call(CREDIT_URL)
    if res.get("code") != 200:
        raise KieError(f"No se pudo consultar el saldo: {res.get('msg')}")
    return float(res.get("data") or 0)


def _bytes_para_subir(path: Path) -> tuple[bytes, str]:
    """Lee la imagen, reescalandola si excede el limite del endpoint."""
    raw = path.read_bytes()
    if len(raw) <= MAX_UPLOAD_BYTES:
        return raw, path.suffix.lstrip(".").lower() or "png"

    import imagenes

    im = imagenes.abrir(path)
    escala = (MAX_UPLOAD_BYTES / len(raw)) ** 0.5
    nuevo = (max(1, int(im.width * escala)), max(1, int(im.height * escala)))
    im = im.resize(nuevo, Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=92)
    print(f"  imagen reescalada a {nuevo} para respetar el limite de subida")
    return buf.getvalue(), "jpg"


def upload_image(path: str | Path, upload_path: str = "images/studio-creative") -> str:
    """Sube una imagen local y devuelve su URL temporal (vive 3 dias)."""
    path = Path(path)
    if not path.exists():
        raise KieError(f"No existe la imagen: {path}")

    raw, ext = _bytes_para_subir(path)
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    b64 = base64.b64encode(raw).decode("ascii")

    res = _call(
        UPLOAD_URL,
        {
            "base64Data": f"data:image/{mime};base64,{b64}",
            "uploadPath": upload_path,
            # Nombre unico: subir dos veces el mismo nombre reusa la URL anterior.
            "fileName": f"{path.stem}-{int(time.time() * 1000)}.{ext}",
        },
    )
    if not res.get("success") and res.get("code") != 200:
        raise KieError(f"Fallo la subida: {res.get('msg')}")
    url = (res.get("data") or {}).get("downloadUrl")
    if not url:
        raise KieError(f"La subida no devolvio downloadUrl: {json.dumps(res)[:300]}")
    return url


def create_task(model: str, inputs: dict) -> str:
    """Crea una tarea de generacion y devuelve su taskId."""
    res = _call(CREATE_URL, {"model": model, "input": inputs})
    if res.get("code") != 200:
        raise KieError(f"createTask rechazado (code {res.get('code')}): {res.get('msg')}")
    data = res.get("data") or {}
    task_id = data.get("taskId")
    if not task_id:
        raise KieError(f"createTask no devolvio taskId: {json.dumps(res)[:300]}")
    return task_id


def poll_task(task_id: str, label: str = "", timeout: int = 420, intervalo: int = 6) -> list[str]:
    """Espera a que la tarea termine y devuelve las URLs del resultado."""
    etiqueta = f"[{label}] " if label else ""
    inicio = time.time()
    while time.time() - inicio < timeout:
        time.sleep(intervalo)
        try:
            res = _call(f"{RECORD_URL}?taskId={task_id}", timeout=60)
        except KieError as e:
            print(f"  {etiqueta}reintentando tras error transitorio: {e}")
            continue

        d = res.get("data") or {}
        estado = d.get("state")
        print(f"  {etiqueta}{estado}", flush=True)

        if estado == "success":
            # resultJson es un string JSON, no un objeto. Doble parseo.
            bruto = d.get("resultJson") or "{}"
            try:
                urls = json.loads(bruto).get("resultUrls") or []
            except json.JSONDecodeError as e:
                raise KieError(f"resultJson ilegible: {bruto[:200]}") from e
            if not urls:
                raise KieError("La tarea termino sin producir imagenes")
            return urls

        if estado == "fail":
            raise KieError(
                f"La generacion fallo. code={d.get('failCode')} msg={d.get('failMsg')}"
            )

    raise KieError(
        f"Timeout tras {timeout}s. La tarea sigue viva: consulta despues con\n"
        f"    python -m engine.kie estado {task_id}"
    )


def download(url: str, dest: str | Path) -> Path:
    """Descarga el resultado a disco."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            dest.write_bytes(r.read())
    except urllib.error.URLError as e:
        raise KieError(f"No se pudo descargar {url}: {e}") from e
    return dest


def run(model: str, inputs: dict, dest: str | Path, label: str = "") -> Path:
    """Crea la tarea, espera, descarga. El camino completo en una llamada."""
    task_id = create_task(model, inputs)
    print(f"  tarea {task_id} ({model}, ~{COSTO.get(model, '?')} creditos)")
    urls = poll_task(task_id, label=label)
    return download(urls[0], dest)


def _cli() -> None:
    import argparse

    p = argparse.ArgumentParser(description="Utilidades del cliente de Kie AI")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("creditos", help="Consultar saldo")
    e = sub.add_parser("estado", help="Consultar una tarea por id")
    e.add_argument("task_id")
    u = sub.add_parser("subir", help="Subir una imagen y mostrar su URL")
    u.add_argument("path")

    a = p.parse_args()
    if a.cmd == "creditos":
        saldo = credits()
        print(f"{saldo:.1f} creditos")
        print(f"  ~{int(saldo // COSTO[MODEL_PRO])} imagenes con {MODEL_PRO}")
        print(f"  ~{int(saldo // COSTO[MODEL_EDIT])} imagenes con {MODEL_EDIT}")
    elif a.cmd == "estado":
        res = _call(f"{RECORD_URL}?taskId={a.task_id}")
        print(json.dumps(res.get("data") or res, indent=2, ensure_ascii=False))
    elif a.cmd == "subir":
        print(upload_image(a.path))


if __name__ == "__main__":
    _cli()
