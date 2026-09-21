from domain.entities.fuente import Fuente
from domain.ports.repositorio_fuentes_port import RepositorioFuentesPort


class GestionarFuentesUseCase:
    """HU-01: registro de la procedencia y el licenciamiento de cada documento del corpus.

    La entidad no admite una fuente sin licenciamiento declarado, de modo que la obligacion
    de gobernanza (RNF-11) se hace cumplir en el dominio y no en la interfaz."""

    def __init__(self, repositorio: RepositorioFuentesPort):
        self._repositorio = repositorio

    def registrar(self, fuente: Fuente) -> Fuente:
        return self._repositorio.crear(fuente)

    def obtener(self, fuente_id: str) -> Fuente | None:
        return self._repositorio.obtener(fuente_id)

    def listar(self) -> list[Fuente]:
        return self._repositorio.listar()

    def actualizar(self, fuente: Fuente) -> Fuente:
        return self._repositorio.actualizar(fuente)

    def eliminar(self, fuente_id: str) -> bool:
        return self._repositorio.eliminar(fuente_id)
