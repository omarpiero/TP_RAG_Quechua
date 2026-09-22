"""Evaluacion completa del pipeline destinado al telefono, sobre los 248 casos.

Reune las tres piezas decididas en la fase 0 y las mide juntas, que es lo unico que
demuestra que no se estropean entre si: recuperacion lexica exportada, traduccion por tabla
precalculada y extraccion determinista de la entrada. Ningun modelo interviene.
"""

import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np

from application.services.depurador_consulta import DepuradorConsulta
from domain.entities.fragmento import TipoFragmento
from infrastructure.adapters.output.corpus_jsonl import cargar_fragmentos
from infrastructure.adapters.output.indice_hibrido_lexico import IndiceHibridoLexico

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validar_tabla_ingles import TraductorTabla, normalizar  # noqa: E402

CABECERA = re.compile(r"(?=\b[A-ZÁÉÍÓÚÜÑ][A-ZÁÉÍÓÚÜÑ\s\-]{1,30}:)")
ENTRADA = re.compile(r"\s*([A-ZÁÉÍÓÚÜÑ][A-ZÁÉÍÓÚÜÑ\s\-]*?)\s*:\s*(.*)", re.S)
UMBRAL = 0.48


def entradas_de(texto: str) -> list:
    salida = []
    for bloque in CABECERA.split(texto):
        m = ENTRADA.match(bloque)
        if not m:
            continue
        cuerpo = m.group(2)
        principal = re.split(r"\(", cuerpo)[0].strip().rstrip(".")
        formas = [f.strip() for f in principal.split(",") if f.strip()]
        subs = [
            (a.strip(), [x.strip() for x in b.strip().rstrip(".").split(",") if x.strip()])
            for a, b in re.findall(r"\(([^)]+)\)\s*([^(]*)", cuerpo)
        ]
        if formas:
            salida.append((m.group(1).strip(), formas, [s for s in subs if s[1]]))
    return salida


def main() -> int:
    raiz = Path(__file__).resolve().parents[1]
    artefactos = raiz / "artefactos_movil"

    indice = IndiceHibridoLexico()
    indice.indexar(cargar_fragmentos(raiz / "data" / "fragmentos_v2.jsonl"))
    depurador = DepuradorConsulta()
    traductor = TraductorTabla(artefactos / "traduccion_en_es.json")
    casos = json.loads((raiz / "data" / "evaluacion_v2.json").read_text("utf-8"))

    est = {}
    for caso in casos:
        sub = caso["subconjunto"]
        e = est.setdefault(sub, {"n": 0, "recall": 0, "atendidas": 0, "redacta": 0})
        e["n"] += 1

        termino = depurador.depurar(caso["consulta"])
        variantes = [termino]
        if sub == "D_ingles":
            variantes = traductor.candidatas(termino) or [termino]

        puntos = None
        for variante in variantes:
            actual = indice.puntuar(variante)
            puntos = actual if puntos is None else np.maximum(puntos, actual)
        mejores = np.argsort(-puntos)[:5]
        recuperados = [indice._fragmentos[i] for i in mejores]

        por_lema = any(
            r.coincidencia_lema
            for variante in variantes
            for r in indice.recuperar(variante, k=5)
        )
        atendida = float(puntos[mejores[0]]) >= UMBRAL or por_lema
        if atendida:
            e["atendidas"] += 1
        if caso.get("oro") and any(f.id in caso["oro"] for f in recuperados):
            e["recall"] += 1

        # Composicion determinista: se busca la entrada cuyo lema coincide con alguna
        # de las variantes de la consulta.
        if atendida and caso.get("forma_esperada"):
            objetivo = {normalizar(v) for v in variantes}
            for fragmento in recuperados:
                if fragmento.tipo is not TipoFragmento.LEXICOGRAFICO:
                    continue
                for lema, formas, subs in entradas_de(fragmento.texto):
                    if normalizar(lema) not in objetivo:
                        continue
                    todas = formas + [x for _, f in subs for x in f]
                    if normalizar(caso["forma_esperada"]) in normalizar(" ".join(todas)):
                        e["redacta"] += 1
                        break
                else:
                    continue
                break

    print(f"{'subconjunto':22s} {'n':>4s} {'recall@5':>10s} {'atendidas':>11s} {'redacta':>10s}")
    for clave in ("A_lexico_es", "B_independiente", "D_ingles", "C_fuera_de_cobertura"):
        v = est[clave]
        n = v["n"]
        if clave == "C_fuera_de_cobertura":
            print(
                f"{clave:22s} {n:4d} {'-':>10s} "
                f"{v['atendidas']:4d} falsos+ {'':>9s}"
            )
        else:
            print(
                f"{clave:22s} {n:4d} {100*v['recall']/n:9.1f}% "
                f"{100*v['atendidas']/n:10.1f}% {100*v['redacta']/n:9.1f}%"
            )
    fp = est["C_fuera_de_cobertura"]["atendidas"]
    print(f"\nFalsos positivos en C: {fp}/28")
    return 0 if fp == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
