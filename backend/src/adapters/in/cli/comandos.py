"""Comandos de la CLI: solo conocen los puertos de entrada, no los casos de uso."""

import logging
from typing import TextIO

from application.ports import ConsultarCorpusPort, ReindexarCorpusPort

log = logging.getLogger("rag.cli")


def consultar(puerto: ConsultarCorpusPort, texto: str, salida: TextIO) -> int:
    log.info("[CLI] consultar")
    log.info("[PUERTO-IN] ConsultarCorpusPort.ejecutar")
    respuesta = puerto.ejecutar(texto)

    estado = "ABSTENCION (sin respaldo documental)" if respuesta.abstenida else "RESPUESTA"
    cifras = f"idioma={respuesta.idioma.value}, similitud_maxima={respuesta.similitud_maxima:.4f}"
    print(f"{estado}  [{cifras}]", file=salida)
    print(respuesta.texto, file=salida)
    for rotulo, fragmentos in (
        ("Respaldo", respuesta.respaldo),
        ("Pasajes (no es una respuesta)", respuesta.pasajes),
    ):
        if fragmentos:
            print(f"\n{rotulo}:", file=salida)
        for r in fragmentos:
            lema = " [coincidencia de lema]" if r.coincidencia_lema else ""
            print(
                f"  - {r.procedencia.documento}, p. {r.procedencia.pagina} "
                f"(puntuacion {r.puntuacion.valor:.4f}){lema}\n    {r.texto}",
                file=salida,
            )
    return 0


def indexar(puerto: ReindexarCorpusPort, salida: TextIO) -> int:
    log.info("[CLI] indexar")
    log.info("[PUERTO-IN] ReindexarCorpusPort.ejecutar")
    estado = puerto.ejecutar()
    print(f"Indice reconstruido: {estado.total_fragmentos} fragmentos", file=salida)
    for documento in estado.documentos:
        print(f"  - {documento}", file=salida)
    return 0
