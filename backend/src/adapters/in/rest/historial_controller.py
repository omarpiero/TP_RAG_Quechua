import logging

from fastapi import APIRouter, Depends

from application.ports import ConsultarHistorialPort

from . import dependencias
from .esquemas import EntradaHistorial

log = logging.getLogger("rag.rest")
router = APIRouter(prefix="/api")


@router.get("/historial", response_model=list[EntradaHistorial], tags=["consulta"])
def historial(
    limite: int = 50,
    puerto: ConsultarHistorialPort = Depends(dependencias.consultar_historial),
):
    log.info("[REST] GET /api/historial")
    log.info("[PUERTO-IN] ConsultarHistorialPort.ejecutar")
    return [
        EntradaHistorial(
            consulta=consulta.texto,
            respuesta=respuesta.texto,
            abstenida=respuesta.abstenida,
            similitud_maxima=round(respuesta.similitud_maxima, 4),
            momento=respuesta.momento,
        )
        for consulta, respuesta in puerto.ejecutar(limite)
    ]
