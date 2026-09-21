"""Reproduce los experimentos E4 y E6 de la prueba de concepto sobre la implementacion real.

Recorre el conjunto de evaluacion, mide la recuperacion por subconjunto y barre el umbral
para localizar el primer punto de operacion que no produce ningun falso positivo.
"""

import json
import sys
import time
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from infrastructure.adapters.output.corpus_jsonl import cargar_fragmentos  # noqa: E402
from infrastructure.adapters.output.indice_hibrido_lexico import (  # noqa: E402
    IndiceHibridoLexico,
)

DATOS = RAIZ / "data"
POSITIVOS = ("A_lexico_es", "B_independiente")
NEGATIVOS = ("C_fuera_de_cobertura",)


def evaluar_consulta(indice, consulta, oro, k_max=10):
    puntuaciones = indice.puntuar(consulta)
    orden = np.argsort(-puntuaciones)[:k_max]
    ids = [indice._fragmentos[i].id for i in orden]
    posicion = next((p for p, fid in enumerate(ids, start=1) if fid in oro), None)
    return {
        "similitud_maxima": float(puntuaciones[orden[0]]),
        "posicion": posicion,
        "recall_1": posicion == 1,
        "recall_5": posicion is not None and posicion <= 5,
        "rr": 1.0 / posicion if posicion else 0.0,
    }


def main():
    fragmentos = cargar_fragmentos(DATOS / "fragmentos_v2.jsonl")
    evaluacion = json.loads((DATOS / "evaluacion_v2.json").read_text(encoding="utf-8"))

    indice = IndiceHibridoLexico()
    inicio = time.perf_counter()
    total = indice.indexar(fragmentos)
    print(f"Indexados {total} fragmentos en {time.perf_counter() - inicio:.2f} s\n")

    resultados = []
    latencias = []
    for caso in evaluacion:
        t0 = time.perf_counter()
        medida = evaluar_consulta(indice, caso["consulta"], set(caso.get("oro", [])))
        latencias.append((time.perf_counter() - t0) * 1000)
        medida["subconjunto"] = caso["subconjunto"]
        resultados.append(medida)

    print("RECUPERACION POR SUBCONJUNTO")
    print(f"{'subconjunto':<24}{'n':>5}{'recall@1':>11}{'recall@5':>11}{'MRR@10':>10}")
    for sub in sorted({r["subconjunto"] for r in resultados}):
        grupo = [r for r in resultados if r["subconjunto"] == sub]
        if sub in NEGATIVOS:
            print(f"{sub:<24}{len(grupo):>5}{'(sin oro: fuera de cobertura)':>43}")
            continue
        r1 = np.mean([r["recall_1"] for r in grupo])
        r5 = np.mean([r["recall_5"] for r in grupo])
        mrr = np.mean([r["rr"] for r in grupo])
        print(f"{sub:<24}{len(grupo):>5}{r1:>11.3f}{r5:>11.3f}{mrr:>10.3f}")

    print(f"\nLatencia de recuperacion: media {np.mean(latencias):.1f} ms, "
          f"p95 {np.percentile(latencias, 95):.1f} ms")

    positivos = [r for r in resultados if r["subconjunto"] in POSITIVOS]
    negativos = [r for r in resultados if r["subconjunto"] in NEGATIVOS]
    sim_pos = np.array([r["similitud_maxima"] for r in positivos])
    sim_neg = np.array([r["similitud_maxima"] for r in negativos])

    print("\nSEPARACION DE SIMILITUDES")
    print(f"  con respaldo (n={len(sim_pos)}): media {sim_pos.mean():.3f}  "
          f"min {sim_pos.min():.3f}  max {sim_pos.max():.3f}")
    print(f"  sin respaldo  (n={len(sim_neg)}): media {sim_neg.mean():.3f}  "
          f"min {sim_neg.min():.3f}  max {sim_neg.max():.3f}")
    print(f"  separacion de medias: {sim_pos.mean() - sim_neg.mean():.3f}")

    print("\nBARRIDO DEL UMBRAL")
    print(f"{'umbral':>8}{'VP':>6}{'FN':>6}{'FP':>6}{'VN':>6}{'recall':>9}{'F1':>8}")
    primer_sin_fp = None
    mejor_f1 = (0.0, None)
    for umbral in np.arange(0.0, 1.001, 0.01):
        vp = int((sim_pos >= umbral).sum())
        fn = len(sim_pos) - vp
        fp = int((sim_neg >= umbral).sum())
        vn = len(sim_neg) - fp
        recall = vp / len(sim_pos)
        precision = vp / (vp + fp) if (vp + fp) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        if fp == 0 and primer_sin_fp is None:
            primer_sin_fp = (round(float(umbral), 2), vp, fn, fp, vn, recall, f1)
        if f1 > mejor_f1[0]:
            mejor_f1 = (f1, (round(float(umbral), 2), vp, fn, fp, vn, recall, f1))
        if abs(umbral * 100 % 5) < 1e-6:
            print(f"{umbral:>8.2f}{vp:>6}{fn:>6}{fp:>6}{vn:>6}{recall:>9.3f}{f1:>8.3f}")

    print("\nPUNTO DE OPERACION SIN FALSOS POSITIVOS")
    if primer_sin_fp:
        u, vp, fn, fp, vn, recall, f1 = primer_sin_fp
        print(f"  umbral = {u:.2f}")
        print(f"  VP={vp}  FN={fn}  FP={fp}  VN={vn}")
        print(f"  recall conservado = {recall:.3f}   F1 = {f1:.3f}")
    else:
        print("  NO existe umbral sin falsos positivos")

    if mejor_f1[1]:
        u, vp, fn, fp, vn, recall, f1 = mejor_f1[1]
        print(f"\n  (comparacion) umbral de F1 maximo = {u:.2f} -> "
              f"F1={f1:.3f} pero con {fp} falsos positivos")


if __name__ == "__main__":
    main()
