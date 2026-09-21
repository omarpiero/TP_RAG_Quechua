from abc import ABC, abstractmethod

from domain.value_objects.idioma import Idioma


class DetectorIdiomaPort(ABC):
    @abstractmethod
    def detectar(self, texto: str) -> Idioma:
        ...
