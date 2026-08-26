"""Pruebas del motor. Ninguna gasta creditos.

    python -m pytest test_engine.py -q       (si hay pytest)
    python test_engine.py                    (sin pytest)

El smoke test en vivo, que si gasta 4 creditos, va aparte en smoke_test.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))

import compose
import finish
import kie
import marca
import prep
import profiles
import relight
import scene

REF = Path(r"C:\Users\llope\Documents\Proyectos\studio-creative\Captura de pantalla 2026-08-14 132344.png")
TMP = Path(__file__).resolve().parent / "_test_out"


def _img(w=800, h=1000, color=(120, 100, 80)) -> Image.Image:
    """Imagen sintetica con algo de estructura, para no depender de la de referencia."""
    a = np.zeros((h, w, 3), dtype=np.uint8)
    a[:, :] = color
    a[h // 4: 3 * h // 4, w // 4: 3 * w // 4] = (200, 180, 160)
    a[: h // 8, :] = (20, 20, 20)
    return Image.fromarray(a)


# --------------------------------------------------------------------------
# Perfiles
# --------------------------------------------------------------------------
def test_todos_los_perfiles_cargan():
    ids = profiles.disponibles()
    assert set(ids) >= {"barberia", "comida", "producto", "inmobiliaria", "fitness"}
    for pid in ids:
        p = profiles.load(pid)
        assert p["id"] == pid
        assert p["identity_lock"] in profiles.NIVELES_IDENTITY


def test_perfil_inexistente_falla():
    try:
        profiles.load("no-existe")
    except profiles.ProfileError:
        return
    raise AssertionError("deberia haber fallado")


def test_perfil_invalido_falla(tmp: Path | None = None):
    destino = profiles.PROFILES_DIR / "_invalido.json"
    destino.write_text(json.dumps({"id": "_invalido", "nombre": "x"}), encoding="utf-8")
    try:
        profiles.load("_invalido")
        raise AssertionError("deberia haber fallado por campos faltantes")
    except profiles.ProfileError:
        pass
    finally:
        destino.unlink()


def test_identity_lock_invalido_falla():
    destino = profiles.PROFILES_DIR / "_malo.json"
    p = json.loads((profiles.PROFILES_DIR / "barberia.json").read_text(encoding="utf-8"))
    p["identity_lock"] = "total"
    destino.write_text(json.dumps(p), encoding="utf-8")
    try:
        profiles.load("_malo")
        raise AssertionError("deberia rechazar identity_lock invalido")
    except profiles.ProfileError:
        pass
    finally:
        destino.unlink()


def test_fondo_por_defecto_y_desconocido():
    p = profiles.load("barberia")
    nombre, prompt = profiles.fondo(p)
    assert nombre and len(prompt) > 40
    try:
        profiles.fondo(p, "no-existe")
        raise AssertionError("deberia fallar con fondo desconocido")
    except profiles.ProfileError:
        pass


# --------------------------------------------------------------------------
# Tono
# --------------------------------------------------------------------------
def test_curva_sombras_en_rango_y_monotona():
    for gamma in (1.0, 1.2, 1.3, 1.6, 2.0):
        lut = prep.curva_sombras(gamma)
        assert len(lut) == 256
        assert min(lut) >= 0 and max(lut) <= 255
        assert all(lut[i] <= lut[i + 1] for i in range(255)), f"no monotona con gamma {gamma}"


def test_curva_sombras_levanta_y_protege_altas():
    lut = prep.curva_sombras(1.30)
    assert lut[60] > 60, "las sombras deberian subir"
    assert lut[250] >= 245, "las altas luces no deberian bajar"
    assert lut[255] == 255


def test_gray_world_neutraliza():
    # Imagen con dominante verde marcada.
    a = np.zeros((100, 100, 3), dtype=np.uint8)
    a[:, :] = (100, 160, 90)
    im = Image.fromarray(a)
    _, ganancias = prep.gray_world(im, strength=1.0)
    assert ganancias[1] < 1.0, "el verde dominante deberia bajar"
    assert ganancias[2] > 1.0, "el azul escaso deberia subir"


def test_gray_world_atenuado_es_mas_suave():
    a = np.zeros((50, 50, 3), dtype=np.uint8)
    a[:, :] = (100, 160, 90)
    im = Image.fromarray(a)
    _, fuerte = prep.gray_world(im, 1.0)
    _, suave = prep.gray_world(im, 0.6)
    assert abs(suave[1] - 1.0) < abs(fuerte[1] - 1.0)


def test_ganancias_de_la_foto_de_referencia():
    """Regresion: los valores medidos el 2026-08-14 sobre la foto de prueba."""
    if not REF.exists():
        print("  (omitido: no esta la foto de referencia)")
        return
    im = Image.open(REF).convert("RGB")
    _, g = prep.gray_world(im, 0.6)
    esperado = (0.905, 1.007, 1.129)
    for real, exp in zip(g, esperado):
        assert abs(real - exp) < 0.02, f"ganancia {real} lejos de la medida {exp}"


# --------------------------------------------------------------------------
# Geometria
# --------------------------------------------------------------------------
def test_mapear_punto_centro_es_invariante():
    origen, destino = (800, 1000), (1200, 1300)
    x, y = prep.mapear_punto(400, 500, 35, origen, destino)
    assert abs(x - 600) < 0.01 and abs(y - 650) < 0.01


def test_mapear_punto_angulo_cero():
    origen = destino = (800, 1000)
    x, y = prep.mapear_punto(123, 456, 0, origen, destino)
    assert abs(x - 123) < 0.01 and abs(y - 456) < 0.01


def test_mapear_punto_rota_antihorario():
    """Un punto a la derecha del centro debe subir al rotar en antihorario."""
    origen, destino = (800, 800), (800, 800)
    x, y = prep.mapear_punto(700, 400, 35, origen, destino)
    assert x > 400, "deberia seguir a la derecha"
    assert y < 400, "deberia haber subido"


def test_encuadre_respeta_los_limites():
    im = _img(1000, 1400)
    for sujeto in [None, (10, 10, 200, 300), (900, 1300, 999, 1399), (400, 100, 600, 900)]:
        recorte, caja = prep.encuadrar(im, (4, 5), sujeto)
        x0, y0, x1, y1 = caja
        assert 0 <= x0 < x1 <= im.width, f"caja fuera de rango: {caja}"
        assert 0 <= y0 < y1 <= im.height, f"caja fuera de rango: {caja}"
        assert recorte.size[0] > 0 and recorte.size[1] > 0


def test_encuadre_da_el_ratio_pedido():
    im = _img(1400, 1400)
    for ratio in [(4, 5), (1, 1), (9, 16)]:
        recorte, _ = prep.encuadrar(im, ratio, (600, 300, 800, 900))
        real = recorte.width / recorte.height
        esperado = ratio[0] / ratio[1]
        assert abs(real - esperado) < 0.02, f"ratio {real:.3f} != {esperado:.3f}"


def test_enderezar_blur_no_deja_gris():
    im = _img(400, 500)
    rot = prep.enderezar(im, 35, relleno="blur")
    a = np.asarray(rot)
    esquina = a[:12, :12].reshape(-1, 3)
    gris_exacto = np.all(esquina == 128, axis=1).sum()
    assert gris_exacto == 0, "el relleno blur no deberia dejar gris plano"


def test_enderezar_gris_si_deja_gris():
    im = _img(400, 500)
    rot = prep.enderezar(im, 35, relleno="gris")
    a = np.asarray(rot)
    assert np.all(a[0, 0] == 128), "el relleno gris deberia marcar las esquinas"


def test_enderezar_cero_no_toca():
    im = _img(300, 400)
    assert prep.enderezar(im, 0).size == im.size


def test_prep_devuelve_la_caja_en_coordenadas_de_salida():
    TMP.mkdir(exist_ok=True)
    src = TMP / "prep_src.png"
    _img(1000, 1400).save(src)
    look = profiles.load("barberia")["look"]

    ruta, caja = prep.prep(src, TMP / "prep_out.png", look,
                           angulo=0, sujeto=(300, 200, 700, 900),
                           salida=(1080, 1350))
    assert ruta.exists()
    assert caja is not None
    x0, y0, x1, y1 = caja
    assert x1 > x0 and y1 > y0, "la caja devuelta esta degenerada"
    # Tiene que caer dentro de la imagen de salida, que es lo que la consume.
    assert -5 <= x0 and x1 <= 1085, f"caja fuera de la salida: {caja}"


def test_prep_sin_sujeto_devuelve_none():
    TMP.mkdir(exist_ok=True)
    src = TMP / "prep_src2.png"
    _img(1000, 1400).save(src)
    _, caja = prep.prep(src, TMP / "prep_out2.png",
                        profiles.load("barberia")["look"])
    assert caja is None


def test_espacio_enderezada_no_remapea():
    """Con angulos grandes la caja se lee sobre la enderezada y va tal cual."""
    TMP.mkdir(exist_ok=True)
    src = TMP / "prep_src3.png"
    _img(800, 1000).save(src)
    look = profiles.load("barberia")["look"]

    _, en_original = prep.prep(src, TMP / "a.png", look, angulo=35,
                               sujeto=(300, 200, 600, 700),
                               sujeto_espacio="original", salida=(400, 500))
    _, en_enderezada = prep.prep(src, TMP / "b.png", look, angulo=35,
                                 sujeto=(300, 200, 600, 700),
                                 sujeto_espacio="enderezada", salida=(400, 500))
    assert en_original != en_enderezada, \
        "los dos espacios no pueden dar el mismo resultado con 35 grados"


def test_espacio_invalido_falla():
    TMP.mkdir(exist_ok=True)
    src = TMP / "prep_src4.png"
    _img(400, 500).save(src)
    try:
        prep.prep(src, TMP / "c.png", profiles.load("barberia")["look"],
                  sujeto_espacio="marciano")
        raise AssertionError("deberia rechazar el espacio")
    except ValueError:
        pass


def test_angulo_cero_iguala_los_dos_espacios():
    TMP.mkdir(exist_ok=True)
    src = TMP / "prep_src5.png"
    _img(800, 1000).save(src)
    look = profiles.load("barberia")["look"]
    caja = (200, 150, 600, 750)
    _, a = prep.prep(src, TMP / "d.png", look, angulo=0, sujeto=caja,
                     sujeto_espacio="original", salida=(400, 500))
    _, b = prep.prep(src, TMP / "e.png", look, angulo=0, sujeto=caja,
                     sujeto_espacio="enderezada", salida=(400, 500))
    assert a == b, "sin rotacion los dos espacios son el mismo"


# --------------------------------------------------------------------------
# Prompts
# --------------------------------------------------------------------------
def test_identity_lock_estricto_incluye_el_bloqueo():
    p = relight.construir_prompt("Fondo de prueba.", "estricto", True)
    assert "locked, untouchable cut-out layer" in p
    assert "grey filler" in p
    assert "Fondo de prueba." in p


def test_identity_lock_libre_no_bloquea():
    p = relight.construir_prompt("Fondo de prueba.", "libre", False)
    assert "untouchable cut-out" not in p
    assert "Fondo de prueba." in p


def test_identity_lock_moderado():
    p = relight.construir_prompt("Fondo.", "moderado", False)
    assert "Preserve the main subject faithfully" in p
    assert "untouchable cut-out" not in p


def test_escena_estricta_lleva_refuerzo():
    p = scene.construir_prompt("Escena de prueba.", "estricto")
    assert "locked, untouchable cut-out layer" in p
    assert "adapt the scene instead" in p, "falta el refuerzo propio del modo escena"


def test_escena_deja_espacio_para_texto():
    assert "negative space" in scene.construir_prompt("X.", "libre", dejar_espacio=True)
    assert "negative space" not in scene.construir_prompt("X.", "libre", dejar_espacio=False)


# --------------------------------------------------------------------------
# Cliente de la API (sin red)
# --------------------------------------------------------------------------
def test_result_json_anidado_se_parsea():
    """data.resultJson es un STRING JSON: el doble parseo es el punto clave."""
    respuesta = {
        "code": 200,
        "data": {
            "state": "success",
            "resultJson": json.dumps({"resultUrls": ["https://x/y.png"]}),
        },
    }
    original = kie._call
    kie._call = lambda url, payload=None, timeout=180: respuesta
    try:
        urls = kie.poll_task("t1", intervalo=0)
        assert urls == ["https://x/y.png"]
    finally:
        kie._call = original


def test_estado_fail_lanza_error_con_detalle():
    respuesta = {"code": 200, "data": {"state": "fail",
                                       "failCode": "E42", "failMsg": "boom"}}
    original = kie._call
    kie._call = lambda url, payload=None, timeout=180: respuesta
    try:
        kie.poll_task("t1", intervalo=0)
        raise AssertionError("deberia haber lanzado KieError")
    except kie.KieError as e:
        assert "E42" in str(e) and "boom" in str(e)
    finally:
        kie._call = original


def test_estados_intermedios_no_terminan():
    """waiting/queuing/generating deben seguir esperando, no devolver nada."""
    secuencia = ["waiting", "queuing", "generating", "success"]
    llamadas = {"n": 0}

    def falso(url, payload=None, timeout=180):
        estado = secuencia[min(llamadas["n"], len(secuencia) - 1)]
        llamadas["n"] += 1
        d = {"state": estado}
        if estado == "success":
            d["resultJson"] = json.dumps({"resultUrls": ["https://ok.png"]})
        return {"code": 200, "data": d}

    original = kie._call
    kie._call = falso
    try:
        assert kie.poll_task("t1", intervalo=0) == ["https://ok.png"]
        assert llamadas["n"] == 4
    finally:
        kie._call = original


def test_user_agent_presente():
    h = kie._headers()
    assert h["User-Agent"] == kie.USER_AGENT, "sin User-Agent propio la API responde 403"
    assert h["Authorization"].startswith("Bearer ")


def test_hosts_correctos():
    """La doc oficial da api.kie.ai para el upload y devuelve 404."""
    assert "redpandaai.co" in kie.UPLOAD_URL
    assert kie.CREATE_URL.startswith("https://api.kie.ai/api/v1/jobs/createTask")


def test_nombres_de_modelo():
    assert kie.MODEL_PRO == "nano-banana-pro", "sin prefijo google/, verificado contra el servidor"
    assert kie.MODEL_EDIT == "google/nano-banana-edit"


# --------------------------------------------------------------------------
# Export
# --------------------------------------------------------------------------
def test_formatos_tienen_las_medidas_exactas():
    TMP.mkdir(exist_ok=True)
    maestro = TMP / "maestro.png"
    _img(1856, 2320).save(maestro)
    look = profiles.load("barberia")["look"]
    res = finish.exportar(maestro, list(finish.FORMATOS), look, TMP)
    for nombre, ruta in res.items():
        esperado = finish.FORMATOS[nombre][:2]
        with Image.open(ruta) as im:
            assert im.size == esperado, f"{nombre}: {im.size} != {esperado}"


def test_wide_extiende_en_vez_de_recortar():
    """De 4:5 a 16:9 recortando se decapitaria al sujeto."""
    maestro = _img(1000, 1250)
    for lado in ("derecha", "izquierda"):
        salida = finish._extender_lienzo(maestro, 1920, 1080, lado)
        assert salida.size == (1920, 1080), f"{lado}: {salida.size}"


def test_wide_oscurece_el_lado_libre():
    """El hueco para el titular es el lado OPUESTO al sujeto.

    Maestro de color plano a proposito: asi la unica asimetria horizontal es
    la que introduce el degradado, y el test no se cuela por el contenido.
    """
    plano = Image.new("RGB", (1000, 1250), (150, 150, 150))

    der = np.asarray(finish._extender_lienzo(plano, 1920, 1080, "derecha"))
    assert der[:, :250].mean() < der[:, -250:].mean(), \
        "con el sujeto a la derecha, el hueco de la izquierda deberia ir oscuro"

    izq = np.asarray(finish._extender_lienzo(plano, 1920, 1080, "izquierda"))
    assert izq[:, -250:].mean() < izq[:, :250].mean(), \
        "con el sujeto a la izquierda, el hueco de la derecha deberia ir oscuro"


def test_formato_desconocido_falla():
    TMP.mkdir(exist_ok=True)
    maestro = TMP / "m2.png"
    _img(800, 1000).save(maestro)
    try:
        finish.exportar(maestro, ["no-existe"], profiles.load("barberia")["look"], TMP)
        raise AssertionError("deberia rechazar el formato")
    except ValueError as e:
        assert "no-existe" in str(e)


# --------------------------------------------------------------------------
# Composicion
# --------------------------------------------------------------------------
def test_componer_conserva_tamano_y_escribe():
    TMP.mkdir(exist_ok=True)
    src = TMP / "base.png"
    _img(1080, 1350).save(src)
    dest = compose.componer(src, TMP / "arte.png",
                            titular="Corte y barba", subtitulo="Reserva hoy",
                            cta="Agenda tu cita", contacto="@barberia")
    with Image.open(dest) as im:
        assert im.size == (1080, 1350)


def test_componer_texto_largo_no_revienta():
    TMP.mkdir(exist_ok=True)
    src = TMP / "base2.png"
    _img(1080, 1350).save(src)
    largo = "Promocion especial de temporada con descuentos increibles " * 4
    dest = compose.componer(src, TMP / "arte2.png", titular=largo, subtitulo=largo)
    assert dest.exists()


def test_componer_posicion_invalida_falla():
    TMP.mkdir(exist_ok=True)
    src = TMP / "base3.png"
    _img(600, 600).save(src)
    try:
        compose.componer(src, TMP / "x.png", titular="A", posicion="diagonal")
        raise AssertionError("deberia rechazar la posicion")
    except ValueError:
        pass


def test_scrim_oscurece_el_borde_donde_va_el_texto():
    """El extremo oscuro tiene que caer en el borde, no en el interior."""
    im = Image.new("RGB", (400, 600), (200, 200, 200))
    casos = {
        "abajo":     lambda a: a[-40:].mean() < a[:40].mean(),
        "arriba":    lambda a: a[:40].mean() < a[-40:].mean(),
        "izquierda": lambda a: a[:, :40].mean() < a[:, -40:].mean(),
        "derecha":   lambda a: a[:, -40:].mean() < a[:, :40].mean(),
    }
    for posicion, comprueba in casos.items():
        a = np.asarray(compose._scrim(im, posicion, 0.8))
        assert comprueba(a), f"el scrim '{posicion}' oscurece el borde equivocado"


def _marca_temporal(tmp: Path, **extra) -> Path:
    """Crea un cliente minimo en disco y devuelve su marca.json."""
    d = tmp / "clientes" / "prueba"
    d.mkdir(parents=True, exist_ok=True)
    datos = {"id": "prueba", "nombre": "Prueba", "perfil": "barberia"}
    datos.update(extra)
    archivo = d / "marca.json"
    archivo.write_text(json.dumps(datos), encoding="utf-8")
    return archivo


def test_marca_se_detecta_subiendo_desde_la_imagen():
    TMP.mkdir(exist_ok=True)
    archivo = _marca_temporal(TMP)
    foto = archivo.parent / "fotos" / "sub" / "x.png"
    foto.parent.mkdir(parents=True, exist_ok=True)
    _img(50, 50).save(foto)

    assert marca.detectar(foto) == archivo, "deberia encontrarla subiendo"
    m = marca.cargar(junto_a=foto)
    assert m and m["id"] == "prueba"


def test_sin_marca_cerca_devuelve_none():
    TMP.mkdir(exist_ok=True)
    suelta = TMP / "suelta"
    suelta.mkdir(exist_ok=True)
    (suelta / "y.png").write_bytes(b"x")
    # Ninguna marca por encima de esta ruta dentro del limite de busqueda.
    if marca.detectar(suelta / "y.png") is None:
        assert marca.cargar(junto_a=suelta / "y.png") is None


def test_marca_rellena_colores_por_defecto():
    TMP.mkdir(exist_ok=True)
    m = marca.cargar(_marca_temporal(TMP))
    for clave in marca.COLORES_POR_DEFECTO:
        assert clave in m["colores"], f"falta el color '{clave}'"


def test_marca_rechaza_color_invalido():
    TMP.mkdir(exist_ok=True)
    archivo = _marca_temporal(TMP, colores={"acento": "dorado"})
    try:
        marca.cargar(archivo)
        raise AssertionError("deberia rechazar un color que no es hex")
    except marca.MarcaError as e:
        assert "acento" in str(e)


def test_marca_rechaza_perfil_inexistente():
    TMP.mkdir(exist_ok=True)
    archivo = _marca_temporal(TMP, perfil="rubro-que-no-existe")
    try:
        marca.cargar(archivo)
        raise AssertionError("deberia rechazar un perfil inexistente")
    except (marca.MarcaError, profiles.ProfileError):
        pass


def test_marca_detecta_datos_pendientes():
    """Publicar con el telefono de ejemplo es un fallo caro. Se avisa antes."""
    TMP.mkdir(exist_ok=True)
    m = marca.cargar(_marca_temporal(
        TMP, nombre="LOREM Barberia",
        contacto={"instagram": "@tuinstagram", "telefono": "tu telefono"}))
    pendientes = " ".join(marca.datos_pendientes(m))
    assert "instagram" in pendientes and "telefono" in pendientes
    assert "plantilla" in pendientes, "deberia avisar del nombre de plantilla"


def test_marca_completa_no_tiene_pendientes():
    TMP.mkdir(exist_ok=True)
    m = marca.cargar(_marca_temporal(
        TMP, nombre="Barberia El Corte",
        logo=None,
        contacto={"instagram": "@elcorte", "telefono": "300 111 2233", "ciudad": "Bogota"}))
    assert marca.datos_pendientes(m) == []


def test_marca_sobreescribe_el_look_del_perfil():
    TMP.mkdir(exist_ok=True)
    base = profiles.load("barberia")["look"]["contraste"]
    m = marca.cargar(_marca_temporal(TMP, look={"contraste": base + 0.25}))
    p = marca.perfil(m)
    assert abs(p["look"]["contraste"] - (base + 0.25)) < 1e-6
    # Los campos no sobreescritos siguen viniendo del perfil de rubro.
    assert p["look"]["wb_strength"] == profiles.load("barberia")["look"]["wb_strength"]


def test_linea_contacto():
    TMP.mkdir(exist_ok=True)
    m = marca.cargar(_marca_temporal(
        TMP, contacto={"instagram": "@x", "telefono": "300"}))
    assert marca.linea_contacto(m) == "@x  ·  300"
    m2 = marca.cargar(_marca_temporal(TMP, contacto={"linea": "escribeme"}))
    assert marca.linea_contacto(m2) == "escribeme"


def test_no_deja_separadores_huerfanos():
    """textwrap deja el punto medio empezando linea y se lee como errata."""
    assert compose._sin_huerfanos(["En todos los cortes", "· todo el mes de", "marzo"]) == \
        ["En todos los cortes ·", "todo el mes de", "marzo"]
    assert compose._sin_huerfanos(["Corte", "y barba"]) == ["Corte y", "barba"]
    # Un separador solo en la primera linea no tiene a donde subir.
    assert compose._sin_huerfanos(["· solo"]) == ["· solo"]
    # Una linea que es solo el separador se absorbe entera.
    assert compose._sin_huerfanos(["Corte", "·", "barba"]) == ["Corte ·", "barba"]
    assert compose._sin_huerfanos([]) == []


def test_envolver_no_parte_si_cabe():
    """Estimar el ancho con la 'M' partia titulares que cabian de sobra."""
    im = Image.new("RGB", (100, 100))
    d = compose.ImageDraw.Draw(im)
    f = compose._buscar_fuente(compose.FUENTES_TITULAR, 124)
    ancho_real = compose._ancho(d, "30% DTO", f)
    # Con columna holgada tiene que salir en una sola linea.
    assert compose._envolver(d, "30% DTO", f, ancho_real + 40) == ["30% DTO"]
    # Y con columna justa por debajo, en dos.
    assert len(compose._envolver(d, "30% DTO", f, ancho_real - 40)) == 2


def test_envolver_respeta_el_ancho():
    im = Image.new("RGB", (100, 100))
    d = compose.ImageDraw.Draw(im)
    f = compose._buscar_fuente(compose.FUENTES_TEXTO, 40)
    texto = "En todos los cortes con acabado a navaja durante todo el mes"
    for ancho_max in (200, 400, 800):
        for linea in compose._envolver(d, texto, f, ancho_max):
            # Una palabra suelta puede exceder; dos nunca.
            if " " in linea:
                assert compose._ancho(d, linea, f) <= ancho_max, \
                    f"linea '{linea}' excede {ancho_max}"


def test_envolver_palabra_mas_ancha_que_la_columna():
    im = Image.new("RGB", (100, 100))
    d = compose.ImageDraw.Draw(im)
    f = compose._buscar_fuente(compose.FUENTES_TEXTO, 40)
    lineas = compose._envolver(d, "electroencefalografista", f, 50)
    assert lineas == ["electroencefalografista"], "no debe trocear la palabra ni colgarse"


def test_espacio_texto_reserva_hueco_sin_recortar():
    """El sujeto tiene que caber entero: es lo que el post quiere ensenar."""
    maestro = _img(1856, 2304)
    salida = finish.con_espacio(maestro, 1080, 1350, escala=0.74, ancla="arriba-derecha")
    assert salida.size == (1080, 1350)
    # Con escala 0.74 y ancla arriba, la franja inferior queda libre.
    a = np.asarray(salida)
    assert a[-200:].std() < a[:200].std(), "la franja de texto deberia ser mas plana"


def test_espacio_texto_valida_argumentos():
    maestro = _img(400, 500)
    for ancla in finish.ANCLAS:
        assert finish.con_espacio(maestro, 400, 500, 0.7, ancla).size == (400, 500)
    for malo, escala in (("centro-centro", 0.7), ("arriba-derecha", 1.5), ("arriba-derecha", 0.1)):
        try:
            finish.con_espacio(maestro, 400, 500, escala, malo)
            raise AssertionError(f"deberia rechazar ({malo}, {escala})")
        except ValueError:
            pass


def test_scrim_no_toca_el_lado_opuesto():
    im = Image.new("RGB", (400, 600), (200, 200, 200))
    a = np.asarray(compose._scrim(im, "abajo", 0.8, extension=0.4))
    assert a[:20].mean() > 195, "la zona sin texto deberia quedar intacta"


# --------------------------------------------------------------------------
def _correr():
    pruebas = [(n, f) for n, f in sorted(globals().items())
               if n.startswith("test_") and callable(f)]
    fallos = []
    for nombre, fn in pruebas:
        try:
            fn()
            print(f"  ok   {nombre}")
        except Exception as e:
            print(f"  FALLA {nombre}: {type(e).__name__}: {e}")
            fallos.append(nombre)

    print(f"\n{len(pruebas) - len(fallos)}/{len(pruebas)} pruebas pasan")
    if fallos:
        print("Fallan: " + ", ".join(fallos))
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(_correr())
