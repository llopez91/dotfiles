"""Prueba de conectividad extremo a extremo contra la API real.

GASTA 4 CREDITOS (usa el modelo economico a proposito).

    python smoke_test.py

Verifica el camino completo: subir -> crear tarea -> consultar -> descargar.
Las pruebas que no gastan nada estan en test_engine.py.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import kie
from PIL import Image


def main() -> int:
    print("Smoke test de Kie AI (gasta ~4 creditos)\n")

    try:
        saldo = kie.credits()
    except kie.KieError as e:
        print(f"FALLA al consultar el saldo: {e}")
        return 1
    print(f"1/5 saldo ......... {saldo:.1f} creditos")

    if saldo < kie.COSTO[kie.MODEL_EDIT]:
        print("   saldo insuficiente para la prueba")
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        origen = tmp / "smoke.png"
        Image.new("RGB", (768, 960), (90, 110, 130)).save(origen)

        try:
            url = kie.upload_image(origen, upload_path="images/smoke")
        except kie.KieError as e:
            print(f"FALLA en la subida: {e}")
            return 1
        print(f"2/5 subida ........ {url[:64]}...")

        try:
            task_id = kie.create_task(kie.MODEL_EDIT, {
                "prompt": "Replace the flat background with a clean dark grey studio backdrop.",
                "image_urls": [url],
                "output_format": "png",
                "aspect_ratio": "4:5",
            })
        except kie.KieError as e:
            print(f"FALLA al crear la tarea: {e}")
            return 1
        print(f"3/5 tarea ......... {task_id}")

        try:
            urls = kie.poll_task(task_id, label="smoke")
        except kie.KieError as e:
            print(f"FALLA en el polling: {e}")
            return 1
        print(f"4/5 resultado ..... {len(urls)} imagen(es)")

        destino = tmp / "resultado.png"
        try:
            kie.download(urls[0], destino)
            with Image.open(destino) as im:
                tam = im.size
        except Exception as e:
            print(f"FALLA en la descarga: {e}")
            return 1
        print(f"5/5 descarga ...... {tam[0]}x{tam[1]}, {destino.stat().st_size} bytes")

    gastado = saldo - kie.credits()
    print(f"\nOK. Gastados {gastado:.1f} creditos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
