"""Compara la tabla precalculada con los dos traductores por modelo sobre el subconjunto D.

El criterio no es la calidad literaria de la traduccion sino si el termino espanol obtenido
recupera la entrada correcta del corpus, que es lo unico que el sistema necesita.
"""

import json
import re
import sys
import unicodedata

import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from application.services.depurador_consulta import DepuradorConsulta
from infrastructure.adapters.output.corpus_jsonl import cargar_fragmentos
from infrastructure.adapters.output.indice_hibrido_lexico import IndiceHibridoLexico
from infrastructure.adapters.output.ollama_traductor import OllamaTraductor


def normalizar(texto: str) -> str:
    return "".join(
        c
        for c in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(c) != "Mn"
    ).strip()


class TraductorTabla:
    """Traductor de consulta por busqueda en la tabla generada en tiempo de compilacion.

    Devuelve TODAS las candidatas espanolas, no una sola: un termino ingles corriente
    corresponde a varios lemas del corpus ("twin" -> doble, gemelo, mellizo) y elegir uno
    de antemano descarta el correcto la mayoria de las veces. La recuperacion se ejecuta
    con todas y el umbral decide, que es el mismo criterio que el caso de uso aplica ya
    entre la consulta original y su traduccion."""

    # Los lemas del corpus son infinitivos sin particula ("DESECHAR"), de modo que el
    # modelo genero "discard" y no "to discard": la consulta debe quitar el prefijo.
    PREFIJO_INFINITIVO = re.compile(r"^to\s+")

    def __init__(self, ruta: Path):
        crudo = json.loads(ruta.read_text("utf-8"))
        self._tabla = {normalizar(k): v for k, v in crudo.items()}

    def candidatas(self, texto: str) -> list:
        """Une las variantes de busqueda en lugar de quedarse con la primera que acierte.

        La tabla contiene tanto 'burp' (de eructar) como 'to burp' (de pedar), porque el
        modelo no siempre omitio la particula. Quedarse con la coincidencia exacta hacia
        que 'to burp' devolviera solo 'pedar' y nunca alcanzara 'eructar', que es el lema
        correcto. Se recuperan todas y el umbral decide."""
        clave = normalizar(texto)
        claves = [clave, self.PREFIJO_INFINITIVO.sub("", clave)]
        if " " in clave:
            # "boiled corn" no es clave, pero "corn" si: el nucleo del sintagma es el
            # que identifica la entrada del diccionario.
            claves.append(clave.rsplit(" ", 1)[-1])

        if not any(k in self._tabla for k in claves) and len(clave) >= 7 and " " not in clave:
            # Compuesto ingles sin entrada propia ("lightweight", "hillside"): se parte en
            # dos mitades y se acepta solo si AMBAS son claves conocidas, de modo que la
            # descomposicion no invente terminos.
            for corte in range(3, len(clave) - 2):
                izquierda, derecha = clave[:corte], clave[corte:]
                if izquierda in self._tabla and derecha in self._tabla:
                    claves.extend([izquierda, derecha])
                    break

        reunidas = []
        for k in dict.fromkeys(claves):
            for opcion in self._tabla.get(k, []):
                if opcion not in reunidas:
                    reunidas.append(opcion)
        return reunidas

    def traducir_al_espanol(self, texto: str) -> str:
        opciones = self.candidatas(texto)
        return opciones[0] if opciones else texto


def evaluar(nombre, traductor, casos, indice, depurador, umbral=0.48):
    aciertos = atendidas = 0
    fallos = []
    for caso in casos:
        termino = depurador.depurar(caso["consulta"])
        if isinstance(traductor, TraductorTabla):
            variantes = traductor.candidatas(termino) or [termino]
        else:
            try:
                variantes = [traductor.traducir_al_espanol(termino)]
            except Exception:
                variantes = [termino]

        # Mejor puntuacion por fragmento entre todas las variantes.
        puntos = None
        for variante in variantes:
            actual = indice.puntuar(variante)
            puntos = actual if puntos is None else np.maximum(puntos, actual)
        mejores = np.argsort(-puntos)[:5]
        identificadores = [indice._fragmentos[i].id for i in mejores]
        similitud = float(puntos[mejores[0]])

        por_lema = any(
            r.coincidencia_lema
            for variante in variantes
            for r in indice.recuperar(variante, k=5)
        )
        if similitud >= umbral or por_lema:
            atendidas += 1
        if any(i in caso["oro"] for i in identificadores):
            aciertos += 1
        else:
            fallos.append((caso["id"], termino, ", ".join(variantes)[:46],
                           caso["forma_esperada"]))
    n = len(casos)
    print(
        f"{nombre:24s} recall@5 {aciertos:3d}/{n}={100*aciertos/n:5.1f}%"
        f"   atendidas {atendidas:3d}/{n}={100*atendidas/n:5.1f}%"
    )
    return fallos


def main() -> int:
    raiz = Path(__file__).resolve().parents[1]
    artefactos = Path(sys.argv[1]) if len(sys.argv) > 1 else raiz / "artefactos_movil"

    indice = IndiceHibridoLexico()
    indice.indexar(cargar_fragmentos(raiz / "data" / "fragmentos_v2.jsonl"))
    depurador = DepuradorConsulta()
    casos = [
        c
        for c in json.loads((raiz / "data" / "evaluacion_v2.json").read_text("utf-8"))
        if c["subconjunto"] == "D_ingles"
    ]

    print(f"Subconjunto D: {len(casos)} consultas\n")
    candidatos = [
        ("tabla precalculada", TraductorTabla(artefactos / "traduccion_en_es.json")),
        ("qwen3.5:4b (escritorio)", OllamaTraductor(modelo="qwen3.5:4b")),
        ("gemma3:1b (movil)", OllamaTraductor(modelo="gemma3:1b")),
    ]
    fallos_tabla = None
    for nombre, traductor in candidatos:
        fallos = evaluar(nombre, traductor, casos, indice, depurador)
        if nombre.startswith("tabla"):
            fallos_tabla = fallos

    if fallos_tabla:
        print(f"\nFallos de la tabla ({len(fallos_tabla)}):")
        for identificador, ingles, espanol, esperada in fallos_tabla:
            print(f"  {identificador} '{ingles}' -> '{espanol}'  esperaba {esperada}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
