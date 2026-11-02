"""Mediciones en la nube sin modificar nada (informe de la semana 12).

frio:    espera 16 min sin trafico y mide GET /api/estado hasta el primer 200 (N repeticiones).
paridad: las 248 consultas del arnes contra POST /api/predicciones (no invoca a Gemini ni registra)
         y las compara con el predictor local sobre el corpus v3 de esta PC.
comparar: 10 consultas de A y 10 de C (semilla 2026) con POST /api/consultas en la nube, marcadas con
         TOKEN_PRUEBAS como `humo`, frente al mismo caso de uso local con generador literal.

Solo guarda identificadores y cifras: nunca texto del corpus. No usa ni imprime secretos.

Uso, desde backend/:
    python scripts/medir_nube_u3.py frio <carpeta> [repeticiones]
    python scripts/medir_nube_u3.py paridad <carpeta> [pausa_s]
    python scripts/medir_nube_u3.py comparar <carpeta> [pausa_s]
"""

import json
import os
import random
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

API = "https://quechua-api.onrender.com"
RAIZ = Path(__file__).resolve().parents[1]
PARTICION = {
    "A_lexico_es": "A",
    "B_independiente": "B",
    "C_fuera_de_cobertura": "C",
    "D_ingles": "D",
}


def percentil(valores, q):
    orden = sorted(valores)
    return orden[min(len(orden) - 1, round(q * (len(orden) - 1)))]


def solo_cifras(respuesta):
    """Aplana la respuesta conservando solo numeros y booleanos: ningun texto del corpus."""
    plano = {}

    def recorrer(prefijo, valor):
        if isinstance(valor, dict):
            for clave, sub in valor.items():
                recorrer(f"{prefijo}.{clave}" if prefijo else clave, sub)
        elif isinstance(valor, (bool, int, float)) or valor is None:
            plano[prefijo] = valor

    recorrer("", respuesta)
    return plano


def frio(carpeta: Path, repeticiones: int) -> None:
    resultados = []
    for i in range(repeticiones):
        print(f"[frio] esperando 16 min sin trafico ({i + 1}/{repeticiones})", flush=True)
        time.sleep(16 * 60)
        inicio = time.perf_counter()
        intentos = 0
        codigo = None
        while time.perf_counter() - inicio < 300:
            intentos += 1
            try:
                codigo = httpx.get(f"{API}/api/estado", timeout=120).status_code
                if codigo == 200:
                    break
            except httpx.HTTPError:
                codigo = None
            time.sleep(1)
        segundos = round(time.perf_counter() - inicio, 2)
        resultados.append(
            {
                "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "segundos_hasta_200": segundos,
                "intentos": intentos,
                "codigo": codigo,
            }
        )
        print(f"[frio] {resultados[-1]}", flush=True)
        (carpeta / "arranque_frio.json").write_text(json.dumps(resultados, indent=1), encoding="utf-8")


def paridad(carpeta: Path, pausa: float) -> None:
    sys.path.insert(0, str(RAIZ / "src"))
    from infrastructure.contenedor import Contenedor

    local = Contenedor(generador="literal").predecir_consulta
    casos = json.loads((RAIZ / "data" / "evaluacion_v2.json").read_text(encoding="utf-8"))
    filas = []
    with httpx.Client(base_url=API, timeout=120) as cliente:
        for caso in casos:
            inicio = time.perf_counter()
            respuesta = cliente.post("/api/predicciones", json={"texto": caso["consulta"]})
            ms = (time.perf_counter() - inicio) * 1000
            nube = solo_cifras(respuesta.json()) if respuesta.status_code == 200 else {}
            propia = solo_cifras(local.ejecutar(caso["consulta"]))
            diferencias = {
                clave: (nube.get(clave), propia.get(clave))
                for clave in set(nube) | set(propia)
                if isinstance(propia.get(clave), (int, float, bool))
                and not (
                    isinstance(nube.get(clave), (int, float))
                    and isinstance(propia.get(clave), (int, float))
                    and abs(nube[clave] - propia[clave]) < 1e-6
                )
            }
            filas.append(
                {
                    "id": caso["id"],
                    "particion": PARTICION[caso["subconjunto"]],
                    "http": respuesta.status_code,
                    "ms": round(ms, 1),
                    "nube": nube,
                    "local": propia,
                    "diferencias": diferencias,
                }
            )
            time.sleep(pausa)
    (carpeta / "paridad_por_consulta.json").write_text(
        json.dumps(filas, ensure_ascii=False, indent=0), encoding="utf-8"
    )
    tiempos = [f["ms"] for f in filas if f["http"] == 200]
    por_particion = {}
    for p in "ABCD":
        grupo = [f for f in filas if f["particion"] == p]
        por_particion[p] = {
            "n": len(grupo),
            "http_200": sum(f["http"] == 200 for f in grupo),
            "identicas_a_local": sum(f["http"] == 200 and not f["diferencias"] for f in grupo),
        }
    resumen = {
        "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n": len(filas),
        "p50_ms": round(statistics.median(tiempos), 1) if tiempos else None,
        "p95_ms": round(percentil(tiempos, 0.95), 1) if tiempos else None,
        "por_particion": por_particion,
        "campos_con_diferencia": sorted({c for f in filas for c in f["diferencias"]}),
    }
    (carpeta / "paridad_resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(json.dumps(resumen, ensure_ascii=False))


def comparar(carpeta: Path, pausa: float) -> None:
    token = os.environ["TOKEN_PRUEBAS"]
    os.environ["RUTA_SQLITE"] = str(carpeta / "_comparar_temporal.db")
    sys.path.insert(0, str(RAIZ / "src"))
    from infrastructure.contenedor import Contenedor

    local = Contenedor(generador="literal")
    casos = json.loads((RAIZ / "data" / "evaluacion_v2.json").read_text(encoding="utf-8"))
    azar = random.Random(2026)
    grupo = lambda letra: sorted(
        [c for c in casos if c["subconjunto"].startswith(letra)], key=lambda c: c["id"]
    )
    muestra = azar.sample(grupo("A"), 10) + azar.sample(grupo("C"), 10)
    cabeceras = {"X-Origen-Consultas": "humo", "X-Token-Pruebas": token}
    filas = []
    with httpx.Client(base_url=API, timeout=120, headers=cabeceras) as cliente:
        for caso in muestra:
            inicio = time.perf_counter()
            respuesta = cliente.post("/api/consultas", json={"texto": caso["consulta"]})
            ms = (time.perf_counter() - inicio) * 1000
            nube = respuesta.json()
            inicio = time.perf_counter()
            propia = local.consultar_corpus.ejecutar(caso["consulta"])
            ms_local = (time.perf_counter() - inicio) * 1000
            prediccion = solo_cifras(local.predecir_consulta.ejecutar(caso["consulta"]))
            prediccion_nube = solo_cifras(
                cliente.post("/api/predicciones", json={"texto": caso["consulta"]}).json()
            )
            filas.append(
                {
                    "id": caso["id"],
                    "particion": caso["subconjunto"][0],
                    "nube": {
                        "ms_cliente": round(ms, 1),
                        "decision": "abstiene" if nube.get("abstenida") else "responde",
                        "via": nube.get("via_respaldo"),
                        "similitud": nube.get("similitud_maxima"),
                        "prediccion": prediccion_nube,
                    },
                    "local_literal": {
                        "ms": round(ms_local, 1),
                        "decision": "abstiene" if propia.abstenida else "responde",
                        "via": propia.via_respaldo,
                        "similitud": round(propia.similitud_maxima, 4),
                        "prediccion": prediccion,
                    },
                }
            )
            time.sleep(pausa)
    (carpeta / "comparacion_local_nube.json").write_text(
        json.dumps(filas, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    iguales = sum(f["nube"]["decision"] == f["local_literal"]["decision"] for f in filas)
    print(json.dumps({"n": len(filas), "misma_decision": iguales}))


if __name__ == "__main__":
    modo, salida = sys.argv[1], Path(sys.argv[2])
    salida.mkdir(parents=True, exist_ok=True)
    if modo == "frio":
        frio(salida, int(sys.argv[3]) if len(sys.argv) > 3 else 2)
    elif modo == "comparar":
        comparar(salida, float(sys.argv[3]) if len(sys.argv) > 3 else 5.0)
    else:
        paridad(salida, float(sys.argv[3]) if len(sys.argv) > 3 else 0.3)
