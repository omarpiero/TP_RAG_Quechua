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


@router.get("/vivo", tags=["sistema"])
def vivo():
    """REF-01 (S13, ADR-034): prueba de vida para el ping programado. No toca la base ni el
    generador, de modo que mantiene despierto el servicio de Render sin despertar a Neon ni
    gastar cuota de Gemini. `/api/estado` sigue siendo la comprobacion completa."""
    return {"vivo": True}
