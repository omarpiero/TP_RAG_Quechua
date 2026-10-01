"""Reglas de respuesta del PR-03: via de respaldo (ADR-021), D-1 (consulta lexica sin pasajes)
y D-6 (generador caido -> fragmento literal). Solo fakes; formas del corpus verificadas
(ZORRO: Atuq., pag. 37)."""

from pathlib import Path

import pytest

from application.ports.out.generador_texto_port import GeneradorNoDisponible, GeneradorTextoPort
from application.ports.out.indice_recuperacion_port import IndiceRecuperacionPort
from application.use_cases.consultar_corpus import AVISO_GENERACION, ConsultarCorpusUseCase
from domain.entities.fragmento import Fragmento, FragmentoRecuperado, TipoFragmento
from domain.services.evaluador_confianza import EvaluadorConfianza
from domain.value_objects.procedencia import Procedencia
from domain.value_objects.puntuacion_similitud import PuntuacionSimilitud
from infrastructure.config import configuracion
from tests.unit.application.test_consultar_corpus_con_fakes import (
    DOCUMENTO,
    DetectorFake,
    GeneradorFake,
    RepositorioFake,
)

TAU = configuracion.umbral_abstencion


def _rec(id_, texto, pagina, puntuacion, lema=False, tipo=TipoFragmento.LEXICOGRAFICO):
    return FragmentoRecuperado(
        fragmento=Fragmento(
            id=id_, texto=texto, procedencia=Procedencia(DOCUMENTO, pagina), tipo=tipo
        ),
        puntuacion=PuntuacionSimilitud(puntuacion),
        coincidencia_lema=lema,
    )


class IndiceConPasajes(IndiceRecuperacionPort):
    def __init__(self, recuperados, prosa=()):
        self._recuperados, self._prosa = list(recuperados), list(prosa)

    def indexar(self, fragmentos):
        return len(fragmentos)

    def recuperar(self, consulta, k=5):
        return self._recuperados

    def recuperar_prosa(self, consulta, k=3):
        return self._prosa

    def total_indexado(self):
        return 1

    def es_lema(self, termino):
        return False


class GeneradorCaido(GeneradorTextoPort):
    def redactar(self, consulta, fragmentos, idioma):
        raise GeneradorNoDisponible("ConnectError: sin servicio")

    def disponible(self):
        return False


def _caso(indice, generador=None):
    return ConsultarCorpusUseCase(
        indice=indice,
        generador=generador or GeneradorFake(),
        evaluador=EvaluadorConfianza(TAU),
        detector_idioma=DetectorFake(),
        repositorio=RepositorioFake(),
    )


ZORRO_LEMA = _rec("zorro-37", "ZORRO: Atuq.", 37, 0.30, lema=True)
OTRO = _rec("otro", "CÓNCAVO: Puklu.", 9, 0.20)
PASAJE = _rec(
    "prosa-1",
    "El sufijo ablativo indica el origen del movimiento en la gramatica.",
    12,
    0.30,
    tipo=TipoFragmento.PROSA,
)


@pytest.mark.salvaguarda
def test_via_similitud_cuando_sim_max_alcanza_tau():
    respuesta = _caso(
        IndiceConPasajes([_rec("zorro-37", "ZORRO: Atuq.", 37, 0.61, lema=True)])
    ).ejecutar("zorro")
    assert respuesta.via_respaldo == "similitud"
    assert respuesta.umbral == TAU
    assert respuesta.generador_invocado is True
    assert respuesta.latencia_ms >= 0


@pytest.mark.salvaguarda
def test_via_lema_si_sim_max_menor_que_tau_y_el_generador_recibe_solo_entradas_de_lema():
    generador = GeneradorFake()
    respuesta = _caso(IndiceConPasajes([OTRO, ZORRO_LEMA]), generador).ejecutar("zorro")

    assert respuesta.via_respaldo == "lema"
    assert [r.id for r in respuesta.respaldo] == ["zorro-37"]
    assert not respuesta.abstenida


@pytest.mark.salvaguarda
def test_sin_lema_y_bajo_tau_se_abstiene_sin_via():
    generador = GeneradorFake()
    respuesta = _caso(IndiceConPasajes([OTRO]), generador).ejecutar("zorro")
    assert respuesta.abstenida
    assert respuesta.via_respaldo is None
    assert generador.invocaciones == 0
    assert respuesta.generador_invocado is False


@pytest.mark.salvaguarda
def test_d1_consulta_lexica_no_recibe_pasajes_de_prosa():
    caso = _caso(IndiceConPasajes([OTRO], prosa=[PASAJE]))
    respuesta = caso.ejecutar("¿cómo se dice sufijo ablativo en quechua wanka?")
    assert respuesta.abstenida
    assert respuesta.pasajes == []


@pytest.mark.salvaguarda
def test_d1_la_pregunta_de_prosa_si_recibe_pasajes_rotulados_como_abstencion():
    caso = _caso(IndiceConPasajes([OTRO], prosa=[PASAJE]))
    respuesta = caso.ejecutar("¿qué función cumple el sufijo ablativo en la gramática?")
    assert respuesta.abstenida
    assert [p.id for p in respuesta.pasajes] == ["prosa-1"]


@pytest.mark.salvaguarda
def test_d6_generador_caido_devuelve_el_fragmento_literal_citado_sin_error(caplog):
    import logging

    with caplog.at_level(logging.INFO, logger="rag"):
        respuesta = _caso(
            IndiceConPasajes([_rec("zorro-37", "ZORRO: Atuq.", 37, 0.61, lema=True)]),
            GeneradorCaido(),
        ).ejecutar("zorro")

    assert not respuesta.abstenida
    assert respuesta.texto == f"ZORRO: Atuq. ({DOCUMENTO}, p. 37)"
    assert respuesta.aviso_generacion == AVISO_GENERACION
    assert respuesta.citas == [f"{DOCUMENTO}, p. 37"]
    assert any(
        "[GENERADOR] fallo" in r.getMessage() and "plantilla literal" in r.getMessage()
        for r in caplog.records
    )


def test_ollama_envuelve_los_errores_de_red_en_generador_no_disponible():
    from adapters.out.generacion.ollama_generador import OllamaGenerador

    generador = OllamaGenerador(url_base="http://127.0.0.1:1", modelo="m")
    with pytest.raises(GeneradorNoDisponible):
        generador.redactar(
            "zorro",
            [ZORRO_LEMA],
            __import__("domain.value_objects.idioma", fromlist=["Idioma"]).Idioma.ESPANOL,
        )


@pytest.mark.salvaguarda
def test_tau_tiene_un_unico_origen_la_configuracion():
    assert TAU == 0.48
    assert EvaluadorConfianza.__init__.__defaults__ is None  # sin valor por defecto
    src = Path(__file__).resolve().parents[3] / "src"
    for carpeta in ("domain", "application"):
        for archivo in (src / carpeta).rglob("*.py"):
            texto = archivo.read_text(encoding="utf-8")
            assert "UMBRAL_CALIBRADO" not in texto, archivo
            assert "0.48" not in texto and "0,48" not in texto, archivo


@pytest.mark.datos
@pytest.mark.salvaguarda
def test_d1_y_banco_de_peces_con_el_corpus_real(indice):
    """Con el indice real: «computadora» se abstiene sin pasajes; «banco de peces» no
    responde por el lema «banco»."""
    from adapters.out.idioma.detector_idioma_heuristico import DetectorIdiomaHeuristico
    from adapters.out.traduccion.traductor_tabla import TraductorTabla

    class GeneradorLanza(GeneradorFake):
        def redactar(self, *a):
            raise AssertionError("el generador no debe invocarse sin respaldo")

    caso = ConsultarCorpusUseCase(
        indice=indice,
        generador=GeneradorLanza(),
        evaluador=EvaluadorConfianza(TAU),
        detector_idioma=DetectorIdiomaHeuristico(),
        traductor=TraductorTabla(configuracion.ruta_tabla_traduccion),
    )
    computadora = caso.ejecutar("¿cómo se dice computadora en quechua wanka?")
    assert computadora.abstenida and computadora.pasajes == []

    assert not any(
        r.coincidencia_lema for r in indice.recuperar("¿cómo se dice banco de peces?", k=5)
    )
