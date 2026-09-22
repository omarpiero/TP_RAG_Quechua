"""Pruebas del traductor por tabla, con las trampas que la hicieron fallar."""

from pathlib import Path

import pytest

from infrastructure.adapters.output.traductor_tabla import TraductorTabla

RAIZ = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def traductor() -> TraductorTabla:
    return TraductorTabla(RAIZ / "data" / "traduccion_en_es.json")


def test_una_palabra_inglesa_suelta_se_resuelve(traductor):
    assert "amor" in traductor.candidatas("love")
    assert "perro" in traductor.candidatas("dog")


def test_devuelve_todas_las_lecturas_y_no_solo_la_primera(traductor):
    # "twin" corresponde a varios lemas y el correcto no es el primero: quedarse con
    # uno de antemano descartaba la entrada buena.
    candidatas = traductor.candidatas("twin")
    assert len(candidatas) > 1
    assert "gemelo" in candidatas or "mellizo" in candidatas


def test_el_prefijo_de_infinitivo_no_impide_la_busqueda(traductor):
    # La tabla contiene 'burp' (de eructar) y tambien 'to burp' (de pedar): la
    # coincidencia exacta no debe ganarle a la union de ambas.
    assert "eructar" in traductor.candidatas("to burp")


def test_un_sintagma_espanol_no_se_traduce_por_su_ultima_palabra(traductor):
    """La salvaguarda contra falsos positivos.

    "panel solar", "placa base" y "radiografia dental" estan deliberadamente fuera de
    cobertura, pero su ultima palabra existe en ingles. Aproximar sin saber el idioma
    las hacia responder con SOL, CIMIENTO y DIENTE."""
    for sintagma in ("panel solar", "placa base", "radiografia dental"):
        assert traductor.candidatas(sintagma) == []


def test_la_aproximacion_sigue_disponible_cuando_consta_que_es_ingles(traductor):
    assert "choclo" in traductor.candidatas("boiled corn", aproximar=True)
    assert "liviano" in traductor.candidatas("lightweight", aproximar=True)


def test_un_termino_ausente_no_inventa_traduccion(traductor):
    assert traductor.candidatas("motherboard") == []
    assert traductor.traducir_al_espanol("motherboard") == "motherboard"
