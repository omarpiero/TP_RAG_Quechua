"""D-1 (clasificador lexica/prosa) y normalizacion declarada de la regla de lema (ADR-021)."""

import pytest

from domain.services.clasificador_consulta import ClasificadorConsulta
from domain.services.depurador_consulta import DepuradorConsulta


@pytest.mark.parametrize(
    "texto",
    [
        "¿cómo se dice computadora en quechua wanka?",
        "how do you say computer in Wanka Quechua?",
        "¿cómo se dice banco de peces?",
        "zorro",
        "Zorro",
        "water",
        "cuenta bancaria",
    ],
)
def test_consultas_lexicas(texto):
    assert ClasificadorConsulta().es_lexica(texto)


@pytest.mark.parametrize(
    "texto",
    [
        "¿qué función cumple el sufijo ablativo en la gramática?",
        "¿cuál es la estructura de la oración en quechua wanka?",
        "what is the role of the ablative suffix in the grammar?",
    ],
)
def test_preguntas_de_prosa(texto):
    assert not ClasificadorConsulta().es_lexica(texto)


def test_normalizacion_ignora_mayusculas_y_tildes():
    n = DepuradorConsulta.normalizar
    assert n("Zorro") == n("zorro") == n("ZORRO") == "zorro"
    assert n("cuánto") == n("CUANTO") == "cuanto"
    assert n("año") == "ano"


def test_depurar_extrae_el_termino_sin_importar_mayusculas_ni_signos():
    d = DepuradorConsulta()
    assert d.depurar("¿Cómo se dice Zorro en quechua wanka?") == d.depurar("zorro") == "zorro"
    assert d.depurar("¿cómo se dice banco de peces?") == "banco de peces"
