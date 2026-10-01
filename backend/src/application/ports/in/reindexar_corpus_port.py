from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class EstadoCorpus:
    documentos: list[str]
    total_fragmentos: int


class ReindexarCorpusPort(ABC):
    """Puerto de entrada de RF-13: reconstruye el indice desde el corpus persistido."""

    @abstractmethod
    def ejecutar(self) -> EstadoCorpus: ...

    @abstractmethod
    def estado(self) -> EstadoCorpus:
        """Documentos del corpus y fragmentos indexados, sin reconstruir nada."""
