"""Verificacion del comportamiento medido en la prueba de concepto.

Los criterios que se comprueban aqui son los que el Documento 6 comprometio antes de
ejecutar el experimento: recall@5 sobre las consultas con respaldo, ausencia total de
falsos positivos y conservacion de al menos el 70 % de las consultas atendibles.
"""

from application.services.evaluador_confianza import UMBRAL_CALIBRADO, EvaluadorConfianza

POSITIVOS = ("A_lexico_es", "B_independiente")


def _casos(evaluacion, *subconjuntos):
    return [c for c in evaluacion if c["subconjunto"] in subconjuntos]


def test_corpus_completo(fragmentos):
    assert len(fragmentos) == 3605


def test_todo_fragmento_conserva_procedencia(fragmentos):
    # RNF-08: sin documento y pagina, ninguna respuesta puede citarse en la fuente original.
    for f in fragmentos:
        assert f.procedencia.documento
        assert f.procedencia.pagina >= 1


def test_recall_5_en_consultas_con_respaldo(indice, evaluacion):
    casos = _casos(evaluacion, *POSITIVOS)
    aciertos = 0
    for caso in casos:
        recuperados = indice.recuperar(caso["consulta"], k=5)
        ids = {r.id for r in recuperados}
        if ids & set(caso["oro"]):
            aciertos += 1
    recall = aciertos / len(casos)
    assert recall >= 0.80, f"recall@5={recall:.3f} por debajo del criterio comprometido"


def test_sin_falsos_positivos_fuera_de_cobertura(indice, evaluacion):
    evaluador = EvaluadorConfianza()
    falsos_positivos = []
    for caso in _casos(evaluacion, "C_fuera_de_cobertura"):
        recuperados = indice.recuperar(caso["consulta"], k=5)
        if evaluador.evaluar(recuperados).responder:
            falsos_positivos.append(caso["consulta"])
    assert not falsos_positivos, (
        f"El sistema respondio a {len(falsos_positivos)} consultas sin respaldo "
        f"documental: {falsos_positivos[:3]}"
    )


def test_recall_conservado_en_el_punto_de_operacion(indice, evaluacion):
    evaluador = EvaluadorConfianza()
    casos = _casos(evaluacion, *POSITIVOS)
    atendidas = sum(
        evaluador.evaluar(indice.recuperar(c["consulta"], k=5)).responder for c in casos
    )
    conservado = atendidas / len(casos)
    # El criterio comprometido en el Documento 6 era 70 %. Con la capa de lema la medicion
    # da 100 %, de modo que el liston se fija ahi para que una regresion sea visible.
    assert conservado >= 1.0, (
        f"Solo se conserva el {conservado:.1%} de las consultas atendibles con umbral "
        f"{UMBRAL_CALIBRADO}"
    )


def test_termino_frecuente_del_corpus_se_atiende(indice):
    """Un termino muy repetido en el corpus recibe un IDF bajo y su propia entrada de
    diccionario puede quedar por debajo del umbral. La coincidencia de lema lo resuelve.
    'perro' es el ejemplo literal del criterio de aceptacion de HU-03 en el Documento 0."""
    evaluador = EvaluadorConfianza()
    for termino in ("perro", "casa", "agua"):
        veredicto = evaluador.evaluar(
            indice.recuperar(f"como se dice {termino} en quechua wanka", k=5)
        )
        assert veredicto.responder, f"El sistema se abstiene ante '{termino}'"
        assert veredicto.por_lema


def test_la_coincidencia_de_lema_no_altera_la_similitud_medida(indice):
    # La senal determinista no debe falsear la metrica sobre la que se calibro el umbral.
    recuperados = indice.recuperar("como se dice perro en quechua wanka", k=5)
    assert recuperados[0].coincidencia_lema
    assert recuperados[0].puntuacion.valor < UMBRAL_CALIBRADO


def test_abstencion_ante_nocion_ausente_del_corpus(indice):
    # "criptomoneda" es el caso que la figura 3 del Documento 6 desarrolla paso a paso.
    veredicto = EvaluadorConfianza().evaluar(
        indice.recuperar("como se dice criptomoneda en quechua wanka", k=5)
    )
    assert not veredicto.responder
