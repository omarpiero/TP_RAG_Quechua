from dataclasses import dataclass, field
from datetime import datetime, timezone

from domain.entities.fragmento import FragmentoRecuperado
from domain.value_objects.idioma import Idioma

AVISO_ALCANCE = (
    "Esta es una consulta sobre fuentes documentales publicadas; "
    "no constituye una validación por hablantes de la comunidad."
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
    # Con que terminos se busco realmente, cuando la consulta se tradujo antes de recuperar.
    consulta_traducida: str | None = None
    # Pasajes de prosa que podrian tratar la consulta, sin que el sistema lo afirme.
    #
    # La similitud lexica no distingue una pregunta de gramatica que el corpus cubre de una
    # que no: basta cambiar el nombre de la lengua para que la pregunta deje de estar
    # cubierta sin que las palabras cambien, y el depurador borra precisamente ese nombre.
    # Medido sobre 60 preguntas de prosa y 135 negativas, las distribuciones se solapan y
    # ningun umbral separa ambas poblaciones conservando cobertura util. En lugar de
    # simular una certeza que no existe, el material se entrega literal y citado para que
    # lo juzgue quien consulta, que es como se usa una gramatica en papel.
    pasajes: list[FragmentoRecuperado] = field(default_factory=list)

    def __post_init__(self):
        # RNF-08: ninguna respuesta afirmativa puede emitirse sin fuente verificable.
        if not self.abstenida and not self.respaldo:
            raise ValueError("Una respuesta no abstenida debe citar al menos un fragmento")
        if self.pasajes and not self.abstenida:
            raise ValueError(
                "Los pasajes sin confirmar solo acompanan a una respuesta abstenida: "
                "entregarlos junto a una afirmacion los presentaria como su respaldo"
            )

    @property
    def tiene_pasajes(self) -> bool:
        return bool(self.pasajes)

    @property
    def citas(self) -> list[str]:
        return [f.procedencia.citar() for f in self.respaldo]
