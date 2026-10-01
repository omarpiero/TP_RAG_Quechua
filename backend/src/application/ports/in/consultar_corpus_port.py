from abc import ABC, abstractmethod

from domain.entities.respuesta import Respuesta


class ConsultarCorpusPort(ABC):
    """Puerto de entrada de HU-03, HU-06 y HU-07: una consulta en espanol o ingles que
    devuelve una respuesta citada o la declaracion de ausencia de respaldo."""

    @abstractmethod
    def ejecutar(self, texto_consulta: str) -> Respuesta: ...
