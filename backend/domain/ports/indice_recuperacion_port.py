from abc import ABC, abstractmethod

from domain.entities.fragmento import Fragmento, FragmentoRecuperado


class IndiceRecuperacionPort(ABC):
    """Sustituye al IndiceVectorialPort previsto en el Documento 0: la prueba de concepto
    determino que sobre este corpus la recuperacion lexica supera a la densa, de modo que
    el puerto se define sobre la operacion (recuperar) y no sobre la tecnica (vectorial)."""

    @abstractmethod
    def indexar(self, fragmentos: list[Fragmento]) -> int:
        """Construye el indice y devuelve el numero de fragmentos indexados."""

    @abstractmethod
    def recuperar(self, consulta: str, k: int = 5) -> list[FragmentoRecuperado]:
        """Devuelve los k fragmentos mas similares, ordenados de mayor a menor puntuacion."""

    @abstractmethod
    def total_indexado(self) -> int:
        ...
