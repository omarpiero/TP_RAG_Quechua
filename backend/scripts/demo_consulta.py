"""Demostracion del flujo completo sobre el corpus indexado: recuperacion, decision de
abstencion y redaccion con trazabilidad de la fuente."""

import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from application.services.evaluador_confianza import EvaluadorConfianza  # noqa: E402
from application.use_cases.consultar_corpus import ConsultarCorpusUseCase  # noqa: E402
from infrastructure.adapters.output.corpus_jsonl import cargar_fragmentos  # noqa: E402
from infrastructure.adapters.output.detector_idioma_heuristico import (  # noqa: E402
    DetectorIdiomaHeuristico,
)
from infrastructure.adapters.output.indice_hibrido_lexico import (  # noqa: E402
    IndiceHibridoLexico,
)
from infrastructure.adapters.output.ollama_generador import OllamaGenerador  # noqa: E402

CONSULTAS = [
    "¿cómo se dice zorro en quechua wanka?",
    "¿cómo se dice criptomoneda en quechua wanka?",
    "how do you say water in Wanka Quechua?",
]


def main():
    indice = IndiceHibridoLexico()
    indice.indexar(cargar_fragmentos(RAIZ / "data" / "fragmentos_v2.jsonl"))

    generador = OllamaGenerador()
    if not generador.disponible():
        print("AVISO: el servicio de Ollama no responde o el modelo no esta descargado.")
        return

    caso_uso = ConsultarCorpusUseCase(
        indice=indice,
        generador=generador,
        evaluador=EvaluadorConfianza(),
        detector_idioma=DetectorIdiomaHeuristico(),
    )

    for consulta in CONSULTAS:
        print("=" * 78)
        print(f"CONSULTA: {consulta}")
        inicio = time.perf_counter()
        respuesta = caso_uso.ejecutar(consulta)
        segundos = time.perf_counter() - inicio

        print(f"IDIOMA DETECTADO: {respuesta.idioma.nombre_legible}")
        print(f"SIMILITUD MAXIMA: {respuesta.similitud_maxima:.3f}")
        print(f"ABSTENIDA: {'si' if respuesta.abstenida else 'no'}")
        print(f"\nRESPUESTA:\n{respuesta.texto}\n")
        if respuesta.respaldo:
            print("RESPALDO DOCUMENTAL:")
            for f in respuesta.respaldo:
                print(f"  - \"{f.texto}\"")
                print(f"    {f.procedencia.citar()}  [similitud {f.puntuacion}]")
        print(f"\nTIEMPO TOTAL: {segundos:.2f} s")
        print()


if __name__ == "__main__":
    main()
