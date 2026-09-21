import re
import unicodedata


class DepuradorConsulta:
    """Elimina de la consulta el fraseo que acompana a toda pregunta y que, por repetirse
    en todas, no distingue ninguna.

    No es un detalle de limpieza: el experimento E6 de la prueba de concepto midio que la
    depuracion, junto con la segmentacion por entrada, triplica la ventana util del umbral
    (de 0,13 a 0,41) y eleva el recall en el punto de operacion del 48,3 % al 85,6 %."""

    PLANTILLAS = [
        r"\bcomo\s+se\s+dice\b",
        r"\bque\s+significa\b",
        r"\bnecesito\s+el\s+termino\s+wanka\s+para\s+referirme\s+a\b",
        r"\bestoy\s+buscando\s+la\s+palabra\s+que\s+designa\b",
        r"\bcual\s+es\s+la\s+palabra\b",
        r"\bhow\s+do\s+you\s+say\b",
        r"\bwhat\s+is\s+the\s+wanka\s+quechua\s+word\s+for\b",
        r"\bwhat\s+is\s+the\s+word\s+for\b",
        r"\bin\s+wanka\s+quechua\b",
        r"\ben\s+la\s+variedad\s+wanka\b",
        r"\ben\s+quechua\s+wanka\b",
        r"\bquechua\s+wanka\b",
        r"\bwanka\s+quechua\b",
        r"\bvariedad\s+wanka\b",
    ]

    def __init__(self):
        self._patrones = [re.compile(p, re.IGNORECASE) for p in self.PLANTILLAS]

    def depurar(self, texto: str) -> str:
        normalizado = self.normalizar(texto)
        for patron in self._patrones:
            normalizado = patron.sub(" ", normalizado)
        normalizado = re.sub(r"[^\w\s]", " ", normalizado)
        depurado = re.sub(r"\s+", " ", normalizado).strip()
        # Una consulta que era solo fraseo se devuelve intacta: vaciarla dejaria al
        # recuperador sin nada con que comparar y produciria una abstencion enganosa.
        return depurado or self.normalizar(texto)

    @staticmethod
    def normalizar(texto: str) -> str:
        """Minusculas y sin diacriticos. Se aplica por igual a la consulta y al corpus para
        que la variacion ortografica entre fuentes (riesgo R-04) no impida la coincidencia."""
        sin_tildes = "".join(
            c
            for c in unicodedata.normalize("NFD", texto.lower())
            if unicodedata.category(c) != "Mn"
        )
        return sin_tildes
