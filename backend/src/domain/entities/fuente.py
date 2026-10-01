from dataclasses import dataclass, field
from datetime import date
from uuid import uuid4


@dataclass
class Fuente:
    """Documento del corpus con su gobernanza declarada (RNF-11, principios CARE):
    toda fuente indexada queda registrada con procedencia, fecha de extraccion y
    condiciones de licenciamiento antes de poder ser citada."""

    titulo: str
    entidad_publicadora: str
    licenciamiento: str
    fecha_extraccion: date
    nombre_archivo: str
    paginas_totales: int = 0
    paginas_con_texto: int = 0
    derivado_ocr: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        if not self.licenciamiento.strip():
            raise ValueError(
                f"La fuente '{self.titulo}' no declara licenciamiento y no puede indexarse"
            )

    @property
    def cobertura_extraccion(self) -> float:
        if self.paginas_totales == 0:
            return 0.0
        return self.paginas_con_texto / self.paginas_totales
