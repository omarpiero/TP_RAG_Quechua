"""Reproduce el experimento E7: traducir la consulta al español antes de recuperar.

Mide el subconjunto D (inglés) con y sin traducción previa, y comprueba si el umbral
calibrado sobre consultas en español sigue siendo válido una vez incorporada la traducción.
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from application.services.depurador_consulta import DepuradorConsulta  # noqa: E402
from application.services.evaluador_confianza import (  # noqa: E402
    UMBRAL_CALIBRADO,
    EvaluadorConfianza,
)
from application.use_cases.consultar_corpus import ConsultarCorpusUseCase  # noqa: E402
from domain.entities.consulta import Consulta  # noqa: E402
from domain.value_objects.idioma import Idioma  # noqa: E402
from infrastructure.adapters.output.corpus_jsonl import cargar_fragmentos  # noqa: E402
from infrastructure.adapters.output.detector_idioma_heuristico import (  # noqa: E402
    DetectorIdiomaHeuristico,
)
from infrastructure.adapters.output.indice_hibrido_lexico import (  # noqa: E402
    IndiceHibridoLexico,
)
from infrastructure.adapters.output.ollama_traductor import OllamaTraductor  # noqa: E402

DATOS = RAIZ / "data"


class GeneradorNulo:
    def redactar(self, consulta, fragmentos, idioma):
        return ""

    def disponible(self):
        return True


def medir(caso_uso, consulta_texto, oro, traduccion=None):
    consulta = Consulta(texto=consulta_texto, idioma=Idioma.INGLES)
    consulta.texto_traducido = traduccion
    recuperados = caso_uso._recuperar_con_variantes(consulta)
    ids = [r.id for r in recuperados]
    posicion = next((p for p, fid in enumerate(ids, start=1) if fid in oro), None)
    return {
        "similitud_maxima": max((r.puntuacion.valor for r in recuperados), default=0.0),
        "responde": EvaluadorConfianza().evaluar(recuperados).responder,
        "recall_1": posicion == 1,
        "recall_5": posicion is not None and posicion <= 5,
    }


def main():
    indice = IndiceHibridoLexico()
    indice.indexar(cargar_fragmentos(DATOS / "fragmentos_v2.jsonl"))
    evaluacion = json.loads((DATOS / "evaluacion_v2.json").read_text(encoding="utf-8"))

    traductor = OllamaTraductor()
    caso_uso = ConsultarCorpusUseCase(
        indice=indice,
        generador=GeneradorNulo(),
        evaluador=EvaluadorConfianza(),
        detector_idioma=DetectorIdiomaHeuristico(),
        traductor=traductor,
    )

    ingles = [c for c in evaluacion if c["subconjunto"] == "D_ingles"]
    print(f"Traduciendo y evaluando {len(ingles)} consultas en ingles...\n")

    sin_traducir, con_traducir, latencias = [], [], []
    muestra = []

    for caso in ingles:
        oro = set(caso.get("oro", []))
        sin_traducir.append(medir(caso_uso, caso["consulta"], oro))

        inicio = time.perf_counter()
        traduccion = traductor.traducir_al_espanol(
            DepuradorConsulta().depurar(caso["consulta"])
        )
        latencias.append(time.perf_counter() - inicio)

        con_traducir.append(medir(caso_uso, caso["consulta"], oro, traduccion))
        if len(muestra) < 8:
            muestra.append((caso["consulta"], traduccion, caso["forma_esperada"]))

    print("MUESTRA DE TRADUCCIONES")
    for original, traducida, esperada in muestra:
        print(f"  {original}")
        print(f"     -> '{traducida}'   (forma esperada en el corpus: {esperada})")
    print()

    def resumen(nombre, datos):
        print(
            f"{nombre:<22}"
            f"recall@1 {np.mean([d['recall_1'] for d in datos]):.3f}   "
            f"recall@5 {np.mean([d['recall_5'] for d in datos]):.3f}   "
            f"atendidas {np.mean([d['responde'] for d in datos]):.3f}   "
            f"sim.media {np.mean([d['similitud_maxima'] for d in datos]):.3f}"
        )

    print("SUBCONJUNTO D (ingles)")
    resumen("sin traduccion", sin_traducir)
    resumen("con traduccion", con_traducir)
    print(f"\nLatencia de traduccion: media {np.mean(latencias):.2f} s, "
          f"max {np.max(latencias):.2f} s")

    negativos = [c for c in evaluacion if c["subconjunto"] == "C_fuera_de_cobertura"]
    sim_neg = np.array(
        [
            max(
                (r.puntuacion.valor for r in indice.recuperar(c["consulta"], k=5)),
                default=0.0,
            )
            for c in negativos
        ]
    )
    sim_pos_d = np.array([d["similitud_maxima"] for d in con_traducir])

    print("\nEFECTO SOBRE EL UMBRAL")
    print(f"  ingles traducido: media {sim_pos_d.mean():.3f}  min {sim_pos_d.min():.3f}")
    print(f"  fuera de cobertura: media {sim_neg.mean():.3f}  max {sim_neg.max():.3f}")
    atendidas = int((sim_pos_d >= UMBRAL_CALIBRADO).sum())
    falsos = int((sim_neg >= UMBRAL_CALIBRADO).sum())
    print(f"  con el umbral actual ({UMBRAL_CALIBRADO}): "
          f"{atendidas}/{len(sim_pos_d)} atendidas, {falsos} falsos positivos")


if __name__ == "__main__":
    main()
