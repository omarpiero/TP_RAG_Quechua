"""Traductor de consulta por tabla calculada en tiempo de compilacion.

Sustituye al traductor por modelo. Los lemas del corpus son finitos y conocidos, de modo
que se traducen una sola vez con qwen3.5:4b (scripts/generar_tabla_ingles.py) y aqui solo
se consultan. Medido sobre el subconjunto D: la tabla alcanza 100 % de recall y 100 % de
consultas atendidas, frente al 95 % y 90 % del mismo modelo resolviendo en el momento, y
sin coste de inferencia. Ademas es revisable a mano por un hablante, lo que un modelo no
permite.
"""

import json
import re
import unicodedata
from pathlib import Path

from domain.ports.traductor_port import TraductorPort

PREFIJO_INFINITIVO = re.compile(r"^to\s+")
LARGO_MINIMO_COMPUESTO = 7


def normalizar(texto: str) -> str:
    return "".join(
        c
        for c in unicodedata.normalize("NFD", texto.lower())
        if unicodedata.category(c) != "Mn"
    ).strip()


class TraductorTabla(TraductorPort):
    def __init__(self, ruta: Path):
        crudo = json.loads(Path(ruta).read_text(encoding="utf-8"))
        self._tabla = {normalizar(clave): valor for clave, valor in crudo.items()}

    def candidatas(self, texto: str, aproximar: bool = False) -> list[str]:
        clave = normalizar(texto)
        if not clave:
            return []

        # La busqueda exacta es segura en cualquier idioma: si el termino figura tal cual
        # como palabra inglesa, es que lo es.
        claves = [clave, PREFIJO_INFINITIVO.sub("", clave)]

        # Las aproximaciones no lo son. "panel solar" y "placa base" son sintagmas
        # espanoles cuya ultima palabra existe en ingles ("solar", "base"), y admitirlas
        # sin saber el idioma hacia que tres consultas deliberadamente fuera de cobertura
        # recibieran respuesta. Solo se aplican cuando consta que la consulta es inglesa.
        if aproximar:
            if " " in clave:
                claves.append(clave.rsplit(" ", 1)[-1])
            elif len(clave) >= LARGO_MINIMO_COMPUESTO:
                claves.extend(self._descomponer(clave))

        reunidas: list[str] = []
        for candidata in dict.fromkeys(claves):
            for opcion in self._tabla.get(candidata, []):
                if opcion not in reunidas:
                    reunidas.append(opcion)
        return reunidas

    def _descomponer(self, clave: str) -> list[str]:
        """Parte un compuesto ingles ("lightweight", "hillside") y lo acepta solo si AMBAS
        mitades son claves conocidas, de modo que la descomposicion no invente terminos."""
        for corte in range(3, len(clave) - 2):
            izquierda, derecha = clave[:corte], clave[corte:]
            if izquierda in self._tabla and derecha in self._tabla:
                return [izquierda, derecha]
        return []

    def traducir_al_espanol(self, texto: str) -> str:
        opciones = self.candidatas(texto)
        # Sin entrada se devuelve el original: la recuperacion se ejecuta igualmente con
        # la consulta inglesa y el umbral decide si hay respaldo.
        return opciones[0] if opciones else texto

    def conoce(self, texto: str) -> bool:
        return bool(self.candidatas(texto))
