import logging

from fastapi import APIRouter, Depends

from . import dependencias
from .esquemas import EstadoSistema

log = logging.getLogger("rag.rest")
router = APIRouter(prefix="/api")


@router.get("/estado", response_model=EstadoSistema, tags=["sistema"])
def estado(datos: dict = Depends(dependencias.estado_sistema)):
    log.info("[REST] GET /api/estado")
    return EstadoSistema(**datos)
