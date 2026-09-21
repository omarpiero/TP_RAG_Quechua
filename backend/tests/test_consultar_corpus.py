"""Pruebas del caso de uso con dobles de los puertos.

Ninguna toca Ollama, PostgreSQL ni el indice real: esa independencia es exactamente lo que
justifica la arquitectura hexagonal y permite verificar la regla de abstencion sin
depender de que haya un modelo cargado.
"""

import pytest

from application.services.evaluador_confianza import EvaluadorConfianza
from application.use_cases.consultar_corpus import ConsultarCorpusUseCase
from domain.entities.fragmento import Fragmento, FragmentoRecuperado, TipoFragmento
from domain.ports.detector_idioma_port import DetectorIdiomaPort
from domain.ports.generador_texto_port import GeneradorTextoPort
from domain.ports.indice_recuperacion_port import IndiceRecuperacionPort
from domain.ports.repositorio_consultas_port import RepositorioConsultasPort
from domain.value_objects.idioma import Idioma
from domain.value_objects.procedencia import Procedencia
from domain.value_objects.puntuacion_similitud import PuntuacionSimilitud


def _fragmento(texto="PERRO: Allqu.", pagina=27):
    return Fragmento(
        id="f1",
        texto=texto,
        procedencia=Procedencia("diccionario.pdf", pagina),
        tipo=TipoFragmento.LEXICOGRAFICO,
    )


class IndiceFalso(IndiceRecuperacionPort):
    def __init__(self, puntuacion=0.9, lema=False):
        self._puntuacion = puntuacion
        self._lema = lema

    def indexar(self, fragmentos):
        return len(fragmentos)

    def recuperar(self, consulta, k=5):
        return [
            FragmentoRecuperado(
                fragmento=_fragmento(),
                puntuacion=PuntuacionSimilitud(self._puntuacion),
                coincidencia_lema=self._lema,
            )
        ]

    def total_indexado(self):
        return 1


class GeneradorFalso(GeneradorTextoPort):
    def __init__(self):
        self.invocaciones = 0

    def redactar(self, consulta, fragmentos, idioma):
        self.invocaciones += 1
        return "En quechua wanka, perro se dice Allqu."

    def disponible(self):
        return True


class DetectorFalso(DetectorIdiomaPort):
    def __init__(self, idioma=Idioma.ESPANOL):
        self._idioma = idioma

    def detectar(self, texto):
        return self._idioma


class RepositorioFalso(RepositorioConsultasPort):
    def __init__(self):
        self.registros = []

    def registrar(self, consulta, respuesta):
        self.registros.append((consulta, respuesta))

    def historial(self, limite=50):
        return self.registros

    def no_cubiertas(self, limite=500):
        return [c for c, r in self.registros if r.abstenida]

    def total_registradas(self):
        return len(self.registros)


def _caso_uso(indice, generador, repositorio=None, idioma=Idioma.ESPANOL):
    return ConsultarCorpusUseCase(
        indice=indice,
        generador=generador,
        evaluador=EvaluadorConfianza(),
        detector_idioma=DetectorFalso(idioma),
        repositorio=repositorio,
    )


def test_consulta_con_respaldo_cita_documento_y_pagina():
    generador = GeneradorFalso()
    respuesta = _caso_uso(IndiceFalso(puntuacion=0.9), generador).ejecutar("perro")

    assert not respuesta.abstenida
    assert respuesta.respaldo
    assert respuesta.citas == ["diccionario.pdf, p. 27"]
    assert generador.invocaciones == 1


def test_la_abstencion_no_invoca_al_generador():
    """El orden del caso de uso importa: si el modelo no llega a ejecutarse, no tiene
    ocasion de inventar una forma."""
    generador = GeneradorFalso()
    respuesta = _caso_uso(IndiceFalso(puntuacion=0.10), generador).ejecutar("criptomoneda")

    assert respuesta.abstenida
    assert respuesta.respaldo == []
    assert generador.invocaciones == 0


def test_la_coincidencia_de_lema_responde_pese_a_similitud_baja():
    generador = GeneradorFalso()
    respuesta = _caso_uso(IndiceFalso(puntuacion=0.27, lema=True), generador).ejecutar("perro")

    assert not respuesta.abstenida
    assert generador.invocaciones == 1


def test_idioma_no_soportado_se_rechaza_sin_recuperar():
    generador = GeneradorFalso()
    respuesta = _caso_uso(
        IndiceFalso(), generador, idioma=Idioma.NO_SOPORTADO
    ).ejecutar("comment dit-on chien")

    assert respuesta.abstenida
    assert generador.invocaciones == 0


def test_toda_consulta_queda_registrada_incluida_la_abstenida():
    repositorio = RepositorioFalso()
    _caso_uso(IndiceFalso(puntuacion=0.10), GeneradorFalso(), repositorio).ejecutar("x")
    _caso_uso(IndiceFalso(puntuacion=0.90), GeneradorFalso(), repositorio).ejecutar("perro")

    assert repositorio.total_registradas() == 2
    # Las no cubiertas son el insumo de los modelos predictivos del PMV2.
    assert len(repositorio.no_cubiertas()) == 1


class IndiceSensibleAlIdioma(IndiceRecuperacionPort):
    """Devuelve una puntuacion baja para la consulta en ingles y alta para su traduccion,
    que es el comportamiento medido sobre el corpus real."""

    def indexar(self, fragmentos):
        return 1

    def recuperar(self, consulta, k=5):
        puntuacion = 0.85 if "zorro" in consulta.lower() else 0.12
        return [
            FragmentoRecuperado(
                fragmento=_fragmento("ZORRO: Atuq.", pagina=37),
                puntuacion=PuntuacionSimilitud(puntuacion),
            )
        ]

    def total_indexado(self):
        return 1


class TraductorFalso:
    def __init__(self, traduccion="zorro"):
        self._traduccion = traduccion
        self.invocaciones = 0

    def traducir_al_espanol(self, texto):
        self.invocaciones += 1
        return self._traduccion


def test_la_traduccion_previa_rescata_la_consulta_en_ingles():
    traductor = TraductorFalso("zorro")
    generador = GeneradorFalso()
    caso_uso = ConsultarCorpusUseCase(
        indice=IndiceSensibleAlIdioma(),
        generador=generador,
        evaluador=EvaluadorConfianza(),
        detector_idioma=DetectorFalso(Idioma.INGLES),
        traductor=traductor,
    )

    respuesta = caso_uso.ejecutar("how do you say fox in Wanka Quechua?")

    assert traductor.invocaciones == 1
    assert not respuesta.abstenida
    # Se conserva la mejor de las dos puntuaciones, no la de la consulta original.
    assert respuesta.similitud_maxima == pytest.approx(0.85)
    # La traduccion queda registrada: el usuario puede ver con que terminos se busco.
    assert respuesta.consulta_traducida == "zorro"


def test_una_traduccion_inutil_no_empeora_el_resultado():
    """Si el traductor falla o devuelve algo irrelevante, el sistema debe comportarse como
    si no hubiera traducido, nunca peor."""
    caso_uso = ConsultarCorpusUseCase(
        indice=IndiceSensibleAlIdioma(),
        generador=GeneradorFalso(),
        evaluador=EvaluadorConfianza(),
        detector_idioma=DetectorFalso(Idioma.INGLES),
        traductor=TraductorFalso("disparate"),
    )

    respuesta = caso_uso.ejecutar("how do you say fox in Wanka Quechua?")

    assert respuesta.abstenida
    assert respuesta.similitud_maxima == pytest.approx(0.12)


def test_una_respuesta_no_abstenida_exige_respaldo():
    from domain.entities.respuesta import Respuesta

    with pytest.raises(ValueError):
        Respuesta(consulta_id="c1", texto="inventada", respaldo=[], abstenida=False)
