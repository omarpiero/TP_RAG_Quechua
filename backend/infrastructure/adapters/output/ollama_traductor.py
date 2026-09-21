import re

import httpx

from domain.ports.traductor_port import TraductorPort

INSTRUCCION = (
    "Traduce al español la siguiente palabra o expresión en inglés.\n"
    "Responde únicamente con la traducción, sin comillas, sin explicaciones y sin "
    "ninguna palabra adicional.\n"
    "Si la expresión es un verbo en infinitivo con 'to', traduce solo el verbo.\n\n"
    "Inglés: {texto}\n"
    "Español:"
)


class OllamaTraductor(TraductorPort):
    """Traduce la consulta reutilizando el modelo ya cargado por el generador.

    Se emplea el mismo modelo en lugar de incorporar uno especifico de traduccion porque
    la entrada es de una a cinco palabras y porque evita una segunda descarga y una segunda
    carga en memoria de video, que es el recurso escaso del proyecto.

    El traductor nunca interviene sobre el quechua: solo convierte al español una consulta
    formulada en ingles, y la forma quechua se toma literal del fragmento recuperado."""

    def __init__(
        self,
        url_base: str = "http://localhost:11434",
        modelo: str = "qwen3.5:4b",
        timeout: float = 60.0,
        permanencia: str = "30m",
    ):
        self._url_base = url_base.rstrip("/")
        self._modelo = modelo
        self._timeout = timeout
        self._permanencia = permanencia

    def traducir_al_espanol(self, texto: str) -> str:
        try:
            respuesta = httpx.post(
                f"{self._url_base}/api/generate",
                json={
                    "model": self._modelo,
                    "prompt": INSTRUCCION.format(texto=texto),
                    "stream": False,
                    "think": False,
                    "keep_alive": self._permanencia,
                    "options": {"temperature": 0.0, "num_predict": 30},
                },
                timeout=self._timeout,
            )
            respuesta.raise_for_status()
            return self._limpiar(respuesta.json()["response"])
        except (httpx.HTTPError, KeyError):
            # Si la traduccion falla se devuelve la consulta original: la recuperacion se
            # degrada al comportamiento sin traduccion, pero no se interrumpe.
            return texto

    @staticmethod
    def _limpiar(salida: str) -> str:
        texto = salida.strip().strip('"').strip("'")
        # El modelo puede anteponer una etiqueta o anadir una aclaracion tras un salto.
        texto = re.sub(r"^(español|spanish)\s*:\s*", "", texto, flags=re.IGNORECASE)
        return texto.split("\n")[0].strip().rstrip(".").strip()
