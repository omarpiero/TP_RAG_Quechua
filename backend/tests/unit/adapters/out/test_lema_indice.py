"""Regla de lema (ADR-021, condiciones 1 y 2) sobre un indice pequeno con entradas reales."""

import pytest

from adapters.out.recuperacion.indice_hibrido_lexico import IndiceHibridoLexico
from domain.entities.fragmento import Fragmento, TipoFragmento
from domain.value_objects.procedencia import Procedencia

DOC = "293274822-diccionario-quechua-Wanka-docx.pdf"


def _frag(id_, texto, pagina, tipo=TipoFragmento.LEXICOGRAFICO):
    return Fragmento(id=id_, texto=texto, procedencia=Procedencia(DOC, pagina), tipo=tipo)


@pytest.fixture(scope="module")
def indice():
    idx = IndiceHibridoLexico()
    idx.indexar(
        [
            _frag("z", "ZORRO: Atuq.", 37),
            _frag("c", "CÓNCAVO: Puklu.", 9),
            _frag("k", "CONFESAR: Kunfisay.", 9),
            _frag(
                "p",
                "El zorro aparece en los relatos tradicionales de la region.",
                5,
                TipoFragmento.PROSA,
            ),
        ]
    )
    return idx


@pytest.mark.parametrize(
    "consulta", ["zorro", "Zorro", "ZORRO", "¿cómo se dice Zorro en quechua wanka?"]
)
def test_el_lema_coincide_sin_importar_mayusculas_ni_fraseo(indice, consulta):
    assert indice.es_lema(consulta)
    assert indice.recuperar(consulta, k=3)[0].coincidencia_lema


def test_la_tilde_se_ignora(indice):
    assert indice.es_lema("concavo") and indice.es_lema("cóncavo")


@pytest.mark.salvaguarda
@pytest.mark.parametrize(
    "consulta", ["¿cómo se dice zorro de peces?", "zorro de mar", "banco de peces"]
)
def test_un_termino_de_varias_palabras_no_activa_la_regla(indice, consulta):
    assert not indice.es_lema(consulta)
    assert not any(r.coincidencia_lema for r in indice.recuperar(consulta, k=4))


@pytest.mark.salvaguarda
def test_la_prosa_nunca_cuenta_como_lema(indice):
    assert not any(r.coincidencia_lema for r in indice.recuperar_prosa("zorro", k=3))
