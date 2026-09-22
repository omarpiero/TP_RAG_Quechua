"""Comprueba que el indice exportado se puede puntuar sin scikit-learn.

Este archivo es el plano de la implementacion en Dart: reproduce la funcion de puntuacion
usando unicamente los artefactos exportados y operaciones elementales. Si las puntuaciones
coinciden con las de scikit-learn sobre el conjunto de evaluacion, el umbral 0,48 viaja
intacto al telefono y no hay que recalibrar nada.
"""

import json
import math
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

CORPUS = "fragmentos_v3.jsonl"

import numpy as np

from infrastructure.adapters.output.corpus_jsonl import cargar_fragmentos
from infrastructure.adapters.output.indice_hibrido_lexico import IndiceHibridoLexico

PATRON_TOKEN = re.compile(r"\b\w+\b", re.UNICODE)
ESPACIOS_MULTIPLES = re.compile(r"\s\s+")


class MotorPortable:
    """Puntuador equivalente a IndiceHibridoLexico que no depende de scikit-learn."""

    def __init__(self, carpeta: Path):
        self.carpeta = carpeta
        self.manifiesto = json.loads((carpeta / "manifiesto.json").read_text("utf-8"))
        self.patrones = [
            re.compile(p, re.IGNORECASE)
            for p in self.manifiesto["plantillas_depuracion"]
        ]
        self.n_fragmentos = self.manifiesto["n_fragmentos"]
        self.campos = {}
        for nombre in ("palabras", "caracteres"):
            terminos = json.loads((carpeta / f"vocab_{nombre}.json").read_text("utf-8"))
            idf = np.frombuffer(
                (carpeta / f"idf_{nombre}.bin").read_bytes(), dtype="<f4"
            )
            meta = self.manifiesto[f"matriz_{nombre}"]
            crudo = (carpeta / meta["archivo"]).read_bytes()
            n_col, nnz = meta["columnas"], meta["nnz"]
            corte1 = (n_col + 1) * 4
            corte2 = corte1 + nnz * 4
            self.campos[nombre] = {
                "vocab": {t: i for i, t in enumerate(terminos)},
                "idf": idf,
                "indptr": np.frombuffer(crudo[:corte1], dtype="<u4"),
                "indices": np.frombuffer(crudo[corte1:corte2], dtype="<u4"),
                "data": np.frombuffer(crudo[corte2:], dtype="<f4"),
            }

    # -- preparacion de la consulta -------------------------------------------------
    @staticmethod
    def normalizar(texto: str) -> str:
        return "".join(
            c
            for c in unicodedata.normalize("NFD", texto.lower())
            if unicodedata.category(c) != "Mn"
        )

    def depurar(self, texto: str) -> str:
        normalizado = self.normalizar(texto)
        for patron in self.patrones:
            normalizado = patron.sub(" ", normalizado)
        normalizado = re.sub(r"[^\w\s]", " ", normalizado)
        return re.sub(r"\s+", " ", normalizado).strip() or self.normalizar(texto)

    # -- analizadores, replicando scikit-learn --------------------------------------
    @staticmethod
    def tokens_palabra(texto: str) -> list:
        return PATRON_TOKEN.findall(texto.lower())

    @staticmethod
    def tokens_caracter(texto: str, n_min: int = 3, n_max: int = 5) -> list:
        texto = ESPACIOS_MULTIPLES.sub(" ", texto.lower())
        salida = []
        for palabra in texto.split():
            w = " " + palabra + " "
            largo = len(w)
            for n in range(n_min, n_max + 1):
                desplazamiento = 0
                salida.append(w[desplazamiento : desplazamiento + n])
                while desplazamiento + n < largo:
                    desplazamiento += 1
                    salida.append(w[desplazamiento : desplazamiento + n])
                if desplazamiento == 0:  # palabra mas corta que n: se cuenta una vez
                    break
        return salida

    # -- puntuacion -----------------------------------------------------------------
    def _similitudes(self, nombre: str, tokens: list) -> np.ndarray:
        campo = self.campos[nombre]
        pesos = {}
        for termino, veces in Counter(tokens).items():
            columna = campo["vocab"].get(termino)
            if columna is not None:
                pesos[columna] = veces * float(campo["idf"][columna])
        norma = math.sqrt(sum(v * v for v in pesos.values()))
        if norma == 0.0:
            return np.zeros(self.n_fragmentos, dtype=np.float64)

        acumulado = np.zeros(self.n_fragmentos, dtype=np.float64)
        for columna, peso in pesos.items():
            inicio, fin = campo["indptr"][columna], campo["indptr"][columna + 1]
            if inicio == fin:
                continue
            filas = campo["indices"][inicio:fin]
            valores = campo["data"][inicio:fin]
            acumulado[filas] += valores * (peso / norma)
        return acumulado

    def puntuar(self, consulta: str) -> np.ndarray:
        depurada = self.depurar(consulta)
        pal = self._similitudes("palabras", self.tokens_palabra(depurada))
        car = self._similitudes("caracteres", self.tokens_caracter(depurada))
        return np.clip((pal + car) / 2.0, 0.0, 1.0)


def main() -> int:
    raiz = Path(__file__).resolve().parents[1]
    carpeta = Path(sys.argv[1]) if len(sys.argv) > 1 else raiz / "artefactos_movil"

    referencia = IndiceHibridoLexico()
    referencia.indexar(cargar_fragmentos(raiz / "data" / CORPUS))
    motor = MotorPortable(carpeta)

    evaluacion = json.loads((raiz / "data" / "evaluacion_v2.json").read_text("utf-8"))
    consultas = evaluacion if isinstance(evaluacion, list) else evaluacion["consultas"]

    peor = 0.0
    desajustes_orden = 0
    peor_consulta = ""
    for caso in consultas:
        texto = caso["consulta"]
        a = referencia.puntuar(texto)
        b = motor.puntuar(texto)
        delta = float(np.max(np.abs(a - b)))
        if delta > peor:
            peor, peor_consulta = delta, texto
        if list(np.argsort(-a)[:5]) != list(np.argsort(-b)[:5]):
            desajustes_orden += 1

    print(f"Consultas comparadas      : {len(consultas)}")
    print(f"Diferencia maxima absoluta: {peor:.3e}   ({peor_consulta[:60]})")
    print(f"Desajustes en el top-5    : {desajustes_orden}")
    ok = peor < 1e-6 and desajustes_orden == 0
    print("\nRESULTADO:", "EQUIVALENTE" if ok else "DIVERGE — revisar analizadores")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
