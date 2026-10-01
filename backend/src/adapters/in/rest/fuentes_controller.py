import logging

from fastapi import APIRouter, Depends, HTTPException

from application.ports import GestionarFuentesPort
from domain.entities.fuente import Fuente

from . import dependencias
from .esquemas import FuenteEntrada, FuenteSalida

log = logging.getLogger("rag.rest")
router = APIRouter(prefix="/api")


def _a_salida(f: Fuente) -> FuenteSalida:
    return FuenteSalida(
        id=f.id,
        titulo=f.titulo,
        entidad_publicadora=f.entidad_publicadora,
        licenciamiento=f.licenciamiento,
        fecha_extraccion=f.fecha_extraccion,
        nombre_archivo=f.nombre_archivo,
        paginas_totales=f.paginas_totales,
        paginas_con_texto=f.paginas_con_texto,
        derivado_ocr=f.derivado_ocr,
        cobertura_extraccion=round(f.cobertura_extraccion, 4),
    )


@router.post("/fuentes", response_model=FuenteSalida, status_code=201, tags=["fuentes"])
def crear_fuente(
    entrada: FuenteEntrada,
    puerto: GestionarFuentesPort = Depends(dependencias.gestionar_fuentes),
):
    log.info("[REST] POST /api/fuentes")
    try:
        fuente = Fuente(**entrada.model_dump())
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return _a_salida(puerto.registrar(fuente))


@router.get("/fuentes", response_model=list[FuenteSalida], tags=["fuentes"])
def listar_fuentes(puerto: GestionarFuentesPort = Depends(dependencias.gestionar_fuentes)):
    log.info("[REST] GET /api/fuentes")
    return [_a_salida(f) for f in puerto.listar()]


@router.get("/fuentes/{fuente_id}", response_model=FuenteSalida, tags=["fuentes"])
def obtener_fuente(
    fuente_id: str,
    puerto: GestionarFuentesPort = Depends(dependencias.gestionar_fuentes),
):
    log.info("[REST] GET /api/fuentes/{id}")
    fuente = puerto.obtener(fuente_id)
    if fuente is None:
        raise HTTPException(404, "Fuente no encontrada")
    return _a_salida(fuente)


@router.put("/fuentes/{fuente_id}", response_model=FuenteSalida, tags=["fuentes"])
def actualizar_fuente(
    fuente_id: str,
    entrada: FuenteEntrada,
    puerto: GestionarFuentesPort = Depends(dependencias.gestionar_fuentes),
):
    log.info("[REST] PUT /api/fuentes/{id}")
    try:
        fuente = Fuente(id=fuente_id, **entrada.model_dump())
        return _a_salida(puerto.actualizar(fuente))
    except KeyError as exc:
        raise HTTPException(404, "Fuente no encontrada") from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.delete("/fuentes/{fuente_id}", status_code=204, tags=["fuentes"])
def eliminar_fuente(
    fuente_id: str,
    puerto: GestionarFuentesPort = Depends(dependencias.gestionar_fuentes),
):
    log.info("[REST] DELETE /api/fuentes/{id}")
    if not puerto.eliminar(fuente_id):
        raise HTTPException(404, "Fuente no encontrada")
