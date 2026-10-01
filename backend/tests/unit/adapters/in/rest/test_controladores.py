"""Controladores REST con TestClient y un contenedor de fakes de los PUERTOS DE ENTRADA.

Comprueban que las rutas, los codigos y los esquemas no cambiaron al partir api.py por
recurso, y que los controladores solo dependen de puertos.
"""

import ast
from datetime import date
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from application.ports import (
    ConsultarCorpusPort,
    ConsultarHistorialPort,
    EstadoCorpus,
    GestionarFuentesPort,
    ReindexarCorpusPort,
)
from domain.entities.consulta import Consulta
from domain.entities.fragmento import Fragmento, FragmentoRecuperado, TipoFragmento
from domain.entities.respuesta import Respuesta
from domain.value_objects.procedencia import Procedencia
from domain.value_objects.puntuacion_similitud import PuntuacionSimilitud

rest = import_module("adapters.in.rest")
DOCUMENTO = "293274822-diccionario-quechua-Wanka-docx.pdf"


def _zorro() -> FragmentoRecuperado:
    return FragmentoRecuperado(
        fragmento=Fragmento(
            id="zorro-37",
            texto="ZORRO: Atuq.",
            procedencia=Procedencia(DOCUMENTO, 37),
            tipo=TipoFragmento.LEXICOGRAFICO,
        ),
        puntuacion=PuntuacionSimilitud(0.6095),
        coincidencia_lema=True,
    )


class ConsultarFake(ConsultarCorpusPort):
    def ejecutar(self, texto_consulta):
        return Respuesta(
            consulta_id="c1", texto="ZORRO: Atuq.", respaldo=[_zorro()], similitud_maxima=0.6095
        )


class HistorialFake(ConsultarHistorialPort):
    def ejecutar(self, limite=50):
        r = Respuesta(consulta_id="c1", texto="ZORRO: Atuq.", respaldo=[_zorro()])
        return [(Consulta(texto="zorro"), r)]


class FuentesFake(GestionarFuentesPort):
    def __init__(self):
        self.datos = {}

    def registrar(self, fuente):
        self.datos[fuente.id] = fuente
        return fuente

    def obtener(self, fuente_id):
        return self.datos.get(fuente_id)

    def listar(self):
        return list(self.datos.values())

    def actualizar(self, fuente):
        if fuente.id not in self.datos:
            raise KeyError(fuente.id)
        self.datos[fuente.id] = fuente
        return fuente

    def eliminar(self, fuente_id):
        return self.datos.pop(fuente_id, None) is not None


class ReindexarFake(ReindexarCorpusPort):
    def ejecutar(self):
        return self.estado()

    def estado(self):
        return EstadoCorpus(documentos=[DOCUMENTO], total_fragmentos=3605)


def _cliente(con_base_datos=True) -> TestClient:
    app = FastAPI()
    for router in rest.routers:
        app.include_router(router)
    app.state.contenedor = SimpleNamespace(
        consultar_corpus=ConsultarFake(),
        consultar_historial=HistorialFake() if con_base_datos else None,
        gestionar_fuentes=FuentesFake() if con_base_datos else None,
        reindexar_corpus=ReindexarFake(),
        ingestar_documento=None,
        estado=lambda: {
            "fragmentos_indexados": 3605,
            "umbral_abstencion": 0.48,
            "generador_disponible": False,
            "base_datos_disponible": con_base_datos,
            "modelo": "qwen3.5:4b",
        },
    )
    return TestClient(app)


def test_las_rutas_son_las_mismas_de_antes_del_refactor():
    cliente = _cliente()
    rutas = {(m, r.path) for r in cliente.app.routes for m in getattr(r, "methods", set())}
    esperadas = {
        ("GET", "/api/estado"),
        ("POST", "/api/consultas"),
        ("GET", "/api/historial"),
        ("POST", "/api/corpus/documentos"),
        ("GET", "/api/corpus/documentos"),
        ("POST", "/api/corpus/reindexar"),
        ("POST", "/api/fuentes"),
        ("GET", "/api/fuentes"),
        ("GET", "/api/fuentes/{fuente_id}"),
        ("PUT", "/api/fuentes/{fuente_id}"),
        ("DELETE", "/api/fuentes/{fuente_id}"),
    }
    assert esperadas <= rutas


@pytest.mark.salvaguarda
def test_consulta_devuelve_forma_literal_con_documento_y_pagina():
    r = _cliente().post("/api/consultas", json={"texto": "¿cómo se dice zorro en quechua wanka?"})

    assert r.status_code == 200
    cuerpo = r.json()
    assert cuerpo["abstenida"] is False
    assert cuerpo["respaldo"][0]["texto"] == "ZORRO: Atuq."
    assert cuerpo["respaldo"][0]["documento"] == DOCUMENTO
    assert cuerpo["respaldo"][0]["pagina"] == 37
    campos = {
        "consulta_id",
        "texto",
        "abstenida",
        "idioma",
        "similitud_maxima",
        "aviso",
        "respaldo",
        "consulta_traducida",
        "pasajes",
    }
    assert campos <= set(cuerpo)


def test_consulta_vacia_es_422():
    assert _cliente().post("/api/consultas", json={"texto": ""}).status_code == 422


def test_historial_con_base_de_datos():
    r = _cliente().get("/api/historial")
    assert r.status_code == 200
    assert r.json()[0]["consulta"] == "zorro"


def test_historial_sin_base_de_datos_es_503():
    assert _cliente(con_base_datos=False).get("/api/historial").status_code == 503


def test_estado():
    r = _cliente().get("/api/estado")
    assert r.status_code == 200
    assert r.json()["umbral_abstencion"] == 0.48


def test_corpus_listar_y_reindexar():
    cliente = _cliente()
    esperado = {"documentos": [DOCUMENTO], "total_fragmentos": 3605}
    assert cliente.get("/api/corpus/documentos").json() == esperado
    reindexar = cliente.post("/api/corpus/reindexar")
    assert reindexar.status_code == 200
    assert reindexar.json() == esperado


def test_fuentes_crud_y_codigos():
    cliente = _cliente()
    cuerpo = {
        "titulo": "Diccionario",
        "entidad_publicadora": "Entidad",
        "licenciamiento": "Por registrar",
        "fecha_extraccion": date(2026, 10, 1).isoformat(),
        "nombre_archivo": DOCUMENTO,
    }
    creada = cliente.post("/api/fuentes", json=cuerpo)
    assert creada.status_code == 201
    fid = creada.json()["id"]
    assert cliente.get(f"/api/fuentes/{fid}").status_code == 200
    assert cliente.get("/api/fuentes/no-existe").status_code == 404
    assert cliente.put(f"/api/fuentes/{fid}", json=cuerpo).status_code == 200
    assert cliente.put("/api/fuentes/no-existe", json=cuerpo).status_code == 404
    assert cliente.post("/api/fuentes", json={**cuerpo, "licenciamiento": " "}).status_code == 422
    assert cliente.delete(f"/api/fuentes/{fid}").status_code == 204
    assert cliente.delete(f"/api/fuentes/{fid}").status_code == 404


def test_fuentes_sin_base_de_datos_es_503():
    assert _cliente(con_base_datos=False).get("/api/fuentes").status_code == 503


def test_ingesta_rechaza_lo_que_no_es_pdf():
    r = _cliente().post(
        "/api/corpus/documentos",
        files={"archivo": ("nota.txt", b"x", "text/plain")},
        data={"titulo": "t", "entidad_publicadora": "e", "licenciamiento": "l"},
    )
    assert r.status_code == 422


def test_los_controladores_solo_importan_puertos():
    """Ningun controlador importa casos de uso, adaptadores de salida ni infraestructura."""
    carpeta = Path(rest.__file__).parent
    prohibidos = ("application.use_cases", "adapters.out", "infrastructure")
    controladores = list(carpeta.glob("*_controller.py"))
    assert len(controladores) == 5
    for archivo in controladores:
        arbol = ast.parse(archivo.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.ImportFrom):
                nombres = [nodo.module or ""]
            elif isinstance(nodo, ast.Import):
                nombres = [a.name for a in nodo.names]
            else:
                continue
            for nombre in nombres:
                assert not nombre.startswith(prohibidos), (archivo.name, nombre)
