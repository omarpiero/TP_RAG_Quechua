"""Genera la tabla ingles->espanol de los lemas del corpus, en tiempo de compilacion.

El paso ingles->espanol de la consulta lo resuelve hoy el modelo en el momento. En el
telefono no cabe un modelo capaz de hacerlo bien: qwen3.5:4b alcanza 95 % de recall en el
subconjunto D y gemma3:1b solo 57,5 %, con errores de significado ("cave"->"tumba",
"lizard"->"serpiente").

Como los lemas del corpus son finitos y conocidos (2257), la traduccion se calcula una sola
vez aqui, con el modelo grande, y el telefono se limita a consultar la tabla. El resultado
es determinista, revisable a mano por un hablante y pesa unos 100 KB.
"""

import json
import re
import sys
import time
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx

from domain.entities.fragmento import TipoFragmento
from infrastructure.adapters.output.corpus_jsonl import cargar_fragmentos

CABECERA = re.compile(r"(?=\b[A-ZÁÉÍÓÚÜÑ][A-ZÁÉÍÓÚÜÑ\s\-]{1,30}:)")
ENTRADA = re.compile(r"\s*([A-ZÁÉÍÓÚÜÑ][A-ZÁÉÍÓÚÜÑ\s\-]*?)\s*:\s*(.*)", re.S)
LOTE = 20
MODELO = "qwen3.5:4b"

INSTRUCCION = """Traduce cada palabra del espanol al ingles. Son entradas de un diccionario.
Devuelve EXACTAMENTE una linea por entrada, en el mismo orden, con el formato:
numero|palabra_espanola|traduccion1, traduccion2, traduccion3
Da entre tres y cinco traducciones inglesas por entrada, en minusculas.
Incluye los sinonimos habituales, no solo el mas comun: quien consulte el
diccionario puede escribir cualquiera de ellos.
Para los verbos da la forma sin particula ('discard', no 'to discard').
Si la palabra no tiene equivalente de una sola palabra en ingles, anade tambien
la descripcion corta habitual (por ejemplo 'mote' -> hominy, boiled corn).
No anadas encabezados, comentarios ni lineas en blanco.

"""


def normalizar(texto: str) -> str:
    return "".join(
        c
        for c in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(c) != "Mn"
    ).strip()


def extraer_lemas(ruta: Path) -> list:
    lemas = set()
    for fragmento in cargar_fragmentos(ruta):
        if fragmento.tipo is not TipoFragmento.LEXICOGRAFICO:
            continue
        for bloque in CABECERA.split(fragmento.texto):
            m = ENTRADA.match(bloque)
            if not m:
                continue
            principal = re.split(r"\(", m.group(2))[0].strip().rstrip(".")
            if [x for x in principal.split(",") if x.strip()]:
                lemas.add(m.group(1).strip().lower())
    return sorted(lemas)


def pedir(lote: list, url: str) -> dict:
    cuerpo = "\n".join(f"{i}|{p}" for i, p in enumerate(lote, start=1))
    respuesta = httpx.post(
        f"{url}/api/generate",
        json={
            "model": MODELO,
            "prompt": INSTRUCCION + cuerpo + "\n\nRespuesta:",
            "stream": False,
            "think": False,
            "keep_alive": "30m",
            "options": {"temperature": 0.0, "num_predict": 110 * len(lote)},
        },
        timeout=300.0,
    )
    respuesta.raise_for_status()
    salida = {}
    for linea in respuesta.json()["response"].splitlines():
        partes = [p.strip() for p in linea.split("|")]
        if len(partes) < 3 or not partes[0].isdigit():
            continue
        posicion = int(partes[0]) - 1
        if not 0 <= posicion < len(lote):
            continue
        # La posicion manda sobre el texto: si el modelo altera la palabra espanola,
        # la entrada se descarta en lugar de asociarse al lema equivocado.
        if normalizar(partes[1]) != normalizar(lote[posicion]):
            continue
        ingleses = [
            normalizar(x) for x in partes[2].split(",") if x.strip() and len(x.strip()) < 40
        ]
        if ingleses:
            salida[lote[posicion]] = ingleses
    return salida


def main() -> int:
    raiz = Path(__file__).resolve().parents[1]
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else raiz / "artefactos_movil"
    destino.mkdir(parents=True, exist_ok=True)
    url = "http://localhost:11434"

    lemas = extraer_lemas(raiz / "data" / "fragmentos_v2.jsonl")
    print(f"Lemas a traducir: {len(lemas)}", flush=True)

    es_en, pendientes = {}, []
    inicio = time.perf_counter()
    for comienzo in range(0, len(lemas), LOTE):
        lote = lemas[comienzo : comienzo + LOTE]
        try:
            obtenido = pedir(lote, url)
        except httpx.HTTPError as e:
            print(f"  lote {comienzo}: fallo HTTP {e}", flush=True)
            obtenido = {}
        es_en.update(obtenido)
        pendientes.extend([p for p in lote if p not in obtenido])
        hechos = comienzo + len(lote)
        if hechos % 200 < LOTE:
            transcurrido = time.perf_counter() - inicio
            print(
                f"  {hechos}/{len(lemas)}  ok={len(es_en)}  pendientes={len(pendientes)}"
                f"  {transcurrido:.0f}s",
                flush=True,
            )

    print(f"Reintentando {len(pendientes)} en lotes de 5...", flush=True)
    for comienzo in range(0, len(pendientes), 5):
        lote = pendientes[comienzo : comienzo + 5]
        try:
            es_en.update(pedir(lote, url))
        except httpx.HTTPError:
            pass

    faltan = [p for p in lemas if p not in es_en]

    en_es = {}
    for espanol, ingleses in es_en.items():
        for ingles in ingleses:
            en_es.setdefault(ingles, [])
            if espanol not in en_es[ingles]:
                en_es[ingles].append(espanol)

    (destino / "traduccion_en_es.json").write_text(
        json.dumps(en_es, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )
    (destino / "traduccion_es_en.json").write_text(
        json.dumps(es_en, ensure_ascii=False, sort_keys=True, indent=1), encoding="utf-8"
    )
    if faltan:
        (destino / "traduccion_sin_resolver.txt").write_text(
            "\n".join(faltan), encoding="utf-8"
        )

    peso = (destino / "traduccion_en_es.json").stat().st_size
    print(f"\nLemas resueltos : {len(es_en)}/{len(lemas)}")
    print(f"Sin resolver    : {len(faltan)}")
    print(f"Claves inglesas : {len(en_es)}")
    print(f"Tabla EN->ES    : {peso/1024:.0f} KB")
    print(f"Tiempo total    : {time.perf_counter()-inicio:.0f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
