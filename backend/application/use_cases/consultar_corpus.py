from application.services.depurador_consulta import DepuradorConsulta
from application.services.evaluador_confianza import EvaluadorConfianza
from domain.entities.consulta import Consulta
from domain.entities.fragmento import FragmentoRecuperado
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
        "No propongo ninguna traducción, para evitar introducir una forma no documentada."
    ),
    Idioma.INGLES: (
        "I have no documentary support for that query in the indexed corpus. "
        "I will not propose a translation, to avoid introducing an undocumented form."
    ),
}

MENSAJE_IDIOMA = (
    "Solo se admiten consultas en español o en inglés. "
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
        depurador: DepuradorConsulta | None = None,
        k: int = 5,
    ):
        self._indice = indice
        self._generador = generador
        self._evaluador = evaluador
        self._detector = detector_idioma
        self._repositorio = repositorio
        self._traductor = traductor
        self._depurador = depurador or DepuradorConsulta()
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
            # Se traduce la consulta ya depurada, es decir el termino solo y no la pregunta
            # completa. Traducir la frase entera devuelve el fraseo en espanol ("como se
            # dice X en quechua de Wanka"), que reintroduce en la consulta las palabras que
            # la depuracion existe para eliminar y hunde la similitud del fragmento.
            consulta.texto_traducido = self._traductor.traducir_al_espanol(
                self._depurador.depurar(consulta.texto)
            )

        recuperados = self._recuperar_con_variantes(consulta)
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
                    consulta_traducida=consulta.texto_traducido,
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
                consulta_traducida=consulta.texto_traducido,
            ),
        )

    def _recuperar_con_variantes(self, consulta: Consulta) -> list[FragmentoRecuperado]:
        """Recupera con la consulta original y, si la hay, con su traduccion, conservando
        para cada fragmento la mejor de las dos puntuaciones.

        Buscar con ambas es lo que impide que una traduccion defectuosa anule el resultado:
        en el peor caso degrada al comportamiento que ya se tenia sin traducir."""
        variantes = [consulta.texto]
        if consulta.texto_traducido and consulta.texto_traducido != consulta.texto:
            variantes.append(consulta.texto_traducido)

        mejores: dict[str, FragmentoRecuperado] = {}
        for variante in variantes:
            for recuperado in self._indice.recuperar(variante, k=self._k):
                previo = mejores.get(recuperado.id)
                if previo is None or self._orden(recuperado) > self._orden(previo):
                    mejores[recuperado.id] = recuperado

        return sorted(mejores.values(), key=self._orden, reverse=True)[: self._k]

    @staticmethod
    def _orden(recuperado: FragmentoRecuperado) -> tuple[bool, float]:
        return (recuperado.coincidencia_lema, recuperado.puntuacion.valor)

    def _registrar(self, consulta: Consulta, respuesta: Respuesta) -> Respuesta:
        if self._repositorio is not None:
            self._repositorio.registrar(consulta, respuesta)
        return respuesta
