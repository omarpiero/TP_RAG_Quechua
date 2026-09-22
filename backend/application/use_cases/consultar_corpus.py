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

        recuperados, origen = self._recuperar_con_variantes(consulta)
        if recuperados and consulta.variantes:
            # Se informa de la variante que realmente sostiene la respuesta, no de la
            # primera de la lista: las candidatas salen en orden alfabetico, de modo que
            # "boiled corn" anunciaba haber buscado "comijn" cuando el fragmento que
            # respondia lo habia encontrado "mote".
            ganadora = origen.get(recuperados[0].id)
            if ganadora and ganadora != consulta.texto:
                consulta.texto_traducido = ganadora
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

    def _registrar(self, consulta: Consulta, respuesta: Respuesta) -> Respuesta:
        if self._repositorio is not None:
            self._repositorio.registrar(consulta, respuesta)
        return respuesta
