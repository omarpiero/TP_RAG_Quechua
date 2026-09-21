import re

from domain.ports.detector_idioma_port import DetectorIdiomaPort
from domain.value_objects.idioma import Idioma

MARCAS_ESPANOL = {
    "como", "que", "cual", "cuales", "se", "dice", "el", "la", "los", "las", "en",
    "del", "de", "para", "por", "significa", "palabra", "termino", "necesito",
    "estoy", "buscando", "designa", "variedad", "quiero", "saber", "es", "una", "un",
}
MARCAS_INGLES = {
    "how", "what", "which", "the", "for", "do", "you", "say", "is", "are", "word",
    "mean", "means", "i", "need", "looking", "term", "in", "of", "to", "about",
}


class DetectorIdiomaHeuristico(DetectorIdiomaPort):
    """Cuenta palabras funcionales de cada idioma. Basta para el alcance declarado, en el
    que el sistema solo admite espanol e ingles (RF-04) y debe rechazar cualquier otro."""

    def detectar(self, texto: str) -> Idioma:
        palabras = set(re.findall(r"\b\w+\b", texto.lower()))
        if not palabras:
            return Idioma.NO_SOPORTADO

        marcas_es = len(palabras & MARCAS_ESPANOL)
        marcas_en = len(palabras & MARCAS_INGLES)

        if marcas_es == 0 and marcas_en == 0:
            # Sin marcas funcionales (p. ej. una sola palabra suelta) se asume espanol,
            # que es el idioma en el que esta redactado el corpus.
            return Idioma.ESPANOL
        if marcas_en > marcas_es:
            return Idioma.INGLES
        return Idioma.ESPANOL
