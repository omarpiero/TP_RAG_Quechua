"""Construye un conjunto de evaluacion para el material de prosa.

El conjunto `evaluacion_v2.json` solo contiene consultas lexicas, de modo que el 31,5 % del
corpus que es prosa gramatical nunca se habia medido. Aqui se generan preguntas a partir de
los propios pasajes con qwen3.5:4b y se toma como referencia el pasaje de origen.

Las preguntas son sinteticas y asi hay que declararlo: sirven para comparar dos indices
sobre el mismo material, no para afirmar como pregunta un usuario real. El pasaje del que
sale cada pregunta queda registrado para que se pueda revisar a mano.
"""

import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx

MODELO = "qwen3.5:4b"
URL = "http://localhost:11434"
OBJETIVO = 60

# Un pasaje sirve si es castellano legible. El corpus arrastra indices y paginas con la
# codificacion destrozada ("XOOXLKNXOOXLK") que no se pueden preguntar.
COMUNES = {
    "el", "la", "los", "las", "de", "que", "en", "se", "un", "una", "por", "con",
    "para", "es", "como", "su", "del", "al", "lo", "no", "mas", "este", "esta",
}
PALABRA = re.compile(r"[a-záéíóúüñ]+")

INSTRUCCION = """Lee el pasaje y formula UNA pregunta en espanol que el pasaje responda.

Reglas:
- La pregunta debe poder responderse solo con este pasaje.
- Usa las palabras del propio pasaje, no sinonimos rebuscados.
- Una sola frase interrogativa, sin encabezado ni comillas.
- No menciones "el pasaje", "el texto" ni el numero de pagina.

Pasaje:
"""


def legible(texto: str) -> bool:
    palabras = PALABRA.findall(texto.lower())
    if len(palabras) < 40:
        return False
    return len(set(palabras) & COMUNES) >= 6


def preguntar(texto: str) -> str | None:
    respuesta = httpx.post(
        f"{URL}/api/generate",
        json={
            "model": MODELO,
            "prompt": INSTRUCCION + texto[:900] + "\n\nPregunta:",
            "stream": False,
            "think": False,
            "keep_alive": "30m",
            "options": {"temperature": 0.2, "num_predict": 60},
        },
        timeout=180.0,
    )
    respuesta.raise_for_status()
    pregunta = respuesta.json()["response"].strip().strip('"').split("\n")[0].strip()
    if len(pregunta) < 15 or "?" not in pregunta:
        return None
    return pregunta


def main() -> int:
    raiz = Path(__file__).resolve().parents[1]
    corpus = Path(sys.argv[1]) if len(sys.argv) > 1 else raiz / "data" / "fragmentos_v3.jsonl"
    destino = raiz / "data" / "evaluacion_prosa.json"

    prosa = [
        json.loads(linea)
        for linea in corpus.read_text("utf-8").splitlines()
        if linea.strip() and json.loads(linea).get("tipo") == "prosa"
    ]
    utiles = [f for f in prosa if legible(f["texto"])]
    print(f"prosa total {len(prosa)}, legible {len(utiles)}", flush=True)

    random.seed(20260922)
    muestra = random.sample(utiles, min(OBJETIVO * 2, len(utiles)))

    casos = []
    for fragmento in muestra:
        if len(casos) >= OBJETIVO:
            break
        try:
            pregunta = preguntar(fragmento["texto"])
        except httpx.HTTPError:
            pregunta = None
        if not pregunta:
            continue
        casos.append(
            {
                "id": f"P{len(casos) + 1:03d}",
                "subconjunto": "E_prosa_es",
                "consulta": pregunta,
                "oro": [fragmento["id"]],
                "documento": fragmento["documento"],
                "pagina": fragmento["pagina"],
                "pasaje": fragmento["texto"][:400],
            }
        )
        if len(casos) % 10 == 0:
            print(f"  {len(casos)}/{OBJETIVO}", flush=True)

    destino.write_text(
        json.dumps(casos, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    print(f"\n{len(casos)} preguntas escritas en {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
