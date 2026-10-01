import re

from domain.services.depurador_consulta import DepuradorConsulta


class ClasificadorConsulta:
    """Distingue la consulta LEXICA (pide la forma de un termino) de la pregunta de prosa
    (pregunta por gramatica, fonologia, uso...). Defecto D-1.

    Solo la pregunta de prosa puede recibir pasajes del corpus al abstenerse: ante
    "como se dice computadora", ofrecer un parrafo de la gramatica sugiere una cobertura que
    no existe. Una consulta es lexica si:
    - usa un fraseo de peticion de termino ("como se dice X", "how do you say X",
      "cual es la palabra", "what is the word for", ...), o
    - tras depurar el fraseo queda un termino suelto de una o dos palabras.

    Solo biblioteca estandar; sin umbrales ni datos del corpus."""

    FRASEO_LEXICO = [
        r"\bcomo\s+se\s+dice\b",
        r"\bnecesito\s+el\s+termino\s+wanka\s+para\s+referirme\s+a\b",
        r"\bestoy\s+buscando\s+la\s+palabra\s+que\s+designa\b",
        r"\bcual\s+es\s+la\s+palabra\b",
        r"\bhow\s+do\s+you\s+say\b",
        r"\bwhat\s+is\s+the\s+wanka\s+quechua\s+word\s+for\b",
        r"\bwhat\s+is\s+the\s+word\s+for\b",
    ]
    MAXIMO_PALABRAS_TERMINO = 2

    def __init__(self, depurador: DepuradorConsulta | None = None):
        self._depurador = depurador or DepuradorConsulta()
        self._patrones = [re.compile(p) for p in self.FRASEO_LEXICO]

    def es_lexica(self, texto: str) -> bool:
        normalizado = self._depurador.normalizar(texto)
        if any(p.search(normalizado) for p in self._patrones):
            return True
        return len(self._depurador.depurar(texto).split()) <= self.MAXIMO_PALABRAS_TERMINO
