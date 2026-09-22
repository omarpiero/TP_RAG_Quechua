"""Genera preguntas de gramatica fuera de cobertura, para calibrar el umbral de prosa.

El subconjunto C existente son consultas lexicas ("como se dice panel solar"). Calibrar con
ellas el umbral de la prosa mide mal: una pregunta gramatical larga puntua distinto que un
termino suelto, tanto si el corpus la cubre como si no. Estas negativas tienen la misma
forma que las positivas y versan sobre lenguas y materias que el corpus no documenta.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx

MODELO = "qwen3.5:4b"
URL = "http://localhost:11434"

TEMAS = [
    "la conjugacion de los verbos en japones",
    "las declinaciones del latin",
    "los verbos frasales del ingles",
    "los casos gramaticales del aleman",
    "la escritura del arabe",
    "los tonos del chino mandarin",
    "el aspecto verbal en ruso",
    "los articulos en frances",
    "la formacion del plural en italiano",
    "el orden de palabras en coreano",
    "la legislacion minera peruana",
    "las tacticas del futbol moderno",
    "el cultivo de la quinua en altura",
    "la arquitectura de los computadores",
    "el tratamiento del agua potable",
]

INSTRUCCION = """Formula DOS preguntas en espanol sobre {tema}, del estilo de las que se
harian a un manual de consulta. Una por linea, sin numerar, sin comillas y terminadas en
signo de interrogacion. No menciones el quechua.

Preguntas:"""


def main() -> int:
    raiz = Path(__file__).resolve().parents[1]
    destino = raiz / "data" / "negativas_prosa.json"

    casos = []
    for tema in TEMAS:
        respuesta = httpx.post(
            f"{URL}/api/generate",
            json={
                "model": MODELO,
                "prompt": INSTRUCCION.format(tema=tema),
                "stream": False,
                "think": False,
                "keep_alive": "30m",
                "options": {"temperature": 0.4, "num_predict": 120},
            },
            timeout=180.0,
        )
        respuesta.raise_for_status()
        for linea in respuesta.json()["response"].splitlines():
            pregunta = linea.strip().lstrip("-*0123456789. ").strip()
            if len(pregunta) > 20 and pregunta.endswith("?"):
                casos.append(
                    {
                        "id": f"N{len(casos) + 1:03d}",
                        "subconjunto": "F_prosa_fuera_de_cobertura",
                        "consulta": pregunta,
                        "tema": tema,
                    }
                )
        print(f"  {tema[:40]:42s} -> {len(casos)}", flush=True)

    destino.write_text(json.dumps(casos, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{len(casos)} negativas escritas en {destino}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
