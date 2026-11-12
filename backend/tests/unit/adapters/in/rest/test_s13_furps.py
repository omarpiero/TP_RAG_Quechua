"""S13 · fase 1 (FURPS+): ruta de vida sin base (M-02, REF-01) y parametros acotados
(M-04, R-04)."""

from importlib import import_module
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

rest = import_module("adapters.in.rest")


class HistorialFake:
    def __init__(self):
        self.limites = []

    def ejecutar(self, limite=50):
        self.limites.append(limite)
        return []

    def borrar(self):
        pass


class DemandaFake:
    def ejecutar(self, top=15, incluir_sinteticas=False):
        return {"suficiente": True, "prioridades": []}


class ContenedorQueNoDebeUsarse:
    """`/api/vivo` no debe tocar el contenedor: ni la base ni el generador."""

    def __getattr__(self, nombre):
        raise AssertionError(f"/api/vivo no debe acceder a contenedor.{nombre}")


def _app(contenedor) -> TestClient:
    app = FastAPI()
    for router in rest.routers:
        app.include_router(router)
    app.state.contenedor = contenedor
    return TestClient(app)


def test_vivo_responde_sin_tocar_base_ni_generador():
    r = _app(ContenedorQueNoDebeUsarse()).get("/api/vivo")
    assert r.status_code == 200
    assert r.json() == {"vivo": True}


@pytest.mark.parametrize("limite", ["-1", "0", "501", "abc"])
def test_limite_del_historial_fuera_de_rango_es_422(limite):
    historial = HistorialFake()
    cliente = _app(SimpleNamespace(consultar_historial=historial))
    assert cliente.get(f"/api/historial?limite={limite}").status_code == 422
    assert historial.limites == []  # no llega a la base


@pytest.mark.parametrize(
    ("consulta", "esperado"), [("", 50), ("?limite=1", 1), ("?limite=500", 500)]
)
def test_limite_del_historial_valido_conserva_el_comportamiento(consulta, esperado):
    historial = HistorialFake()
    cliente = _app(SimpleNamespace(consultar_historial=historial))
    assert cliente.get(f"/api/historial{consulta}").status_code == 200
    assert historial.limites == [esperado]


@pytest.mark.parametrize(
    ("top", "codigo"), [("0", 422), ("-3", 422), ("101", 422), ("1", 200), ("100", 200)]
)
def test_top_de_la_demanda_acotado(top, codigo):
    cliente = _app(SimpleNamespace(analizar_demanda=DemandaFake()))
    assert cliente.get(f"/api/analitica/demanda?top={top}").status_code == codigo
