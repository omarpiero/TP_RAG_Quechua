"""Caso de uso de consulta con dobles de TODOS los puertos de salida (G-11).

No hay base de datos, Ollama ni indice real: el nucleo se prueba solo con fakes. Las
formas de ejemplo son las verificadas del corpus (ZORRO: Atuq., pag. 37 del diccionario).
"""

import logging

import pytest

from application.ports import ConsultarCorpusPort
from application.ports.out.detector_idioma_port import DetectorIdiomaPort
from application.ports.out.generador_texto_port import GeneradorTextoPort
from application.ports.out.indice_recuperacion_port import IndiceRecuperacionPort
from application.ports.out.repositorio_consultas_port import RepositorioConsultasPort
from application.ports.out.traductor_port import TraductorPort
from application.use_cases.consultar_corpus import ConsultarCorpusUseCase
from domain.entities.fragmento import Fragmento, FragmentoRecuperado, TipoFragmento
from domain.services.evaluador_confianza import EvaluadorConfianza
from domain.value_objects.idioma import Idioma
from domain.value_objects.procedencia import Procedencia
from domain.value_objects.puntuacion_similitud import PuntuacionSimilitud

DOCUMENTO = "293274822-diccionario-quechua-Wanka-docx.pdf"


def _recuperado(puntuacion: float, lema: bool = False) -> FragmentoRecuperado:
    return FragmentoRecuperado(
        fragmento=Fragmento(
            id="zorro-37",
            texto="ZORRO: Atuq.",
            procedencia=Procedencia(DOCUMENTO, 37),
            tipo=TipoFragmento.LEXICOGRAFICO,
        ),
        puntuacion=PuntuacionSimilitud(puntuacion),
        coincidencia_lema=lema,
    )


class IndiceFake(IndiceRecuperacionPort):
    def __init__(self, puntuacion: float, lema: bool = False):
        self._p, self._lema = puntuacion, lema

    def indexar(self, fragmentos):
        return len(fragmentos)

    def recuperar(self, consulta, k=5):
        return [_recuperado(self._p, self._lema)]

    def total_indexado(self):
        return 1

    def es_lema(self, termino):
        return False


class GeneradorFake(GeneradorTextoPort):
    def __init__(self):
        self.invocaciones = 0

    def redactar(self, consulta, fragmentos, idioma):
        self.invocaciones += 1
        return fragmentos[0].texto

    def disponible(self):
        return True


class DetectorFake(DetectorIdiomaPort):
    def detectar(self, texto):
        return Idioma.ESPANOL


class TraductorFake(TraductorPort):
    def traducir_al_espanol(self, texto):
        return texto

    def candidatas(self, termino, aproximar=False):
        return []


class RepositorioFake(RepositorioConsultasPort):
    def __init__(self):
        self.registros = []

    def registrar(self, consulta, respuesta):
        self.registros.append((consulta, respuesta))

    def historial(self, limite=50):
        return self.registros[:limite]

    def no_cubiertas(self, limite=500):
        return [c for c, r in self.registros if r.abstenida]

    def borrar_todo(self):
        n = len(self.registros)
        self.registros.clear()
        return n

    def total_registradas(self):
        return len(self.registros)


def _caso(puntuacion: float, lema: bool = False):
    generador, repo = GeneradorFake(), RepositorioFake()
    caso = ConsultarCorpusUseCase(
        indice=IndiceFake(puntuacion, lema),
        generador=generador,
        evaluador=EvaluadorConfianza(umbral=0.48),
        detector_idioma=DetectorFake(),
        repositorio=repo,
        traductor=TraductorFake(),
    )
    return caso, generador, repo


def test_el_caso_de_uso_implementa_el_puerto_de_entrada():
    caso, _, _ = _caso(0.9)
    assert isinstance(caso, ConsultarCorpusPort)


def test_con_respaldo_cita_documento_y_pagina_e_invoca_al_generador():
    caso, generador, repo = _caso(0.61)
    respuesta = caso.ejecutar("¿cómo se dice zorro en quechua wanka?")

    assert not respuesta.abstenida
    assert respuesta.texto == "ZORRO: Atuq."
    assert respuesta.citas == [f"{DOCUMENTO}, p. 37"]
    assert generador.invocaciones == 1
    assert len(repo.registros) == 1


@pytest.mark.salvaguarda
def test_sin_respaldo_el_generador_no_se_invoca_y_se_declara_la_ausencia():
    caso, generador, repo = _caso(0.20)
    respuesta = caso.ejecutar("¿cómo se dice zorro en quechua wanka?")

    assert respuesta.abstenida
    assert respuesta.respaldo == []
    assert generador.invocaciones == 0
    assert repo.registros[0][1].abstenida


@pytest.mark.salvaguarda
def test_la_coincidencia_de_lema_da_respaldo_aunque_la_similitud_sea_menor_que_tau():
    caso, generador, _ = _caso(0.30, lema=True)
    respuesta = caso.ejecutar("zorro")

    assert not respuesta.abstenida
    assert generador.invocaciones == 1


def test_el_log_recorre_las_capas_en_orden_y_no_incluye_texto_de_fragmentos(caplog):
    caso, _, _ = _caso(0.61)
    with caplog.at_level(logging.INFO, logger="rag"):
        caso.ejecutar("¿cómo se dice zorro en quechua wanka?")

    lineas = [r.getMessage() for r in caplog.records]
    orden = ["[CASO-USO]", "[INDICE]", "[EVALUADOR]", "[GENERADOR] invocado", "[REPOSITORIO]"]
    posiciones = [next(i for i, linea in enumerate(lineas) if linea.startswith(p)) for p in orden]
    assert posiciones == sorted(posiciones)
    assert "Atuq" not in "\n".join(lineas)


def test_el_log_declara_que_el_generador_no_se_invoco(caplog):
    caso, _, _ = _caso(0.20)
    with caplog.at_level(logging.INFO, logger="rag"):
        caso.ejecutar("¿cómo se dice zorro en quechua wanka?")

    lineas = [r.getMessage() for r in caplog.records]
    assert "[GENERADOR] NO invocado (sin respaldo)" in lineas
