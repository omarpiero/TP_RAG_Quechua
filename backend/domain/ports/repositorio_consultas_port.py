from abc import ABC, abstractmethod

from domain.entities.consulta import Consulta
from domain.entities.respuesta import Respuesta


class RepositorioConsultasPort(ABC):
    @abstractmethod
    def registrar(self, consulta: Consulta, respuesta: Respuesta) -> None:
        ...

    @abstractmethod
    def historial(self, limite: int = 50) -> list[tuple[Consulta, Respuesta]]:
        """Consultas y respuestas de la sesion activa (RF-11)."""

    @abstractmethod
    def no_cubiertas(self, limite: int = 500) -> list[Consulta]:
        """Consultas en las que el sistema se abstuvo. Es el insumo con el que el PMV2
        entrenara los modelos de prediccion de cobertura y de demanda lexica."""

    @abstractmethod
    def total_registradas(self) -> int:
        ...
