from datetime import date, datetime

from pydantic import BaseModel, Field


class ConsultaEntrada(BaseModel):
    texto: str = Field(min_length=1, max_length=500)


class RespaldoSalida(BaseModel):
    fragmento_id: str
    texto: str
    documento: str
    pagina: int
    puntuacion: float
    derivado_ocr: bool
    coincidencia_lema: bool


class RespuestaSalida(BaseModel):
    consulta_id: str
    texto: str
    abstenida: bool
    idioma: str
    similitud_maxima: float
    aviso: str
    respaldo: list[RespaldoSalida]
    consulta_traducida: str | None = None


class EntradaHistorial(BaseModel):
    consulta: str
    respuesta: str
    abstenida: bool
    similitud_maxima: float
    momento: datetime


class FuenteEntrada(BaseModel):
    titulo: str = Field(min_length=1, max_length=300)
    entidad_publicadora: str = Field(min_length=1, max_length=200)
    licenciamiento: str = Field(min_length=1, max_length=300)
    fecha_extraccion: date
    nombre_archivo: str = Field(min_length=1, max_length=300)
    paginas_totales: int = 0
    paginas_con_texto: int = 0
    derivado_ocr: bool = False


class FuenteSalida(FuenteEntrada):
    id: str
    cobertura_extraccion: float


class ResultadoIngestaSalida(BaseModel):
    nombre_archivo: str
    titulo: str
    paginas_totales: int
    paginas_con_texto: int
    cobertura_extraccion: float
    fragmentos_generados: int
    fragmentos_nuevos: int
    total_indexado: int
    requiere_ocr: bool
    aviso: str | None = None


class DocumentosCorpus(BaseModel):
    documentos: list[str]
    total_fragmentos: int


class EstadoSistema(BaseModel):
    fragmentos_indexados: int
    umbral_abstencion: float
    generador_disponible: bool
    base_datos_disponible: bool
    modelo: str
