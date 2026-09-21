import httpx

from domain.entities.fragmento import FragmentoRecuperado
from domain.ports.generador_texto_port import GeneradorTextoPort
from domain.value_objects.idioma import Idioma

INSTRUCCION = {
    Idioma.ESPANOL: (
        "Eres un asistente de consulta documental sobre el quechua wanka de Junin.\n"
        "Reglas estrictas:\n"
        "1. Responde UNICAMENTE con la informacion contenida en los fragmentos entregados.\n"
        "2. No inventes, no traduzcas y no completes ninguna forma en quechua wanka que no "
        "aparezca literalmente en los fragmentos.\n"
        "3. Copia la forma quechua exactamente como figura en el fragmento.\n"
        "4. Si los fragmentos no contienen la respuesta, dilo de forma explicita.\n"
        "5. Responde en espanol, en un maximo de tres frases, sin encabezados ni listas."
    ),
    Idioma.INGLES: (
        "You are a documentary consultation assistant for Wanka Quechua of Junin.\n"
        "Strict rules:\n"
        "1. Answer ONLY with information contained in the provided fragments.\n"
        "2. Never invent, translate or complete any Wanka Quechua form that does not appear "
        "literally in the fragments.\n"
        "3. Copy the Quechua form exactly as it appears in the fragment.\n"
        "4. If the fragments do not contain the answer, say so explicitly.\n"
        "5. Answer in English in at most three sentences, with no headings or lists. "
        "Keep the Quechua term untranslated."
    ),
}


class OllamaGenerador(GeneradorTextoPort):
    """Adaptador del puerto de generacion contra el servicio HTTP local de Ollama.

    Cumple la integracion con un servicio externo exigida por la consigna sin contradecir
    RF-12 y RNF-06: el servicio es externo al proceso pero interno al equipo, de modo que
    ninguna consulta ni fragmento del corpus sale del dispositivo."""

    def __init__(
        self,
        url_base: str = "http://localhost:11434",
        modelo: str = "qwen3.5:4b",
        temperatura: float = 0.1,
        timeout: float = 120.0,
    ):
        self._url_base = url_base.rstrip("/")
        self._modelo = modelo
        self._temperatura = temperatura
        self._timeout = timeout

    def redactar(
        self,
        consulta: str,
        fragmentos: list[FragmentoRecuperado],
        idioma: Idioma,
    ) -> str:
        if not fragmentos:
            raise ValueError(
                "El generador no puede invocarse sin fragmentos: la decision de abstencion "
                "se toma antes, en EvaluadorConfianza"
            )

        contexto = "\n\n".join(
            f"[Fragmento {i}] {f.texto}\n(Fuente: {f.procedencia.citar()})"
            for i, f in enumerate(fragmentos, start=1)
        )
        instruccion = INSTRUCCION.get(idioma, INSTRUCCION[Idioma.ESPANOL])
        prompt = f"{instruccion}\n\nFragmentos:\n{contexto}\n\nConsulta: {consulta}\n\nRespuesta:"

        respuesta = httpx.post(
            f"{self._url_base}/api/generate",
            json={
                "model": self._modelo,
                "prompt": prompt,
                "stream": False,
                "think": False,
                "options": {"temperature": self._temperatura, "num_predict": 300},
            },
            timeout=self._timeout,
        )
        respuesta.raise_for_status()
        return respuesta.json()["response"].strip()

    def disponible(self) -> bool:
        try:
            r = httpx.get(f"{self._url_base}/api/tags", timeout=5.0)
            r.raise_for_status()
            modelos = {m["name"] for m in r.json().get("models", [])}
            return any(m.startswith(self._modelo.split(":")[0]) for m in modelos)
        except (httpx.HTTPError, KeyError):
            return False
