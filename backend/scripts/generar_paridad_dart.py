"""Emite las puntuaciones de referencia con las que la implementacion en Dart se compara.

El motor del telefono no reimplementa el ajuste, pero si reimplementa la preparacion de la
consulta: la depuracion, la tokenizacion por palabras y el analizador char_wb de
scikit-learn. Cualquier diferencia en esos tres pasos desplaza las puntuaciones y con ellas
el umbral calibrado, de modo que la equivalencia hay que demostrarla, no suponerla.

La salida se consume desde movil/test/paridad_test.dart.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from application.services.depurador_consulta import DepuradorConsulta
from infrastructure.adapters.output.corpus_jsonl import cargar_fragmentos
from infrastructure.adapters.output.indice_hibrido_lexico import IndiceHibridoLexico

CORPUS = "fragmentos_v3.jsonl"

# Consultas escogidas por lo que ponen a prueba, no al azar.
CONSULTAS = [
    # Depuracion del fraseo y coincidencia de lema por debajo del umbral.
    "como se dice perro en quechua wanka",
    "¿cómo se dice agua?",
    "casa",
    # Acentos y ñ: la normalizacion que Dart resuelve con una tabla, no con NFD.
    "¿cómo se dice niño en quechua wanka?",
    "corazón",
    "araña",
    # Terminos que solo casan por n-gramas de caracteres.
    "allqu",
    "yaku",
    # Prosa, donde la consulta es larga y la similitud baja.
    "como se forma el plural de los pronombres",
    "que es el sufijo ablativo",
    # Fuera de cobertura: la abstencion tiene que coincidir tambien.
    "cual es la capital de francia",
    "panel solar",
    # Consulta que era solo fraseo: el depurador la devuelve intacta.
    "en quechua wanka",
    # Ingles, que la tabla traduce antes de llegar al indice.
    "love",
    "how do you say water in wanka quechua",
]


def main() -> int:
    raiz = Path(__file__).resolve().parents[1]
    indice = IndiceHibridoLexico()
    indice.indexar(cargar_fragmentos(raiz / "data" / CORPUS))
    depurador = DepuradorConsulta()

    casos = []
    for consulta in CONSULTAS:
        recuperados = indice.recuperar(consulta, k=5)
        casos.append(
            {
                "consulta": consulta,
                "depurada": depurador.depurar(consulta),
                "es_lema": indice.es_lema(depurador.depurar(consulta)),
                "similitud_maxima": round(
                    max((r.puntuacion.valor for r in recuperados), default=0.0), 6
                ),
                "top": [
                    {
                        "id": r.id,
                        "puntuacion": round(r.puntuacion.valor, 6),
                        "lema": r.coincidencia_lema,
                    }
                    for r in recuperados
                ],
                "prosa": [
                    {"id": r.id, "puntuacion": round(r.puntuacion.valor, 6)}
                    for r in indice.recuperar_prosa(consulta, k=3)
                ],
            }
        )

    destino = raiz.parent / "movil" / "test" / "paridad_esperada.json"
    destino.write_text(json.dumps(casos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(casos)} casos escritos en {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
