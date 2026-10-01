import logging

from application.ports import ConsultarHistorialPort
from application.ports.out.repositorio_consultas_port import RepositorioConsultasPort
from domain.entities.consulta import Consulta
from domain.entities.respuesta import Respuesta

log = logging.getLogger("rag.caso_uso")


class ConsultarHistorialUseCase(ConsultarHistorialPort):
    """RF-11: devuelve las consultas y respuestas registradas de la sesion activa."""

    def __init__(self, repositorio: RepositorioConsultasPort):
        self._repositorio = repositorio

    def ejecutar(self, limite: int = 50) -> list[tuple[Consulta, Respuesta]]:
        log.info("[CASO-USO] ConsultarHistorial: limite=%d", limite)
        return self._repositorio.historial(limite)

    def borrar(self) -> int:
        log.info("[CASO-USO] ConsultarHistorial: borrar")
        return self._repositorio.borrar_todo()
