from abc import ABC, abstractmethod

from domain.entities.fuente import Fuente


class GestionarFuentesPort(ABC):
    """Puerto de entrada de HU-01: procedencia y licenciamiento de cada documento."""

    @abstractmethod
    def registrar(self, fuente: Fuente) -> Fuente: ...

    @abstractmethod
    def obtener(self, fuente_id: str) -> Fuente | None: ...

    @abstractmethod
    def listar(self) -> list[Fuente]: ...

    @abstractmethod
    def actualizar(self, fuente: Fuente) -> Fuente: ...

    @abstractmethod
    def eliminar(self, fuente_id: str) -> bool: ...
