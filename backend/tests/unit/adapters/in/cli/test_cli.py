"""CLI: `consultar` e `indexar` hablan solo con los puertos de entrada."""

import io
from importlib import import_module

import pytest

from application.ports import ConsultarCorpusPort, EstadoCorpus, ReindexarCorpusPort
from domain.entities.fragmento import Fragmento, FragmentoRecuperado, TipoFragmento
from domain.entities.respuesta import Respuesta
from domain.value_objects.procedencia import Procedencia
from domain.value_objects.puntuacion_similitud import PuntuacionSimilitud

comandos = import_module("adapters.in.cli.comandos")
DOCUMENTO = "293274822-diccionario-quechua-Wanka-docx.pdf"
CONSULTA = "¿cómo se dice zorro en quechua wanka?"


class ConsultarFake(ConsultarCorpusPort):
    def ejecutar(self, texto_consulta):
        zorro = FragmentoRecuperado(
            fragmento=Fragmento(
                id="zorro-37",
                texto="ZORRO: Atuq.",
                procedencia=Procedencia(DOCUMENTO, 37),
                tipo=TipoFragmento.LEXICOGRAFICO,
            ),
            puntuacion=PuntuacionSimilitud(0.6095),
            coincidencia_lema=True,
        )
        return Respuesta(consulta_id="c1", texto="ZORRO: Atuq.", respaldo=[zorro])


class ReindexarFake(ReindexarCorpusPort):
    def ejecutar(self):
        return self.estado()

    def estado(self):
        return EstadoCorpus(documentos=[DOCUMENTO], total_fragmentos=3605)


def test_consultar_imprime_forma_literal_documento_y_pagina():
    salida = io.StringIO()
    assert comandos.consultar(ConsultarFake(), CONSULTA, salida) == 0
    texto = salida.getvalue()
    assert "ZORRO: Atuq." in texto
    assert f"{DOCUMENTO}, p. 37" in texto


def test_indexar_informa_el_total():
    salida = io.StringIO()
    assert comandos.indexar(ReindexarFake(), salida) == 0
    assert "3605 fragmentos" in salida.getvalue()


@pytest.mark.datos
@pytest.mark.salvaguarda
def test_cli_responde_zorro_con_el_corpus_real_y_sin_ollama(indice):
    """Mismo caso de uso real que usa la API, con el corpus de datos y sin Ollama."""
    from adapters.out.generacion.generador_literal import GeneradorLiteral
    from adapters.out.idioma.detector_idioma_heuristico import DetectorIdiomaHeuristico
    from adapters.out.traduccion.traductor_tabla import TraductorTabla
    from application.use_cases.consultar_corpus import ConsultarCorpusUseCase
    from domain.services.evaluador_confianza import EvaluadorConfianza
    from infrastructure.config import configuracion

    caso = ConsultarCorpusUseCase(
        indice=indice,
        generador=GeneradorLiteral(),
        evaluador=EvaluadorConfianza(umbral=configuracion.umbral_abstencion),
        detector_idioma=DetectorIdiomaHeuristico(),
        traductor=TraductorTabla(configuracion.ruta_tabla_traduccion),
    )
    salida = io.StringIO()
    comandos.consultar(caso, CONSULTA, salida)
    texto = salida.getvalue()
    assert "ZORRO: Atuq." in texto
    assert "p. 37" in texto
