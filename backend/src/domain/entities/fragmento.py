from dataclasses import dataclass
from enum import Enum

from domain.value_objects.procedencia import Procedencia
from domain.value_objects.puntuacion_similitud import PuntuacionSimilitud


class TipoFragmento(str, Enum):
    LEXICOGRAFICO = "lexicografico"
    PROSA = "prosa"


@dataclass(frozen=True)
class Fragmento:
    id: str
    texto: str
    procedencia: Procedencia
    tipo: TipoFragmento

    def __post_init__(self):
        if not self.texto.strip():
            raise ValueError(f"Fragmento {self.id} sin texto")


@dataclass(frozen=True)
class FragmentoRecuperado:
    fragmento: Fragmento
    puntuacion: PuntuacionSimilitud
    # Senal independiente de la similitud: el termino consultado coincide exactamente con
    # el lema de una entrada lexicografica. No se expresa elevando la puntuacion porque no
    # es una similitud medida sino una certeza documental, y mezclarlas haria ilegible la
    # calibracion del umbral.
    coincidencia_lema: bool = False

    @property
    def id(self) -> str:
        return self.fragmento.id

    @property
    def texto(self) -> str:
        return self.fragmento.texto

    @property
    def procedencia(self) -> Procedencia:
        return self.fragmento.procedencia
