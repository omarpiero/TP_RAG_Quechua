from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from domain.entities.consulta import Consulta
from domain.entities.fragmento import Fragmento, FragmentoRecuperado, TipoFragmento
from domain.entities.respuesta import Respuesta
from domain.ports.repositorio_consultas_port import RepositorioConsultasPort
from domain.value_objects.idioma import Idioma
from domain.value_objects.procedencia import Procedencia
from domain.value_objects.puntuacion_similitud import PuntuacionSimilitud
from infrastructure.adapters.output.persistencia.modelos import ConsultaORM, RespaldoORM


class RepositorioConsultasPostgres(RepositorioConsultasPort):
    def __init__(self, sesion: sessionmaker[Session]):
        self._sesion = sesion

    def registrar(self, consulta: Consulta, respuesta: Respuesta) -> None:
        with self._sesion() as s, s.begin():
            s.add(
                ConsultaORM(
                    id=consulta.id,
                    texto=consulta.texto,
                    idioma=consulta.idioma.value,
                    texto_traducido=consulta.texto_traducido,
                    momento=consulta.momento,
                    respuesta_texto=respuesta.texto,
                    abstenida=respuesta.abstenida,
                    similitud_maxima=respuesta.similitud_maxima,
                    respaldos=[
                        RespaldoORM(
                            fragmento_id=r.id,
                            documento=r.procedencia.documento,
                            pagina=r.procedencia.pagina,
                            texto=r.texto,
                            puntuacion=r.puntuacion.valor,
                            derivado_ocr=r.procedencia.derivado_ocr,
                        )
                        for r in respuesta.respaldo
                    ],
                )
            )

    def historial(self, limite: int = 50) -> list[tuple[Consulta, Respuesta]]:
        with self._sesion() as s:
            registros = s.scalars(
                select(ConsultaORM).order_by(ConsultaORM.momento.desc()).limit(limite)
            ).all()
            return [self._a_dominio(r) for r in registros]

    def no_cubiertas(self, limite: int = 500) -> list[Consulta]:
        with self._sesion() as s:
            registros = s.scalars(
                select(ConsultaORM)
                .where(ConsultaORM.abstenida.is_(True))
                .order_by(ConsultaORM.momento.desc())
                .limit(limite)
            ).all()
            return [self._a_dominio(r)[0] for r in registros]

    def total_registradas(self) -> int:
        with self._sesion() as s:
            return s.scalar(select(func.count()).select_from(ConsultaORM)) or 0

    @staticmethod
    def _a_dominio(r: ConsultaORM) -> tuple[Consulta, Respuesta]:
        consulta = Consulta(
            id=r.id,
            texto=r.texto,
            idioma=Idioma(r.idioma),
            momento=r.momento,
            texto_traducido=r.texto_traducido,
        )
        respaldo = [
            FragmentoRecuperado(
                fragmento=Fragmento(
                    id=b.fragmento_id,
                    texto=b.texto,
                    procedencia=Procedencia(b.documento, b.pagina, b.derivado_ocr),
                    tipo=TipoFragmento.LEXICOGRAFICO,
                ),
                puntuacion=PuntuacionSimilitud(b.puntuacion),
            )
            for b in r.respaldos
        ]
        respuesta = Respuesta(
            consulta_id=r.id,
            texto=r.respuesta_texto,
            respaldo=respaldo,
            abstenida=r.abstenida,
            idioma=Idioma(r.idioma),
            similitud_maxima=r.similitud_maxima,
            momento=r.momento,
        )
        return consulta, respuesta
