"""S13 · fase 2 (OWASP): token de administracion (ADR-035/036), limite de peticiones (ADR-037),
HSTS, CORS y contencion de rutas de la interfaz (OW-05)."""

import logging
from importlib import import_module
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from infrastructure.seguridad import OrigenDePruebasAutorizado
from infrastructure.seguridad_nube import (
    CabeceraHsts,
    EscrituraProtegida,
    LimitePeticiones,
    requiere_admin,
)

rest = import_module("adapters.in.rest")
TOKEN = "token-de-prueba-s13"  # valor de prueba generado para esta suite, no el real


class Reloj:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t


class Historial:
    borrados = 0

    def ejecutar(self, limite=50):
        return []

    def borrar(self):
        Historial.borrados += 1


class Fuentes:
    def listar(self):
        return []

    def eliminar(self, fuente_id):
        return True


class Consultar:
    def ejecutar(self, texto):
        raise RuntimeError("no debe llegar en estas pruebas")


class Predecir:
    def ejecutar(self, texto):
        return {"texto": texto}

    def modelos(self):
        return []


def _app(nube=True, token=TOKEN, limites=None, reloj=None, token_pruebas="") -> TestClient:
    app = FastAPI()
    for router in rest.routers:
        app.include_router(router)
    app.state.contenedor = SimpleNamespace(
        consultar_historial=Historial(),
        gestionar_fuentes=Fuentes(),
        predecir_consulta=Predecir(),
        consultar_corpus=Consultar(),
    )
    app.add_middleware(LimitePeticiones, limites=limites or {}, reloj=reloj or Reloj())
    app.add_middleware(EscrituraProtegida, activo=nube, token=token)
    app.add_middleware(OrigenDePruebasAutorizado, token=token_pruebas)
    app.add_middleware(CabeceraHsts, activo=nube)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://quechua-web.onrender.com"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "X-Admin-Token"],
    )
    return TestClient(app)


ESCRITURAS = [
    ("DELETE", "/api/historial"),
    ("POST", "/api/fuentes"),
    ("PUT", "/api/fuentes/abc"),
    ("DELETE", "/api/fuentes/abc"),
    ("POST", "/api/corpus/documentos"),
    ("POST", "/api/corpus/reindexar"),
]


@pytest.mark.parametrize(("metodo", "ruta"), ESCRITURAS + [("GET", "/api/historial")])
def test_en_la_nube_sin_token_es_401(metodo, ruta):
    r = _app().request(metodo, ruta)
    assert r.status_code == 401
    assert "X-Admin-Token" in r.json()["detail"]


@pytest.mark.parametrize(("metodo", "ruta"), ESCRITURAS)
def test_en_la_nube_con_token_incorrecto_es_403(metodo, ruta):
    assert _app().request(metodo, ruta, headers={"X-Admin-Token": "otro"}).status_code == 403


@pytest.mark.parametrize(("metodo", "ruta"), ESCRITURAS)
def test_en_la_nube_sin_admin_token_configurado_se_niega_siempre(metodo, ruta):
    cliente = _app(token="")
    assert cliente.request(metodo, ruta, headers={"X-Admin-Token": "x"}).status_code == 403


def test_con_token_correcto_pasa_al_controlador():
    cliente = _app()
    cabecera = {"X-Admin-Token": TOKEN}
    assert cliente.delete("/api/historial", headers=cabecera).status_code == 204
    assert cliente.get("/api/historial", headers=cabecera).status_code == 200
    assert cliente.delete("/api/fuentes/abc", headers=cabecera).status_code == 204
    # Un cuerpo invalido llega al controlador (422): el middleware ya autorizo.
    assert cliente.post("/api/fuentes", json={}, headers=cabecera).status_code == 422


def test_en_local_no_cambia_nada():
    cliente = _app(nube=False)
    assert cliente.delete("/api/historial").status_code == 204
    assert cliente.get("/api/historial").status_code == 200
    assert cliente.delete("/api/fuentes/abc").status_code == 204
    assert "strict-transport-security" not in cliente.get("/api/fuentes").headers


def test_lecturas_publicas_siguen_sin_token_en_la_nube():
    cliente = _app()
    assert cliente.get("/api/fuentes").status_code == 200
    assert cliente.post("/api/predicciones", json={"texto": "zorro"}).status_code == 200
    assert cliente.post("/api/consultas", json={"texto": ""}).status_code == 422  # no 401


@pytest.mark.parametrize(
    ("metodo", "ruta", "esperado"),
    [
        ("POST", "/api/consultas", False),
        ("POST", "/api/predicciones", False),
        ("GET", "/api/fuentes", False),
        ("GET", "/api/analitica/demanda", False),
        ("OPTIONS", "/api/fuentes", False),
        ("GET", "/api/historial", True),
        ("POST", "/api/nueva-ruta-de-escritura", True),  # protegida por defecto
        ("PATCH", "/api/fuentes/x", True),
        ("POST", "/docs", False),
    ],
)
def test_proteccion_por_defecto(metodo, ruta, esperado):
    assert requiere_admin(metodo, ruta) is esperado


def test_el_token_no_aparece_en_la_bitacora(caplog):
    with caplog.at_level(logging.INFO, logger="rag.seguridad"):
        cliente = _app()
        cliente.delete("/api/historial", headers={"X-Admin-Token": TOKEN})
        cliente.delete("/api/historial", headers={"X-Admin-Token": "intento-malo"})
    texto = caplog.text
    assert "autorizada DELETE /api/historial" in texto
    assert "rechazada 403" in texto
    assert TOKEN not in texto and "intento-malo" not in texto
    assert "testclient" not in texto  # la IP/host del cliente va seudonimizada


def test_limite_de_peticiones_429_con_retry_after():
    reloj = Reloj()
    cliente = _app(limites={"/api/predicciones": 3}, reloj=reloj)
    codigos = [cliente.post("/api/predicciones", json={"texto": "a"}).status_code for _ in range(4)]
    assert codigos == [200, 200, 200, 429]
    r = cliente.post("/api/predicciones", json={"texto": "a"})
    assert r.status_code == 429
    assert int(r.headers["retry-after"]) > 0
    assert "límite es 3 por minuto" in r.json()["detail"]
    # Otra IP no se ve afectada.
    otra_ip = {"CF-Connecting-IP": "9.9.9.9"}
    otra = cliente.post("/api/predicciones", json={"texto": "a"}, headers=otra_ip)
    assert otra.status_code == 200
    # Pasado el minuto, la ventana se libera.
    reloj.t += 61
    assert cliente.post("/api/predicciones", json={"texto": "a"}).status_code == 200


def test_el_token_de_pruebas_valido_queda_exento_del_limite():
    cliente = _app(limites={"/api/predicciones": 1}, token_pruebas="tp")
    cab = {"X-Token-Pruebas": "tp", "X-Origen-Consultas": "humo"}
    assert all(
        cliente.post("/api/predicciones", json={"texto": "a"}, headers=cab).status_code == 200
        for _ in range(5)
    )


def test_429_y_401_llevan_cors_para_que_el_navegador_lea_el_mensaje():
    cliente = _app(limites={"/api/predicciones": 1})
    origen = {"Origin": "https://quechua-web.onrender.com"}
    cliente.post("/api/predicciones", json={"texto": "a"}, headers=origen)
    r = cliente.post("/api/predicciones", json={"texto": "a"}, headers=origen)
    assert r.status_code == 429
    assert r.headers["access-control-allow-origin"] == "https://quechua-web.onrender.com"
    r = cliente.delete("/api/historial", headers=origen)
    assert r.status_code == 401
    assert r.headers["access-control-allow-origin"] == "https://quechua-web.onrender.com"


def test_hsts_solo_en_la_nube():
    assert "max-age=31536000" in _app().get("/api/fuentes").headers["strict-transport-security"]


def test_cors_no_admite_credenciales_ni_origen_ajeno():
    cliente = _app()
    ajeno = cliente.options(
        "/api/historial",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "DELETE"},
    )
    assert ajeno.status_code == 400
    assert "access-control-allow-origin" not in ajeno.headers
    propio = cliente.options(
        "/api/fuentes",
        headers={
            "Origin": "https://quechua-web.onrender.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "x-admin-token",
        },
    )
    assert propio.status_code == 200
    assert "access-control-allow-credentials" not in propio.headers


# ---------------- OW-05: contencion de rutas al servir la interfaz ----------------


def test_resolver_recurso_no_sale_de_la_carpeta(tmp_path):
    from infrastructure.main import resolver_recurso_interfaz

    interfaz = tmp_path / "interfaz"
    (interfaz / "assets").mkdir(parents=True)
    (interfaz / "index.html").write_text("<html>ok</html>")
    (interfaz / "assets" / "app.js").write_text("js")
    (tmp_path / "secreto.txt").write_text("NO")
    indice = (interfaz / "index.html").resolve()

    legitimo = (interfaz / "assets/app.js").resolve()
    assert resolver_recurso_interfaz(interfaz, "assets/app.js") == legitimo
    for malicioso in ["../secreto.txt", "assets/../../secreto.txt", str(tmp_path / "secreto.txt")]:
        assert resolver_recurso_interfaz(interfaz, malicioso) == indice
    assert resolver_recurso_interfaz(interfaz, "ruta/del/cliente") == indice
