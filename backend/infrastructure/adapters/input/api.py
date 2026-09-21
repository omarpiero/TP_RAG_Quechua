from fastapi import APIRouter, HTTPException, Request

from domain.entities.fuente import Fuente
from infrastructure.adapters.input.esquemas import (
    ConsultaEntrada,
    EntradaHistorial,
    EstadoSistema,
    FuenteEntrada,
    FuenteSalida,
    RespaldoSalida,
    RespuestaSalida,
)
from infrastructure.config import configuracion

router = APIRouter(prefix="/api")


def _contenedor(request: Request):
    return request.app.state.contenedor


@router.get("/estado", response_model=EstadoSistema, tags=["sistema"])
def estado(request: Request):
    c = _contenedor(request)
    return EstadoSistema(
        fragmentos_indexados=c.indice.total_indexado(),
        umbral_abstencion=c.evaluador.umbral,
        generador_disponible=c.generador.disponible(),
        base_datos_disponible=c.base_datos_disponible,
        modelo=configuracion.ollama_modelo,
    )


@router.post("/consultas", response_model=RespuestaSalida, tags=["consulta"])
def consultar(entrada: ConsultaEntrada, request: Request):
    """HU-03, HU-06 y HU-07. La respuesta no puede emitirse sin los campos de documento y
    pagina cuando no es una abstencion: el contrato lo hace verificable."""
    c = _contenedor(request)
    respuesta = c.consultar_corpus.ejecutar(entrada.texto)
    return RespuestaSalida(
        consulta_id=respuesta.consulta_id,
        texto=respuesta.texto,
        abstenida=respuesta.abstenida,
        idioma=respuesta.idioma.value,
        similitud_maxima=round(respuesta.similitud_maxima, 4),
        aviso=respuesta.aviso,
        respaldo=[
            RespaldoSalida(
                fragmento_id=r.id,
                texto=r.texto,
                documento=r.procedencia.documento,
                pagina=r.procedencia.pagina,
                puntuacion=round(r.puntuacion.valor, 4),
                derivado_ocr=r.procedencia.derivado_ocr,
                coincidencia_lema=r.coincidencia_lema,
            )
            for r in respuesta.respaldo
        ],
    )


@router.get("/historial", response_model=list[EntradaHistorial], tags=["consulta"])
def historial(request: Request, limite: int = 50):
    c = _contenedor(request)
    if c.repositorio_consultas is None:
        raise HTTPException(503, "El historial requiere la base de datos y no esta conectada")
    return [
        EntradaHistorial(
            consulta=consulta.texto,
            respuesta=respuesta.texto,
            abstenida=respuesta.abstenida,
            similitud_maxima=round(respuesta.similitud_maxima, 4),
            momento=respuesta.momento,
        )
        for consulta, respuesta in c.repositorio_consultas.historial(limite)
    ]


def _gestor(request: Request):
    gestor = _contenedor(request).gestionar_fuentes
    if gestor is None:
        raise HTTPException(503, "La gestion de fuentes requiere la base de datos")
    return gestor


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
def crear_fuente(entrada: FuenteEntrada, request: Request):
    try:
        fuente = Fuente(**entrada.model_dump())
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return _a_salida(_gestor(request).registrar(fuente))


@router.get("/fuentes", response_model=list[FuenteSalida], tags=["fuentes"])
def listar_fuentes(request: Request):
    return [_a_salida(f) for f in _gestor(request).listar()]


@router.get("/fuentes/{fuente_id}", response_model=FuenteSalida, tags=["fuentes"])
def obtener_fuente(fuente_id: str, request: Request):
    fuente = _gestor(request).obtener(fuente_id)
    if fuente is None:
        raise HTTPException(404, "Fuente no encontrada")
    return _a_salida(fuente)


@router.put("/fuentes/{fuente_id}", response_model=FuenteSalida, tags=["fuentes"])
def actualizar_fuente(fuente_id: str, entrada: FuenteEntrada, request: Request):
    try:
        fuente = Fuente(id=fuente_id, **entrada.model_dump())
        return _a_salida(_gestor(request).actualizar(fuente))
    except KeyError as exc:
        raise HTTPException(404, "Fuente no encontrada") from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc


@router.delete("/fuentes/{fuente_id}", status_code=204, tags=["fuentes"])
def eliminar_fuente(fuente_id: str, request: Request):
    if not _gestor(request).eliminar(fuente_id):
        raise HTTPException(404, "Fuente no encontrada")
