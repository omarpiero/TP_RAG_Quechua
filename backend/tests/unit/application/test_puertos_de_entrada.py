"""Cada caso de uso implementa exactamente un puerto de entrada (PR-02)."""

import pytest

from application.ports import (
    ConsultarCorpusPort,
    ConsultarHistorialPort,
    GestionarFuentesPort,
    IngestarDocumentoPort,
    ReindexarCorpusPort,
)
from application.use_cases.consultar_corpus import ConsultarCorpusUseCase
from application.use_cases.consultar_historial import ConsultarHistorialUseCase
from application.use_cases.gestionar_fuentes import GestionarFuentesUseCase
from application.use_cases.ingestar_documento import IngestarDocumentoUseCase
from application.use_cases.reindexar_corpus import ReindexarCorpusUseCase

PUERTOS = {
    ConsultarCorpusPort,
    IngestarDocumentoPort,
    GestionarFuentesPort,
    ConsultarHistorialPort,
    ReindexarCorpusPort,
}


@pytest.mark.parametrize(
    ("caso_de_uso", "puerto"),
    [
        (ConsultarCorpusUseCase, ConsultarCorpusPort),
        (IngestarDocumentoUseCase, IngestarDocumentoPort),
        (GestionarFuentesUseCase, GestionarFuentesPort),
        (ConsultarHistorialUseCase, ConsultarHistorialPort),
        (ReindexarCorpusUseCase, ReindexarCorpusPort),
    ],
)
def test_cada_caso_de_uso_implementa_exactamente_un_puerto(caso_de_uso, puerto):
    implementados = {p for p in PUERTOS if issubclass(caso_de_uso, p)}
    assert implementados == {puerto}
