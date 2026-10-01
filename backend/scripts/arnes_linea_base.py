"""Arnes de no regresion: ejecuta el caso de uso completo sobre las 248 consultas de
evaluacion_v2.json con un generador falso instrumentado y deja dos CSV.

- arnes_por_consulta.csv: una fila por consulta con la decision del caso de uso.
- barrido_umbral.csv: barrido de tau 0,00..1,00 sobre la similitud maxima del caso de
  uso (positivos A+B, negativos C), con y sin la regla de lema.

Sirve de red de seguridad para los PR de refactor (PROMPT_CIERRE_PMV1.md, paso 3): tras
cada PR el arnes debe dar exactamente lo mismo salvo los cambios que el PR declare. No
escribe texto del corpus: solo identificadores, cifras y las consultas del conjunto de
evaluacion (que ya esta versionado).

Uso, desde backend/:  python scripts/arnes_linea_base.py <carpeta_salida>
"""

import csv
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

from adapters.out.documentos.corpus_jsonl import cargar_fragmentos  # noqa: E402
from adapters.out.idioma.detector_idioma_heuristico import (  # noqa: E402
    DetectorIdiomaHeuristico,
)
from adapters.out.recuperacion.indice_hibrido_lexico import (  # noqa: E402
    IndiceHibridoLexico,
)
from adapters.out.traduccion.traductor_tabla import TraductorTabla  # noqa: E402
from application.use_cases.consultar_corpus import ConsultarCorpusUseCase  # noqa: E402
from domain.services.evaluador_confianza import EvaluadorConfianza  # noqa: E402
from infrastructure.config import configuracion  # noqa: E402

DATOS = RAIZ / "data"
PARTICION = {
    "A_lexico_es": "A",
    "B_independiente": "B",
    "C_fuera_de_cobertura": "C",
    "D_ingles": "D",
}


class GeneradorInstrumentado:
    """Doble del generador: no redacta nada propio, cuenta invocaciones y devuelve el
    texto literal del primer fragmento de respaldo."""

    def __init__(self):
        self.invocaciones = 0

    def redactar(self, consulta, respaldo, idioma):
        self.invocaciones += 1
        return respaldo[0].texto

    def precalentar(self):
        return None


def construir_caso_de_uso(umbral: float):
    indice = IndiceHibridoLexico()
    indice.indexar(cargar_fragmentos(configuracion.ruta_corpus))
    generador = GeneradorInstrumentado()
    caso = ConsultarCorpusUseCase(
        indice=indice,
        generador=generador,
        evaluador=EvaluadorConfianza(umbral=umbral),
        detector_idioma=DetectorIdiomaHeuristico(),
        repositorio=None,
        traductor=TraductorTabla(configuracion.ruta_tabla_traduccion),
        k=configuracion.fragmentos_recuperados,
    )
    return caso, generador


def decidir(respuesta) -> str:
    if not respuesta.abstenida:
        return "responde"
    if respuesta.pasajes:
        return "abstiene_con_pasajes"
    if respuesta.similitud_maxima == 0.0 and not respuesta.consulta_traducida:
        # El caso de uso solo devuelve similitud 0 sin recuperar cuando el idioma no es
        # soportado (o el indice no devolvio nada).
        return "abstiene_sin_recuperar"
    return "abstiene"


def ejecutar(salida: Path) -> list[dict]:
    umbral = configuracion.umbral_abstencion
    caso, generador = construir_caso_de_uso(umbral)
    evaluacion = json.loads((DATOS / "evaluacion_v2.json").read_text(encoding="utf-8"))

    filas = []
    for item in evaluacion:
        antes = generador.invocaciones
        respuesta = caso.ejecutar(item["consulta"])
        invocado = generador.invocaciones - antes
        oro = set(item.get("oro", []))
        respaldo_ids = [r.id for r in respuesta.respaldo]
        por_lema = any(r.coincidencia_lema for r in respuesta.respaldo)
        via = respuesta.via_respaldo or ""
        filas.append(
            {
                "id": item["id"],
                "particion": PARTICION[item["subconjunto"]],
                "consulta": item["consulta"],
                "traduccion": respuesta.consulta_traducida or "",
                "top1_id": respaldo_ids[0] if respaldo_ids else "",
                "similitud_max": f"{respuesta.similitud_maxima:.6f}",
                "decision": decidir(respuesta),
                "via_respaldo": via,
                "pasajes": len(respuesta.pasajes),
                "pasajes_ids": "|".join(p.id for p in respuesta.pasajes),
                "respaldo_ids": "|".join(respaldo_ids),
                "respaldo_lema": int(por_lema),
                "respaldo_correcto": int(bool(oro & set(respaldo_ids))),
                "generador_invocado": invocado,
                "respaldo_sin_documento_o_pagina": int(
                    any(
                        not r.procedencia.documento or r.procedencia.pagina < 1
                        for r in respuesta.respaldo
                    )
                ),
            }
        )

    with (salida / "arnes_por_consulta.csv").open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)
    return filas


def barrido(filas: list[dict], salida: Path) -> list[dict]:
    """Barrido sobre la similitud maxima que ve el caso de uso. Con regla de lema, una
    consulta tambien se responde si su respaldo llego por coincidencia exacta de lema."""
    positivos = [f for f in filas if f["particion"] in ("A", "B")]
    negativos = [f for f in filas if f["particion"] == "C"]
    resultado = []
    for paso in range(101):
        tau = paso / 100
        for regla_lema in (True, False):
            def responde(f):
                sim = float(f["similitud_max"])
                return sim >= tau or (regla_lema and f["respaldo_lema"] == 1)

            vp = sum(responde(f) for f in positivos)
            fn = len(positivos) - vp
            fp = sum(responde(f) for f in negativos)
            vn = len(negativos) - fp
            precision = vp / (vp + fp) if vp + fp else 0.0
            recall = vp / len(positivos)
            f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
            especificidad = vn / len(negativos)
            resultado.append(
                {
                    "tau": f"{tau:.2f}",
                    "regla_lema": "si" if regla_lema else "no",
                    "vp": vp, "fp": fp, "vn": vn, "fn": fn,
                    "precision": f"{precision:.4f}",
                    "recall": f"{recall:.4f}",
                    "f1": f"{f1:.4f}",
                    "especificidad": f"{especificidad:.4f}",
                }
            )
    with (salida / "barrido_umbral.csv").open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=list(resultado[0]))
        escritor.writeheader()
        escritor.writerows(resultado)
    return resultado


def resumen(filas: list[dict], barrido_filas: list[dict]) -> dict:
    por_particion = {}
    for p in ("A", "B", "C", "D"):
        grupo = [f for f in filas if f["particion"] == p]
        por_particion[p] = {
            "n": len(grupo),
            "responde_similitud": sum(f["via_respaldo"] == "similitud" for f in grupo),
            "responde_lema": sum(f["via_respaldo"] == "lema" for f in grupo),
            "abstiene": sum(f["decision"] == "abstiene" for f in grupo),
            "abstiene_con_pasajes": sum(f["decision"] == "abstiene_con_pasajes" for f in grupo),
            "respaldo_correcto": sum(f["respaldo_correcto"] for f in grupo),
        }
    sin_respaldo = [f for f in filas if f["decision"] != "responde"]
    primer_sin_fp = {}
    for regla in ("si", "no"):
        fila = next(
            (b for b in barrido_filas if b["regla_lema"] == regla and b["fp"] == 0), None
        )
        primer_sin_fp[regla] = fila
    return {
        "tau": configuracion.umbral_abstencion,
        "por_particion": por_particion,
        "fp_en_C": por_particion["C"]["responde_similitud"] + por_particion["C"]["responde_lema"],
        "invocaciones_generador": sum(f["generador_invocado"] for f in filas),
        "respuestas": sum(f["decision"] == "responde" for f in filas),
        "invocaciones_sin_respaldo": sum(f["generador_invocado"] for f in sin_respaldo),
        "respuestas_sin_documento_o_pagina": sum(
            f["respaldo_sin_documento_o_pagina"] for f in filas
        ),
        "primer_tau_sin_fp": primer_sin_fp,
        "en_tau_vigente": [
            b for b in barrido_filas if b["tau"] == f"{configuracion.umbral_abstencion:.2f}"
        ],
    }


def main():
    salida = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    salida.mkdir(parents=True, exist_ok=True)
    filas = ejecutar(salida)
    barrido_filas = barrido(filas, salida)
    datos = resumen(filas, barrido_filas)
    (salida / "resumen_arnes.json").write_text(
        json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(datos, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
