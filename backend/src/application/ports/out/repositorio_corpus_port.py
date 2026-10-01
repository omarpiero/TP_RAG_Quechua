from abc import ABC, abstractmethod

from domain.entities.fragmento import Fragmento


class RepositorioCorpusPort(ABC):
    """Almacenamiento del corpus segmentado, del que se reconstruye el indice.

    Se mantiene separado del indice porque son dos cosas distintas: el corpus es el dato
    persistente y el indice una estructura derivada que se puede reconstruir en cualquier
    momento (RF-13)."""

    @abstractmethod
    def cargar(self) -> list[Fragmento]:
        ...

    @abstractmethod
    def agregar(self, fragmentos: list[Fragmento]) -> int:
        """Incorpora fragmentos nuevos sin duplicar los existentes y devuelve cuantos
        se anadieron efectivamente."""

    @abstractmethod
    def documentos(self) -> list[str]:
        ...
