"""Compara la recuperacion en prosa entre el corpus original y el reparado.

Misma pregunta, mismo motor, mismo umbral: lo unico que cambia es si los acentos que el
OCR separo estan o no rejuntados. El conjunto es sintetico (scripts/generar_evaluacion_
prosa.py) y sirve para comparar dos indices sobre el mismo material, no para afirmar como
pregunta un usuario real.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from infrastructure.adapters.output.corpus_jsonl import cargar_fragmentos
from infrastructure.adapters.output.indice_hibrido_lexico import IndiceHibridoLexico

UMBRAL = 0.48


def medir(ruta_corpus: Path, casos: list) -> dict:
    indice = IndiceHibridoLexico()
    indice.indexar(cargar_fragmentos(ruta_corpus))

    en_1 = en_5 = atendidas = 0
    similitudes = []
    fallos = []
    for caso in casos:
        recuperados = indice.recuperar(caso["consulta"], k=5)
        identificadores = [r.fragmento.id for r in recuperados]
        similitud = max((r.puntuacion.valor for r in recuperados), default=0.0)
        similitudes.append(similitud)
        if similitud >= UMBRAL:
            atendidas += 1
        if identificadores and identificadores[0] in caso["oro"]:
            en_1 += 1
        if any(i in caso["oro"] for i in identificadores):
            en_5 += 1
        else:
            fallos.append(caso["id"])
    n = len(casos)
    return {
        "recall@1": 100 * en_1 / n,
        "recall@5": 100 * en_5 / n,
        "atendidas": 100 * atendidas / n,
        "similitud_media": sum(similitudes) / n,
        "fallos": fallos,
    }


def main() -> int:
    raiz = Path(__file__).resolve().parents[1]
    casos = json.loads((raiz / "data" / "evaluacion_prosa.json").read_text("utf-8"))
    print(f"Conjunto de prosa: {len(casos)} preguntas sinteticas\n")

    resultados = {}
    for nombre, archivo in (
        ("v2 original", "fragmentos_v2.jsonl"),
        ("v3 reparado", "fragmentos_v3.jsonl"),
    ):
        resultados[nombre] = medir(raiz / "data" / archivo, casos)

    print(f"{'corpus':14s} {'recall@1':>9s} {'recall@5':>9s} {'atendidas':>10s} {'sim.media':>10s}")
    for nombre, r in resultados.items():
        print(
            f"{nombre:14s} {r['recall@1']:8.1f}% {r['recall@5']:8.1f}% "
            f"{r['atendidas']:9.1f}% {r['similitud_media']:10.3f}"
        )

    solo_v2 = set(resultados["v2 original"]["fallos"]) - set(resultados["v3 reparado"]["fallos"])
    solo_v3 = set(resultados["v3 reparado"]["fallos"]) - set(resultados["v2 original"]["fallos"])
    print(f"\nRescatadas por la reparacion : {len(solo_v2)}")
    print(f"Perdidas por la reparacion   : {len(solo_v3)}  {sorted(solo_v3)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
