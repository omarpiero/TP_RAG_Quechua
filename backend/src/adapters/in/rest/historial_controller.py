import logging

from fastapi import APIRouter, Depends, Query, Response

from application.ports import ConsultarHistorialPort

from . import dependencias
from .esquemas import EntradaHistorial

log = logging.getLogger("rag.rest")
router = APIRouter(prefix="/api")


@router.get("/historial", response_model=list[EntradaHistorial], tags=["consulta"])
def historial(
    # R-04 (S13): fuera de rango da 422; antes, un LIMIT negativo era un 500 de PostgreSQL.
    limite: int = Query(50, ge=1, le=500),
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
            via_respaldo=respuesta.via_respaldo,
            momento=respuesta.momento,
            probabilidad_cobertura=respuesta.probabilidad_cobertura,
        )
        for consulta, respuesta in puerto.ejecutar(limite)
    ]


@router.delete("/historial", status_code=204, tags=["consulta"])
def borrar_historial(
    puerto: ConsultarHistorialPort = Depends(dependencias.consultar_historial),
):
    log.info("[REST] DELETE /api/historial")
    log.info("[PUERTO-IN] ConsultarHistorialPort.borrar")
    puerto.borrar()
    return Response(status_code=204)
