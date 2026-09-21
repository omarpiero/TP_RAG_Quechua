from dataclasses import dataclass, field
from datetime import datetime, timezone

from domain.entities.fragmento import FragmentoRecuperado
from domain.value_objects.idioma import Idioma

AVISO_ALCANCE = (
    "Esta es una consulta sobre fuentes documentales publicadas; "
    "no constituye una validacion por hablantes de la comunidad."
)


@dataclass
class Respuesta:
    consulta_id: str
    texto: str
    respaldo: list[FragmentoRecuperado] = field(default_factory=list)
    abstenida: bool = False
    idioma: Idioma = Idioma.ESPANOL
    similitud_maxima: float = 0.0
    momento: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    aviso: str = AVISO_ALCANCE

    def __post_init__(self):
        # RNF-08: ninguna respuesta afirmativa puede emitirse sin fuente verificable.
        if not self.abstenida and not self.respaldo:
            raise ValueError("Una respuesta no abstenida debe citar al menos un fragmento")

    @property
    def citas(self) -> list[str]:
        return [f.procedencia.citar() for f in self.respaldo]
