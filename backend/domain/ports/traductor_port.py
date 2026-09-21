from abc import ABC, abstractmethod


class TraductorPort(ABC):
    """Traduce unicamente la consulta, nunca el corpus ni la respuesta (experimento E7 de la
    prueba de concepto): la forma quechua sale siempre literal del fragmento recuperado."""

    @abstractmethod
    def traducir_al_espanol(self, texto: str) -> str:
        ...
