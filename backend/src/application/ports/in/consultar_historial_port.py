from abc import ABC, abstractmethod

from domain.entities.consulta import Consulta
from domain.entities.respuesta import Respuesta


class ConsultarHistorialPort(ABC):
    """Puerto de entrada de RF-11: consultas y respuestas de la sesion activa."""

    @abstractmethod
    def ejecutar(self, limite: int = 50) -> list[tuple[Consulta, Respuesta]]: ...

    @abstractmethod
    def borrar(self) -> int:
        """Borra el historial y devuelve cuantas consultas se eliminaron."""
