import logging

from application.ports import EstadoCorpus, ReindexarCorpusPort
from application.ports.out.indice_recuperacion_port import IndiceRecuperacionPort
from application.ports.out.repositorio_corpus_port import RepositorioCorpusPort

log = logging.getLogger("rag.caso_uso")


class ReindexarCorpusUseCase(ReindexarCorpusPort):
    """RF-13: reconstruye el indice desde el corpus persistido, que es el dato; el indice
    es una estructura derivada."""

    def __init__(self, corpus: RepositorioCorpusPort, indice: IndiceRecuperacionPort):
        self._corpus = corpus
        self._indice = indice

    def ejecutar(self) -> EstadoCorpus:
        log.info("[CASO-USO] ReindexarCorpus")
        total = self._indice.indexar(self._corpus.cargar())
        log.info("[INDICE] reindexado: fragmentos=%d", total)
        return self.estado()

    def estado(self) -> EstadoCorpus:
        return EstadoCorpus(
            documentos=self._corpus.documentos(),
            total_fragmentos=self._indice.total_indexado(),
        )
