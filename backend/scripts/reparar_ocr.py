"""Rejunta los acentos que el OCR separo de su palabra en el material de prosa.

La extraccion del PDF de la gramatica dejo cada letra acentuada suelta entre espacios
("la f o rmula para una ra i z bisil a bica"), lo que afecta al 70,6 % de los fragmentos de
prosa y rompe la recuperacion por palabra: "formula" se tokeniza como f + o + rmula, de
modo que ninguna consulta con esa palabra puede encontrarla.

Unir siempre las tres piezas no sirve: "Naci o en" es "Nacio en", dos palabras, y en la
lamina del alfabeto las letras estan sueltas a proposito. La decision se toma con un
vocabulario construido a partir de los fragmentos que el OCR no daño, que son el 78 % del
corpus y estan en el mismo castellano.
"""

import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

ACENTUADAS = "áéíóúüñÁÉÍÓÚÜÑ"
PARTIDO = re.compile(
    rf"(?<=[A-Za-zÀ-ÿ])\s([{ACENTUADAS}]{{1,2}})\s(?=[A-Za-zÀ-ÿ])"
)
PARTIDO_FINAL = re.compile(
    rf"(?<=[A-Za-zÀ-ÿ])\s([{ACENTUADAS}]{{1,2}})(?=[\s,.;:)\]¿?!]|$)"
)
PALABRA = re.compile(r"[A-Za-zÀ-ÿ]+")

# Palabras castellanas de una sola letra. Cuando son la pieza izquierda, el acento no es
# suyo sino de la palabra siguiente: "y e sta" es "y esta", no "yesta".
DE_UNA_LETRA = {"y", "o", "a", "e", "u"}

# Segundo patron de daño: el acento quedo pegado a la pieza derecha en lugar de suelto
# ("hist oricamente"). Solo se une cuando la pieza izquierda no es una palabra, para no
# tocar un articulo seguido de palabra acentuada ("la epoca").
PEGADO_DERECHA = re.compile(
    rf"(?<=[A-Za-zÀ-ÿ])\s(?=[{ACENTUADAS}][a-zà-ÿ]{{2,}})"
)


def sin_tildes(texto: str) -> str:
    return "".join(
        c
        for c in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(c) != "Mn"
    )


class ReparadorOcr:
    def __init__(self, vocabulario: set[str]):
        self._vocabulario = vocabulario

    @classmethod
    def desde_textos_limpios(cls, textos) -> "ReparadorOcr":
        """El vocabulario sale de los fragmentos sin daño: son el mismo castellano y la
        misma terminologia, de modo que no hace falta ningun recurso externo."""
        conteo = Counter()
        for texto in textos:
            if (
                PARTIDO.search(texto)
                or PARTIDO_FINAL.search(texto)
                or PEGADO_DERECHA.search(texto)
            ):
                continue
            conteo.update(p.lower() for p in PALABRA.findall(texto) if len(p) > 1)
        return cls({palabra for palabra, veces in conteo.items() if veces >= 2})

    def _conoce(self, palabra: str) -> bool:
        return palabra.lower() in self._vocabulario or sin_tildes(palabra) in self._vocabulario

    def reparar(self, texto: str) -> str:
        anterior = None
        while anterior != texto:
            anterior = texto
            texto = PARTIDO.sub(self._sustituir, texto)
        return PARTIDO_FINAL.sub(r"\1", texto)

    def _sustituir(self, m: re.Match) -> str:
        acento = m.group(1)
        inicio, fin = m.start(), m.end()
        completo = m.string
        izquierda = PALABRA.findall(completo[:inicio])
        derecha = PALABRA.findall(completo[fin:])
        pieza_izquierda = izquierda[-1] if izquierda else ""
        pieza_derecha = derecha[0] if derecha else ""
        if pieza_izquierda.lower() in DE_UNA_LETRA:
            # El acento pertenece a la palabra de la derecha: "y e sta" es "y esta".
            return " " + acento

        # Se prefiere la lectura cuyas piezas son todas palabras conocidas, en este orden:
        # unir las tres, unir solo por la derecha, unir solo por la izquierda.
        if self._conoce((pieza_izquierda + acento + pieza_derecha).lower()):
            return acento
        if self._conoce(pieza_izquierda) and self._conoce((acento + pieza_derecha).lower()):
            return " " + acento
        if self._conoce((pieza_izquierda + acento).lower()) and self._conoce(pieza_derecha):
            return acento + " "
        if acento in "áéíóú" and self._conoce(pieza_derecha):
            # Una palabra acabada en vocal acentuada seguida de otra palabra conocida es
            # una forma verbal y su complemento ("cogio de", "esta formada"), no una
            # palabra partida. El corpus nunca trae esas formas intactas, de modo que el
            # vocabulario no puede confirmarlas y la terminacion es la unica evidencia.
            return acento + " "
        # Sin evidencia, se une: el daño es la explicacion mas frecuente con diferencia.
        return acento


if __name__ == "__main__":
    import json

    raiz = Path(__file__).resolve().parents[1]
    origen = raiz / "data" / "fragmentos_v2.jsonl"
    destino = Path(sys.argv[1]) if len(sys.argv) > 1 else raiz / "data" / "fragmentos_v3.jsonl"

    lineas = [json.loads(l) for l in origen.read_text("utf-8").splitlines() if l.strip()]
    reparador = ReparadorOcr.desde_textos_limpios(d["texto"] for d in lineas)
    print(f"vocabulario construido: {len(reparador._vocabulario)} palabras")

    cambiados = 0
    for dato in lineas:
        reparado = reparador.reparar(dato["texto"])
        if reparado != dato["texto"]:
            cambiados += 1
            dato["texto"] = reparado
    destino.write_text(
        "\n".join(json.dumps(d, ensure_ascii=False) for d in lineas) + "\n",
        encoding="utf-8",
    )
    print(f"fragmentos reparados: {cambiados}/{len(lineas)} = {100*cambiados/len(lineas):.1f}%")
    print(f"escrito en {destino}")
