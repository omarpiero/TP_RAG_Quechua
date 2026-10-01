import logging

from application.ports import ConsultarCorpusPort
from application.ports.out.detector_idioma_port import DetectorIdiomaPort
from application.ports.out.generador_texto_port import GeneradorTextoPort
from application.ports.out.indice_recuperacion_port import IndiceRecuperacionPort
from application.ports.out.repositorio_consultas_port import RepositorioConsultasPort
from application.ports.out.traductor_port import TraductorPort
from domain.entities.consulta import Consulta
from domain.entities.fragmento import FragmentoRecuperado
from domain.entities.respuesta import Respuesta
from domain.services.depurador_consulta import DepuradorConsulta
from domain.services.evaluador_confianza import EvaluadorConfianza
from domain.value_objects.idioma import Idioma

log = logging.getLogger("rag.caso_uso")

MENSAJE_CON_PASAJES = {
    Idioma.ESPANOL: (
        "No tengo una respuesta confirmada para esa consulta. Estos pasajes del corpus "
        "podrían tratarla; léelos y juzga tú."
    ),
    Idioma.INGLES: (
        "I have no confirmed answer for that query. These passages from the corpus may "
        "deal with it; read them and judge for yourself."
    ),
}
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


class ConsultarCorpusUseCase(ConsultarCorpusPort):
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
        log.info("[CASO-USO] ConsultarCorpus: idioma=%s", idioma.value)

        if not idioma.soportado:
            log.info("[GENERADOR] NO invocado (idioma no soportado)")
            return self._registrar(
                consulta,
                Respuesta(
                    consulta_id=consulta.id,
                    texto=MENSAJE_IDIOMA,
                    abstenida=True,
                    idioma=idioma,
                ),
            )

        if self._traductor is not None:
            # Se traduce la consulta ya depurada, es decir el termino solo y no la pregunta
            # completa. Traducir la frase entera devuelve el fraseo en espanol ("como se
            # dice X en quechua de Wanka"), que reintroduce en la consulta las palabras que
            # la depuracion existe para eliminar y hunde la similitud del fragmento.
            termino = self._depurador.depurar(consulta.texto)
            candidatas = self._traductor.candidatas(
                termino, aproximar=idioma is Idioma.INGLES
            )

            # Una palabra inglesa suelta ("love") no trae ninguna marca funcional que
            # contar, de modo que el detector la asume espanola y nunca se traducia. Si el
            # termino no encabeza ninguna entrada del corpus pero si figura en la tabla
            # como palabra inglesa, la evidencia lexica pesa mas que la heuristica.
            if (
                candidatas
                and idioma is Idioma.ESPANOL
                and termino not in candidatas
                and not self._indice.es_lema(termino)
            ):
                idioma = Idioma.INGLES
                consulta.idioma = idioma
                candidatas = self._traductor.candidatas(termino, aproximar=True)

            consulta.variantes = candidatas
            log.info("[TRADUCTOR] lecturas candidatas=%d", len(candidatas))

        recuperados, origen = self._recuperar_con_variantes(consulta)
        if recuperados and consulta.variantes:
            # Se informa de la variante que realmente sostiene la respuesta, no de la
            # primera de la lista: las candidatas salen en orden alfabetico, de modo que
            # "boiled corn" anunciaba haber buscado "comijn" cuando el fragmento que
            # respondia lo habia encontrado "mote".
            ganadora = origen.get(recuperados[0].id)
            if ganadora and ganadora != consulta.texto:
                consulta.texto_traducido = ganadora
        log.info(
            "[INDICE] k=%d recuperados=%d sim_max=%.3f%s",
            self._k,
            len(recuperados),
            max((r.puntuacion.valor for r in recuperados), default=0.0),
            self._cita_mejor(recuperados),
        )
        veredicto = self._evaluador.evaluar(recuperados)
        log.info(
            "[EVALUADOR] responder=%s via=%s tau=%.2f",
            veredicto.responder,
            "lema" if veredicto.por_lema else ("similitud" if veredicto.responder else "ninguna"),
            veredicto.umbral,
        )

        if not veredicto.responder:
            # Antes de abstenerse del todo se busca en la prosa, que se consulta aparte
            # porque las entradas de diccionario, mucho mas cortas, copan siempre las
            # primeras posiciones. Lo recuperado no se afirma: se entrega literal y citado.
            pasajes = self._evaluador.ofrecer_pasajes(
                self._indice.recuperar_prosa(consulta.texto_para_recuperar, k=3),
                # El solapamiento se mide contra la consulta depurada, no contra la
                # cruda: "en quechua wanka" acompana a casi toda consulta y a ningun
                # pasaje distingue, de modo que sin depurar bastaba esa palabra para
                # sacar el prologo del libro ante cualquier termino no cubierto.
                consulta=self._depurador.depurar(consulta.texto_para_recuperar),
            )
            log.info("[GENERADOR] NO invocado (sin respaldo)")
            log.info("[CASO-USO] pasajes de prosa ofrecidos=%d (no es una respuesta)", len(pasajes))
            return self._registrar(
                consulta,
                Respuesta(
                    consulta_id=consulta.id,
                    texto=(MENSAJE_CON_PASAJES if pasajes else MENSAJE_SIN_RESPALDO)[idioma],
                    abstenida=True,
                    idioma=idioma,
                    similitud_maxima=veredicto.similitud_maxima,
                    consulta_traducida=consulta.texto_traducido,
                    pasajes=pasajes,
                ),
            )

        respaldo = [
            r
            for r in recuperados
            if r.coincidencia_lema or r.puntuacion.valor >= self._evaluador.umbral
        ]
        log.info("[GENERADOR] invocado (%d fragmentos de respaldo)", len(respaldo))
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

    def _recuperar_con_variantes(
        self, consulta: Consulta
    ) -> tuple[list[FragmentoRecuperado], dict[str, str]]:
        """Recupera con la consulta original y con cada lectura espanola plausible,
        conservando para cada fragmento la mejor puntuacion obtenida.

        Buscar con todas es lo que impide que una traduccion defectuosa anule el resultado:
        en el peor caso degrada al comportamiento que ya se tenia sin traducir.

        Devuelve tambien, por fragmento, la variante que logro esa mejor puntuacion, para
        poder decir al usuario con que termino se encontro lo que se le muestra."""
        variantes = [consulta.texto]
        for candidata in consulta.variantes:
            if candidata and candidata not in variantes:
                variantes.append(candidata)

        mejores: dict[str, FragmentoRecuperado] = {}
        origen: dict[str, str] = {}
        for variante in variantes:
            for recuperado in self._indice.recuperar(variante, k=self._k):
                previo = mejores.get(recuperado.id)
                if previo is None or self._orden(recuperado) > self._orden(previo):
                    mejores[recuperado.id] = recuperado
                    origen[recuperado.id] = variante

        ordenados = sorted(mejores.values(), key=self._orden, reverse=True)[: self._k]
        return ordenados, origen

    @staticmethod
    def _orden(recuperado: FragmentoRecuperado) -> tuple[bool, float]:
        return (recuperado.coincidencia_lema, recuperado.puntuacion.valor)

    @staticmethod
    def _cita_mejor(recuperados: list[FragmentoRecuperado]) -> str:
        if not recuperados:
            return ""
        mejor = recuperados[0]
        return f" mejor={mejor.id} ({mejor.procedencia.documento}, p. {mejor.procedencia.pagina})"

    def _registrar(self, consulta: Consulta, respuesta: Respuesta) -> Respuesta:
        if self._repositorio is not None:
            self._repositorio.registrar(consulta, respuesta)
            log.info(
                "[REPOSITORIO] registrada consulta_id=%s abstenida=%s",
                consulta.id,
                respuesta.abstenida,
            )
        else:
            log.info("[REPOSITORIO] omitido (sin base de datos)")
        return respuesta
