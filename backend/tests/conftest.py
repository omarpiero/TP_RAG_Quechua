import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from infrastructure.adapters.output.corpus_jsonl import cargar_fragmentos  # noqa: E402
from infrastructure.adapters.output.indice_hibrido_lexico import (  # noqa: E402
    IndiceHibridoLexico,
)

DATOS = RAIZ / "data"


@pytest.fixture(scope="session")
def fragmentos():
    return cargar_fragmentos(DATOS / "fragmentos_v2.jsonl")


@pytest.fixture(scope="session")
def indice(fragmentos):
    idx = IndiceHibridoLexico()
    idx.indexar(fragmentos)
    return idx


@pytest.fixture(scope="session")
def evaluacion():
    return json.loads((DATOS / "evaluacion_v2.json").read_text(encoding="utf-8"))
