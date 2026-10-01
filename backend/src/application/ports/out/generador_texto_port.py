from abc import ABC, abstractmethod

from domain.entities.fragmento import FragmentoRecuperado
from domain.value_objects.idioma import Idioma


class GeneradorTextoPort(ABC):
    @abstractmethod
    def redactar(
        self,
        consulta: str,
        fragmentos: list[FragmentoRecuperado],
        idioma: Idioma,
    ) -> str:
        """Redacta la respuesta ciniendose a los fragmentos recibidos.

        El generador no aporta conocimiento linguistico: la informacion sustantiva proviene
        del fragmento recuperado y no de los pesos del modelo. Ninguna implementacion debe
        invocarse sin fragmentos."""

    @abstractmethod
    def disponible(self) -> bool:
        ...
