"""Punto de entrada: `python -m adapters.in.cli <comando>` (desde backend/src).

Este modulo es el unico de la CLI que toca la infraestructura: arma el contenedor y entrega
a los comandos los puertos de entrada que necesitan.
"""

import argparse
import logging
import sys
from importlib import import_module

from infrastructure.contenedor import Contenedor

comandos = import_module("adapters.in.cli.comandos")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m adapters.in.cli",
        description="Asistente de consulta del quechua wanka (adaptador de entrada CLI).",
    )
    sub = parser.add_subparsers(dest="comando", required=True)
    p_consultar = sub.add_parser("consultar", help="consulta el corpus en espanol o ingles")
    p_consultar.add_argument("texto")
    p_consultar.add_argument(
        "--generador",
        choices=["auto", "ollama", "literal"],
        default="auto",
        help="auto: Ollama si responde; literal: texto del fragmento, sin modelo",
    )
    sub.add_parser("indexar", help="reconstruye el indice desde el corpus")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S", stream=sys.stderr
    )
    contenedor = Contenedor(generador=getattr(args, "generador", "auto"))
    if args.comando == "consultar":
        return comandos.consultar(contenedor.consultar_corpus, args.texto, sys.stdout)
    return comandos.indexar(contenedor.reindexar_corpus, sys.stdout)


if __name__ == "__main__":
    sys.exit(main())
