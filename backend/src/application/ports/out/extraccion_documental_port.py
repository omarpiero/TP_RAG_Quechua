from abc import ABC, abstractmethod

from domain.entities.documento_extraido import DocumentoExtraido, PaginaExtraida  # noqa: F401


class ExtraccionDocumentalPort(ABC):
    @abstractmethod
    def extraer(self, contenido: bytes, nombre_archivo: str) -> DocumentoExtraido:
        """Extrae el texto conservando el numero de pagina de cada fragmento.

        La pagina no es un metadato accesorio: sin ella la trazabilidad exigida por RF-07
        no puede cumplirse, porque la respuesta no podria verificarse en la fuente."""
