"""Composition root: el unico lugar donde el dominio se conecta con tecnologias concretas.

Sustituir PostgreSQL por SQLite, u Ollama por el motor de inferencia embebido del
incremento movil, se resuelve aqui sin tocar el nucleo ni los casos de uso.
"""

import logging

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from application.services.evaluador_confianza import EvaluadorConfianza
from application.use_cases.consultar_corpus import ConsultarCorpusUseCase
from application.use_cases.gestionar_fuentes import GestionarFuentesUseCase
from application.use_cases.ingestar_documento import IngestarDocumentoUseCase
from infrastructure.adapters.output.corpus_jsonl import CorpusJsonl
from infrastructure.adapters.output.extractor_pdf import ExtractorPdf
from infrastructure.adapters.output.detector_idioma_heuristico import (
    DetectorIdiomaHeuristico,
)
from infrastructure.adapters.output.indice_hibrido_lexico import IndiceHibridoLexico
from infrastructure.adapters.output.ollama_generador import OllamaGenerador
from infrastructure.adapters.output.ollama_traductor import OllamaTraductor
from infrastructure.adapters.output.persistencia.modelos import Base
from infrastructure.adapters.output.persistencia.repositorio_consultas_postgres import (
    RepositorioConsultasPostgres,
)
from infrastructure.adapters.output.persistencia.repositorio_fuentes_postgres import (
    RepositorioFuentesPostgres,
)
from infrastructure.config import configuracion

log = logging.getLogger(__name__)


class Contenedor:
    def __init__(self):
        self.corpus = CorpusJsonl(configuracion.ruta_corpus)
        self.indice = IndiceHibridoLexico()
        total = self.indice.indexar(self.corpus.cargar())
        log.info("Indice construido con %s fragmentos", total)

        self.extractor = ExtractorPdf()

        self.generador = OllamaGenerador(
            url_base=configuracion.ollama_url, modelo=configuracion.ollama_modelo
        )
        self.traductor = OllamaTraductor(
            url_base=configuracion.ollama_url, modelo=configuracion.ollama_modelo
        )
        self.evaluador = EvaluadorConfianza(umbral=configuracion.umbral_abstencion)
        self.detector = DetectorIdiomaHeuristico()

        self.repositorio_consultas = None
        self.gestionar_fuentes = None
        self.repositorio_fuentes = None
        self.base_datos_disponible = self._conectar_base_datos()

        self.ingestar_documento = IngestarDocumentoUseCase(
            extractor=self.extractor,
            corpus=self.corpus,
            indice=self.indice,
            repositorio_fuentes=self.repositorio_fuentes,
        )

        self.consultar_corpus = ConsultarCorpusUseCase(
            indice=self.indice,
            generador=self.generador,
            evaluador=self.evaluador,
            detector_idioma=self.detector,
            repositorio=self.repositorio_consultas,
            traductor=self.traductor,
            k=configuracion.fragmentos_recuperados,
        )

    def _conectar_base_datos(self) -> bool:
        try:
            motor = create_engine(configuracion.url_base_datos, pool_pre_ping=True)
            with motor.connect() as conexion:
                conexion.execute(text("SELECT 1"))
            Base.metadata.create_all(motor)
            sesion = sessionmaker(motor, expire_on_commit=False)
            self.repositorio_consultas = RepositorioConsultasPostgres(sesion)
            self.repositorio_fuentes = RepositorioFuentesPostgres(sesion)
            self.gestionar_fuentes = GestionarFuentesUseCase(self.repositorio_fuentes)
            log.info("Base de datos conectada")
            return True
        except Exception as exc:  # noqa: BLE001
            # El sistema sigue respondiendo consultas sin persistencia: la recuperacion y la
            # salvaguarda no dependen de la base de datos. Se pierde el historial (RF-11) y
            # el registro que alimentara los modelos predictivos del PMV2.
            log.warning("Sin base de datos, se opera sin historial: %s", exc)
            return False
