from abc import ABC, abstractmethod


class TraductorPort(ABC):
    """Traduce unicamente la consulta, nunca el corpus ni la respuesta (experimento E7 de la
    prueba de concepto): la forma quechua sale siempre literal del fragmento recuperado."""

    @abstractmethod
    def traducir_al_espanol(self, texto: str) -> str:
        ...

    def candidatas(self, texto: str, aproximar: bool = False) -> list[str]:
        """Todas las lecturas espanolas plausibles del termino, no solo la mejor.

        Un termino ingles corriente corresponde a varios lemas del corpus ("twin" ->
        doble, gemelo, mellizo) y elegir uno de antemano descarta el correcto la mayoria
        de las veces. La recuperacion se ejecuta con todas y el umbral decide."""
        traducida = self.traducir_al_espanol(texto)
        return [traducida] if traducida else []
