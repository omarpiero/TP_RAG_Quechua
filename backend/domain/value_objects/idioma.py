from enum import Enum


class Idioma(str, Enum):
    ESPANOL = "es"
    INGLES = "en"
    NO_SOPORTADO = "xx"

    @property
    def soportado(self) -> bool:
        return self is not Idioma.NO_SOPORTADO

    @property
    def nombre_legible(self) -> str:
        return {"es": "español", "en": "inglés", "xx": "no soportado"}[self.value]
