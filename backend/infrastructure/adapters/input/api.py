from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from domain.entities.fragmento import TipoFragmento
from domain.entities.fuente import Fuente
from infrastructure.adapters.input.esquemas import (
    ConsultaEntrada,
    DocumentosCorpus,
    EntradaHistorial,
    EstadoSistema,
    FuenteEntrada,
    FuenteSalida,
    RespaldoSalida,
    RespuestaSalida,
    ResultadoIngestaSalida,
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
        consulta_traducida=respuesta.consulta_traducida,
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


TAMANO_MAXIMO = 60 * 1024 * 1024


@router.post(
    "/corpus/documentos", response_model=ResultadoIngestaSalida, tags=["corpus"]
)
async def ingestar_documento(
    request: Request,
    archivo: UploadFile = File(...),
    titulo: str = Form(...),
    entidad_publicadora: str = Form(...),
    licenciamiento: str = Form(...),
    tipo: str = Form("lexicografico"),
):
    """RF-01, RF-02 y RF-13: incorpora un PDF al corpus, lo segmenta segun su tipo y
    reconstruye el indice sin reiniciar el servicio."""
    if not archivo.filename or not archivo.filename.lower().endswith(".pdf"):
        raise HTTPException(422, "Solo se admiten archivos PDF")

    contenido = await archivo.read()
    if len(contenido) > TAMANO_MAXIMO:
        raise HTTPException(413, "El archivo supera el tamano maximo admitido (60 MB)")

    try:
        tipo_fragmento = TipoFragmento(tipo)
    except ValueError:
        raise HTTPException(422, "El tipo debe ser 'lexicografico' o 'prosa'") from None

    try:
        resultado = _contenedor(request).ingestar_documento.ejecutar(
            contenido=contenido,
            nombre_archivo=archivo.filename,
            tipo=tipo_fragmento,
            titulo=titulo,
            entidad_publicadora=entidad_publicadora,
            licenciamiento=licenciamiento,
        )
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc

    aviso = None
    if resultado.requiere_ocr:
        aviso = (
            "No se extrajo texto de ninguna pagina: el documento parece una imagen "
            "escaneada y requeriria reconocimiento optico, que no forma parte del flujo "
            "ordinario del sistema."
        )
    elif resultado.fragmentos_nuevos == 0:
        aviso = "Todos los fragmentos ya estaban en el corpus; el indice no ha cambiado."

    return ResultadoIngestaSalida(
        nombre_archivo=archivo.filename,
        titulo=titulo,
        paginas_totales=resultado.paginas_totales,
        paginas_con_texto=resultado.paginas_con_texto,
        cobertura_extraccion=round(
            resultado.paginas_con_texto / resultado.paginas_totales, 4
        )
        if resultado.paginas_totales
        else 0.0,
        fragmentos_generados=resultado.fragmentos_generados,
        fragmentos_nuevos=resultado.fragmentos_nuevos,
        total_indexado=resultado.total_indexado,
        requiere_ocr=resultado.requiere_ocr,
        aviso=aviso,
    )


@router.get("/corpus/documentos", response_model=DocumentosCorpus, tags=["corpus"])
def listar_documentos(request: Request):
    c = _contenedor(request)
    return DocumentosCorpus(
        documentos=c.corpus.documentos(), total_fragmentos=c.indice.total_indexado()
    )


@router.post("/corpus/reindexar", response_model=DocumentosCorpus, tags=["corpus"])
def reindexar(request: Request):
    c = _contenedor(request)
    c.ingestar_documento.reindexar()
    return DocumentosCorpus(
        documentos=c.corpus.documentos(), total_fragmentos=c.indice.total_indexado()
    )


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
