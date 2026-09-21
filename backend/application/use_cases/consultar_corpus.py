from application.services.evaluador_confianza import EvaluadorConfianza
from domain.entities.consulta import Consulta
from domain.entities.respuesta import Respuesta
from domain.ports.detector_idioma_port import DetectorIdiomaPort
from domain.ports.generador_texto_port import GeneradorTextoPort
from domain.ports.indice_recuperacion_port import IndiceRecuperacionPort
from domain.ports.repositorio_consultas_port import RepositorioConsultasPort
from domain.ports.traductor_port import TraductorPort
from domain.value_objects.idioma import Idioma

MENSAJE_SIN_RESPALDO = {
    Idioma.ESPANOL: (
        "No dispongo de respaldo documental para esa consulta en el corpus indexado. "
        "No propongo ninguna traduccion para evitar introducir una forma no documentada."
    ),
    Idioma.INGLES: (
        "I have no documentary support for that query in the indexed corpus. "
        "I will not propose a translation, to avoid introducing an undocumented form."
    ),
}

MENSAJE_IDIOMA = (
    "Solo se admiten consultas en espanol o en ingles. "
    "Only queries in Spanish or English are supported."
)


class ConsultarCorpusUseCase:
    """HU-03 (consulta lexica), HU-06 (salvaguarda antialucinacion) y HU-07 (trazabilidad).

    El orden importa: la decision de abstenerse se toma ANTES de invocar al generador, de
    modo que ante una consulta sin respaldo el modelo de lenguaje no llega a ejecutarse y
    no tiene ocasion de inventar una forma."""

    def __init__(
        self,
        indice: IndiceRecuperacionPort,
        generador: GeneradorTextoPort,
        evaluador: EvaluadorConfianza,
        detector_idioma: DetectorIdiomaPort,
        repositorio: RepositorioConsultasPort | None = None,
        traductor: TraductorPort | None = None,
        k: int = 5,
    ):
        self._indice = indice
        self._generador = generador
        self._evaluador = evaluador
        self._detector = detector_idioma
        self._repositorio = repositorio
        self._traductor = traductor
        self._k = k

    def ejecutar(self, texto_consulta: str) -> Respuesta:
        idioma = self._detector.detectar(texto_consulta)
        consulta = Consulta(texto=texto_consulta, idioma=idioma)

        if not idioma.soportado:
            return self._registrar(
                consulta,
                Respuesta(
                    consulta_id=consulta.id,
                    texto=MENSAJE_IDIOMA,
                    abstenida=True,
                    idioma=idioma,
                ),
            )

        if idioma is Idioma.INGLES and self._traductor is not None:
            consulta.texto_traducido = self._traductor.traducir_al_espanol(consulta.texto)

        recuperados = self._indice.recuperar(consulta.texto_para_recuperar, k=self._k)
        veredicto = self._evaluador.evaluar(recuperados)

        if not veredicto.responder:
            return self._registrar(
                consulta,
                Respuesta(
                    consulta_id=consulta.id,
                    texto=MENSAJE_SIN_RESPALDO[idioma],
                    abstenida=True,
                    idioma=idioma,
                    similitud_maxima=veredicto.similitud_maxima,
                ),
            )

        respaldo = [
            r
            for r in recuperados
            if r.coincidencia_lema or r.puntuacion.valor >= self._evaluador.umbral
        ]
        texto = self._generador.redactar(consulta.texto, respaldo, idioma)

        return self._registrar(
            consulta,
            Respuesta(
                consulta_id=consulta.id,
                texto=texto,
                respaldo=respaldo,
                abstenida=False,
                idioma=idioma,
                similitud_maxima=veredicto.similitud_maxima,
            ),
        )

    def _registrar(self, consulta: Consulta, respuesta: Respuesta) -> Respuesta:
        if self._repositorio is not None:
            self._repositorio.registrar(consulta, respuesta)
        return respuesta
