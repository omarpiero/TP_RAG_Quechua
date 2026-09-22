from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PaginaExtraida:
    numero: int
    texto: str

    @property
    def tiene_texto(self) -> bool:
        return bool(self.texto.strip())


@dataclass(frozen=True)
class DocumentoExtraido:
    nombre_archivo: str
    paginas: list[PaginaExtraida]

    @property
    def paginas_totales(self) -> int:
        return len(self.paginas)

    @property
    def paginas_con_texto(self) -> int:
        return sum(1 for p in self.paginas if p.tiene_texto)

    @property
    def cobertura(self) -> float:
        if not self.paginas:
            return 0.0
        return self.paginas_con_texto / self.paginas_totales


class ExtraccionDocumentalPort(ABC):
    @abstractmethod
    def extraer(self, contenido: bytes, nombre_archivo: str) -> DocumentoExtraido:
        """Extrae el texto conservando el numero de pagina de cada fragmento.

        La pagina no es un metadato accesorio: sin ella la trazabilidad exigida por RF-07
        no puede cumplirse, porque la respuesta no podria verificarse en la fuente."""
