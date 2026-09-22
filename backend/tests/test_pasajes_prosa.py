"""Pruebas del tercer estado de respuesta: pasajes de prosa sin confirmar.

La similitud lexica no distingue una pregunta de gramatica cubierta de una que no lo esta,
de modo que el sistema no afirma nada sobre prosa: entrega el pasaje literal y citado.
"""

import pytest

from application.services.evaluador_confianza import PISO_PASAJES, EvaluadorConfianza
from domain.entities.fragmento import Fragmento, FragmentoRecuperado, TipoFragmento
from domain.value_objects.procedencia import Procedencia
from domain.entities.respuesta import Respuesta
from domain.value_objects.puntuacion_similitud import PuntuacionSimilitud


def _recuperado(puntuacion: float) -> FragmentoRecuperado:
    return FragmentoRecuperado(
        fragmento=Fragmento(
            id="p1",
            texto="Los plurales de los pronombres se forman con kuna.",
            procedencia=Procedencia(documento="gramatica.pdf", pagina=94),
            tipo=TipoFragmento.PROSA,
        ),
        puntuacion=PuntuacionSimilitud(puntuacion),
    )


def test_los_pasajes_por_debajo_del_piso_no_se_ofrecen():
    evaluador = EvaluadorConfianza()
    assert evaluador.ofrecer_pasajes([_recuperado(PISO_PASAJES - 0.01)]) == []


def test_los_pasajes_por_encima_del_piso_se_ofrecen():
    evaluador = EvaluadorConfianza()
    assert len(evaluador.ofrecer_pasajes([_recuperado(PISO_PASAJES + 0.01)])) == 1


def test_el_piso_no_autoriza_a_responder():
    """Ofrecer un pasaje y responder son decisiones distintas.

    El piso solo evita mostrar ruido; la unica puerta que autoriza una afirmacion sigue
    siendo el umbral calibrado."""
    evaluador = EvaluadorConfianza()
    veredicto = evaluador.evaluar([_recuperado(PISO_PASAJES + 0.05)])
    assert not veredicto.responder


def test_los_pasajes_no_pueden_acompanar_a_una_afirmacion():
    """Entregarlos junto a una respuesta afirmativa los presentaria como su respaldo."""
    with pytest.raises(ValueError, match="abstenida"):
        Respuesta(
            consulta_id="x",
            texto="El plural se forma con kuna.",
            abstenida=False,
            respaldo=[_recuperado(0.9)],
            pasajes=[_recuperado(0.3)],
        )


def test_una_abstencion_con_pasajes_sigue_siendo_una_abstencion():
    respuesta = Respuesta(
        consulta_id="x",
        texto="No tengo una respuesta confirmada.",
        abstenida=True,
        pasajes=[_recuperado(0.35)],
    )
    assert respuesta.abstenida
    assert respuesta.tiene_pasajes
    assert respuesta.respaldo == []


def test_hace_falta_compartir_dos_palabras_de_contenido():
    """Con una sola bastaba un termino suelto para sacar un pasaje cualquiera.

    "cual es la capital de Francia" compartia *capital* con un pasaje de la gramatica y
    lo mostraba; exigir dos palabras lo descarta sin perder los casos legitimos, donde la
    consulta comparte tanto el termino como su categoria ("sufijo" y "ablativo")."""
    evaluador = EvaluadorConfianza()
    pasaje = _recuperado(0.30)

    assert evaluador.ofrecer_pasajes([pasaje], consulta="capital Francia") == []
    assert len(evaluador.ofrecer_pasajes([pasaje], consulta="plurales pronombres")) == 1


def test_una_consulta_de_una_sola_palabra_no_puede_compartir_dos():
    evaluador = EvaluadorConfianza()
    assert len(evaluador.ofrecer_pasajes([_recuperado(0.30)], consulta="plurales")) == 1
