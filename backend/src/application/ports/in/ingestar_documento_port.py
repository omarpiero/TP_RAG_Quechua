from abc import ABC, abstractmethod
from dataclasses import dataclass

from domain.entities.fragmento import TipoFragmento
from domain.entities.fuente import Fuente


@dataclass(frozen=True)
class ResultadoIngesta:
    fuente: Fuente
    paginas_totales: int
    paginas_con_texto: int
    fragmentos_generados: int
    fragmentos_nuevos: int
    total_indexado: int

    @property
    def requiere_ocr(self) -> bool:
        """Si no se extrajo texto de ninguna pagina, el documento es una imagen escaneada y
        necesitaria reconocimiento optico, que el proyecto mantiene como contingencia."""
        return self.paginas_con_texto == 0


class IngestarDocumentoPort(ABC):
    """Puerto de entrada de RF-01, RF-02 y RF-13: incorpora un documento al corpus."""

    @abstractmethod
    def ejecutar(
        self,
        contenido: bytes,
        nombre_archivo: str,
        tipo: TipoFragmento,
        titulo: str,
        entidad_publicadora: str,
        licenciamiento: str,
        derivado_ocr: bool = False,
    ) -> ResultadoIngesta: ...
