"""M5: latencia de extremo a extremo con Qwen3.5-4B real.

30 consultas (10 A, 5 B, 5 C, 10 D) en frio y en caliente.
Escribe mediciones_m5.json en la carpeta de salida.

Uso: python scripts/m5_latencia.py <carpeta_salida>
"""

import json
import random
import sys
import time
from pathlib import Path

import httpx

BASE = "http://127.0.0.1:8000/api"
SALIDA = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
EVAL = Path(__file__).resolve().parents[1] / "data" / "evaluacion_v2.json"

random.seed(42)

with open(EVAL, encoding="utf-8") as f:
    datos = json.load(f)

# Seleccionar 30 consultas
por_particion = {}
for e in datos:
    p = e["id"][0]  # A, B, C, D
    por_particion.setdefault(p, []).append(e["consulta"])

muestra = []
for part, n in [("A", 10), ("B", 5), ("C", 5), ("D", 10)]:
    pool = por_particion.get(part, [])
    muestra.extend(random.sample(pool, min(n, len(pool))))


random.shuffle(muestra)

client = httpx.Client(timeout=120.0)

def medir_lote(consultas, etiqueta):
    latencias = []
    for i, q in enumerate(consultas):
        inicio = time.perf_counter()
        r = client.post(f"{BASE}/consultas", json={"texto": q})
        lat = (time.perf_counter() - inicio) * 1000
        latencias.append(lat)
        status = r.status_code
        gen = r.json().get("generador_invocado", False) if status == 200 else False
        print(f"  [{etiqueta}] {i+1}/{len(consultas)}: {lat:.0f}ms (gen={gen}) {q[:50]}")
    latencias.sort()
    n = len(latencias)
    p50 = latencias[n // 2] if n else 0
    p95 = latencias[int(n * 0.95)] if n else 0
    return {
        "etiqueta": etiqueta,
        "n": n,
        "p50_ms": round(p50),
        "p95_ms": round(p95),
        "min_ms": round(min(latencias)) if latencias else 0,
        "max_ms": round(max(latencias)) if latencias else 0,
        "media_ms": round(sum(latencias) / n) if n else 0,
        "latencias": [round(l) for l in latencias],
    }

# Capturar ollama ps
try:
    import subprocess
    ollama_ps = subprocess.check_output(["ollama", "ps"], text=True, timeout=5)
except Exception as e:
    ollama_ps = f"error: {e}"

print("=== M5: en frio (primera ronda) ===")
frio = medir_lote(muestra, "frio")

print("\n=== M5: en caliente (segunda ronda) ===")
caliente = medir_lote(muestra, "caliente")

resultado = {
    "fecha": "2026-10-01",
    "modelo": "qwen3.5:4b",
    "n_consultas": len(muestra),
    "ollama_ps": ollama_ps.strip(),
    "frio": frio,
    "caliente": caliente,
}

SALIDA.mkdir(parents=True, exist_ok=True)
out = SALIDA / "mediciones_m5.json"
out.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nResultado en {out}")
print(f"  Frio:    P50={frio['p50_ms']}ms  P95={frio['p95_ms']}ms")
print(f"  Caliente: P50={caliente['p50_ms']}ms  P95={caliente['p95_ms']}ms")
print(f"  ollama ps: {ollama_ps.strip()[:120]}")
