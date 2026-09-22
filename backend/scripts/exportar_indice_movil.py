"""Exporta el indice de recuperacion a un formato que Dart pueda leer sin scikit-learn.

El indice NO se reimplementa en el movil: se exportan el vocabulario, los pesos IDF y la
matriz ya ajustada, de modo que el telefono solo ejecuta el producto punto. Asi la
aritmetica es la misma que la calibrada en el escritorio y el umbral 0,48 sigue siendo
valido, sin recalibrar.

La matriz se emite en orden por columnas (CSC), es decir como indice invertido: el movil
recorre unicamente los terminos presentes en la consulta en lugar de los 3605 fragmentos.
"""

import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

CORPUS = "fragmentos_v3.jsonl"

import numpy as np
from scipy.sparse import csc_matrix

from application.services.depurador_consulta import DepuradorConsulta
from domain.entities.fragmento import TipoFragmento
from infrastructure.adapters.output.corpus_jsonl import cargar_fragmentos
from infrastructure.adapters.output.indice_hibrido_lexico import IndiceHibridoLexico

VERSION_FORMATO = 1


def _escribir_csc(destino: Path, matriz) -> dict:
    """Emite la matriz como indice invertido en binario plano.

    Formato: indptr uint32[n_columnas+1] | indices uint32[nnz] | data float32[nnz].
    Little-endian explicito para no depender de la arquitectura del telefono."""
    csc = csc_matrix(matriz)
    indptr = csc.indptr.astype("<u4")
    indices = csc.indices.astype("<u4")
    data = csc.data.astype("<f4")
    with destino.open("wb") as f:
        f.write(indptr.tobytes())
        f.write(indices.tobytes())
        f.write(data.tobytes())
    return {
        "archivo": destino.name,
        "columnas": int(csc.shape[1]),
        "filas": int(csc.shape[0]),
        "nnz": int(csc.nnz),
        "bytes": destino.stat().st_size,
    }


def _escribir_float32(destino: Path, valores: np.ndarray) -> dict:
    datos = np.asarray(valores, dtype="<f4")
    destino.write_bytes(datos.tobytes())
    return {"archivo": destino.name, "n": int(datos.size), "bytes": destino.stat().st_size}


def exportar(ruta_corpus: Path, destino: Path, umbral: float) -> dict:
    destino.mkdir(parents=True, exist_ok=True)

    fragmentos = cargar_fragmentos(ruta_corpus)
    indice = IndiceHibridoLexico()
    indice.indexar(fragmentos)

    manifiesto = {
        "version_formato": VERSION_FORMATO,
        "umbral_abstencion": umbral,
        "n_fragmentos": len(fragmentos),
        # El movil debe depurar la consulta igual que el escritorio: la depuracion es
        # parte de la funcion de puntuacion contra la que se calibro el umbral.
        "plantillas_depuracion": DepuradorConsulta.PLANTILLAS,
        "analizadores": {
            "palabras": {"tipo": "word", "patron_token": r"\b\w+\b"},
            "caracteres": {"tipo": "char_wb", "n_min": 3, "n_max": 5},
        },
        "combinacion": "promedio",
    }

    for nombre, vectorizador, matriz in (
        ("palabras", indice._vec_palabras, indice._matriz_palabras),
        ("caracteres", indice._vec_caracteres, indice._matriz_caracteres),
    ):
        vocabulario = vectorizador.vocabulary_
        orden = sorted(vocabulario.items(), key=lambda kv: kv[1])
        (destino / f"vocab_{nombre}.json").write_text(
            json.dumps([t for t, _ in orden], ensure_ascii=False), encoding="utf-8"
        )
        manifiesto[f"idf_{nombre}"] = _escribir_float32(
            destino / f"idf_{nombre}.bin", vectorizador.idf_
        )
        manifiesto[f"matriz_{nombre}"] = _escribir_csc(
            destino / f"matriz_{nombre}.bin", matriz
        )
        manifiesto[f"vocab_{nombre}"] = {
            "archivo": f"vocab_{nombre}.json",
            "n": len(orden),
            "bytes": (destino / f"vocab_{nombre}.json").stat().st_size,
        }

    (destino / "fragmentos.json").write_text(
        json.dumps(
            [
                {
                    "id": f.id,
                    "t": f.texto,
                    "d": f.procedencia.documento,
                    "p": f.procedencia.pagina,
                    "x": 1 if f.tipo is TipoFragmento.LEXICOGRAFICO else 0,
                }
                for f in fragmentos
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    manifiesto["fragmentos"] = {
        "archivo": "fragmentos.json",
        "bytes": (destino / "fragmentos.json").stat().st_size,
    }

    (destino / "lemario.json").write_text(
        json.dumps(indice._lemario, ensure_ascii=False), encoding="utf-8"
    )
    manifiesto["lemario"] = {
        "archivo": "lemario.json",
        "n": len(indice._lemario),
        "bytes": (destino / "lemario.json").stat().st_size,
    }

    (destino / "manifiesto.json").write_text(
        json.dumps(manifiesto, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return manifiesto


if __name__ == "__main__":
    raiz = Path(__file__).resolve().parents[1]
    salida = Path(sys.argv[1]) if len(sys.argv) > 1 else raiz / "artefactos_movil"
    m = exportar(raiz / "data" / CORPUS, salida, umbral=0.48)
    total = sum(v["bytes"] for v in m.values() if isinstance(v, dict) and "bytes" in v)
    print(f"Exportado a {salida}")
    for clave, valor in m.items():
        if isinstance(valor, dict) and "bytes" in valor:
            print(f"  {valor['archivo']:26s} {valor['bytes']/1048576:7.2f} MB")
    print(f"  {'TOTAL':26s} {total/1048576:7.2f} MB")
