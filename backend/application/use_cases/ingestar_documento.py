from dataclasses import dataclass
from datetime import date

from application.services.segmentador import Segmentador
from domain.entities.fragmento import TipoFragmento
from domain.entities.fuente import Fuente
from domain.ports.extraccion_documental_port import ExtraccionDocumentalPort
from domain.ports.indice_recuperacion_port import IndiceRecuperacionPort
from domain.ports.repositorio_corpus_port import RepositorioCorpusPort
from domain.ports.repositorio_fuentes_port import RepositorioFuentesPort


@dataclass(frozen=True)
class ResultadoIngesta:
    fuente: Fuente
    paginas_totales: int
    paginas_con_texto: int
    fragmentos_generados: int
    fragmentos_nuevos: int
    total_indexado: int

    @property
    def requiere_ocr(self) -> bool:
        """Si no se extrajo texto de ninguna pagina, el documento es una imagen escaneada y
        necesitaria reconocimiento optico, que el proyecto mantiene como contingencia."""
        return self.paginas_con_texto == 0


class IngestarDocumentoUseCase:
    """RF-01, RF-02 y RF-13: incorpora un documento al corpus, lo segmenta segun su tipo,
    registra su procedencia y reconstruye el indice.

    El registro de la fuente ocurre antes de indexar: si el documento no declara
    licenciamiento, la entidad Fuente lo rechaza y nada llega al indice."""

    def __init__(
        self,
        extractor: ExtraccionDocumentalPort,
        corpus: RepositorioCorpusPort,
        indice: IndiceRecuperacionPort,
        repositorio_fuentes: RepositorioFuentesPort | None = None,
        segmentador: Segmentador | None = None,
    ):
        self._extractor = extractor
        self._corpus = corpus
        self._indice = indice
        self._repositorio_fuentes = repositorio_fuentes
        self._segmentador = segmentador or Segmentador()

    def ejecutar(
        self,
        contenido: bytes,
        nombre_archivo: str,
        tipo: TipoFragmento,
        titulo: str,
        entidad_publicadora: str,
        licenciamiento: str,
        derivado_ocr: bool = False,
    ) -> ResultadoIngesta:
        documento = self._extractor.extraer(contenido, nombre_archivo)

        fuente = Fuente(
            titulo=titulo,
            entidad_publicadora=entidad_publicadora,
            licenciamiento=licenciamiento,
            fecha_extraccion=date.today(),
            nombre_archivo=nombre_archivo,
            paginas_totales=documento.paginas_totales,
            paginas_con_texto=documento.paginas_con_texto,
            derivado_ocr=derivado_ocr,
        )

        fragmentos = self._segmentador.segmentar(documento, tipo, derivado_ocr)
        nuevos = self._corpus.agregar(fragmentos)

        if nuevos:
            self._indice.indexar(self._corpus.cargar())

        if self._repositorio_fuentes is not None:
            self._repositorio_fuentes.crear(fuente)

        return ResultadoIngesta(
            fuente=fuente,
            paginas_totales=documento.paginas_totales,
            paginas_con_texto=documento.paginas_con_texto,
            fragmentos_generados=len(fragmentos),
            fragmentos_nuevos=nuevos,
            total_indexado=self._indice.total_indexado(),
        )

    def reindexar(self) -> int:
        """RF-13: reconstruye el indice desde el corpus persistido."""
        return self._indice.indexar(self._corpus.cargar())
