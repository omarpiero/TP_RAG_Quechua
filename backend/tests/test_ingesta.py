import pytest

from application.services.segmentador import Segmentador
from application.use_cases.ingestar_documento import IngestarDocumentoUseCase
from domain.entities.fragmento import Fragmento, TipoFragmento
from domain.ports.extraccion_documental_port import (
    DocumentoExtraido,
    ExtraccionDocumentalPort,
    PaginaExtraida,
)
from domain.ports.indice_recuperacion_port import IndiceRecuperacionPort
from domain.ports.repositorio_corpus_port import RepositorioCorpusPort

PAGINA_DICCIONARIO = (
    "ABAJO: Ulay, ulatraw.\n"
    "ABANDONAR: Katraykuy.\n"
    "ABEJA: Mishkiyuq ulunquy.\n"
)
PAGINA_PROSA = " ".join(["El relato narra la vida en el valle del Mantaro."] * 40)


def _documento(paginas):
    return DocumentoExtraido(
        nombre_archivo="prueba.pdf",
        paginas=[PaginaExtraida(numero=n, texto=t) for n, t in paginas],
    )


class ExtractorFalso(ExtraccionDocumentalPort):
    def __init__(self, documento):
        self._documento = documento

    def extraer(self, contenido, nombre_archivo):
        return self._documento


class CorpusFalso(RepositorioCorpusPort):
    def __init__(self):
        self.fragmentos: list[Fragmento] = []

    def cargar(self):
        return list(self.fragmentos)

    def agregar(self, fragmentos):
        existentes = {f.id for f in self.fragmentos}
        nuevos = [f for f in fragmentos if f.id not in existentes]
        self.fragmentos.extend(nuevos)
        return len(nuevos)

    def documentos(self):
        return sorted({f.procedencia.documento for f in self.fragmentos})


class IndiceFalso(IndiceRecuperacionPort):
    def __init__(self):
        self.reconstrucciones = 0
        self._total = 0

    def indexar(self, fragmentos):
        self.reconstrucciones += 1
        self._total = len(fragmentos)
        return self._total

    def recuperar(self, consulta, k=5):
        return []

    def total_indexado(self):
        return self._total


def test_el_material_lexicografico_se_segmenta_por_entrada():
    fragmentos = Segmentador().segmentar(
        _documento([(1, PAGINA_DICCIONARIO)]), TipoFragmento.LEXICOGRAFICO
    )
    assert len(fragmentos) == 3
    assert fragmentos[0].texto.startswith("ABAJO:")
    assert fragmentos[2].texto.startswith("ABEJA:")


def test_la_prosa_se_segmenta_en_bloques():
    fragmentos = Segmentador().segmentar(
        _documento([(1, PAGINA_PROSA)]), TipoFragmento.PROSA
    )
    assert len(fragmentos) > 1
    assert all(len(f.texto) <= 1000 for f in fragmentos)


def test_cada_fragmento_conserva_su_pagina():
    fragmentos = Segmentador().segmentar(
        _documento([(1, PAGINA_DICCIONARIO), (7, "CASA: Wasi.")]),
        TipoFragmento.LEXICOGRAFICO,
    )
    assert {f.procedencia.pagina for f in fragmentos} == {1, 7}
    assert all(f.procedencia.documento == "prueba.pdf" for f in fragmentos)


def test_las_paginas_sin_texto_se_omiten():
    documento = _documento([(1, PAGINA_DICCIONARIO), (2, ""), (3, "   ")])
    assert documento.paginas_totales == 3
    assert documento.paginas_con_texto == 1
    fragmentos = Segmentador().segmentar(documento, TipoFragmento.LEXICOGRAFICO)
    assert all(f.procedencia.pagina == 1 for f in fragmentos)


def _caso_uso(documento):
    return (
        IngestarDocumentoUseCase(
            extractor=ExtractorFalso(documento),
            corpus=CorpusFalso(),
            indice=IndiceFalso(),
        ),
    )[0]


def test_la_ingesta_indexa_y_reporta_la_cobertura():
    caso_uso = _caso_uso(_documento([(1, PAGINA_DICCIONARIO), (2, "")]))
    resultado = caso_uso.ejecutar(
        contenido=b"",
        nombre_archivo="prueba.pdf",
        tipo=TipoFragmento.LEXICOGRAFICO,
        titulo="Diccionario de prueba",
        entidad_publicadora="MINEDU",
        licenciamiento="Acceso publico",
    )

    assert resultado.paginas_totales == 2
    assert resultado.paginas_con_texto == 1
    assert resultado.fragmentos_nuevos == 3
    assert resultado.total_indexado == 3
    assert not resultado.requiere_ocr


def test_reingerir_el_mismo_documento_no_duplica():
    caso_uso = _caso_uso(_documento([(1, PAGINA_DICCIONARIO)]))
    argumentos = dict(
        contenido=b"",
        nombre_archivo="prueba.pdf",
        tipo=TipoFragmento.LEXICOGRAFICO,
        titulo="Diccionario de prueba",
        entidad_publicadora="MINEDU",
        licenciamiento="Acceso publico",
    )
    caso_uso.ejecutar(**argumentos)
    segunda = caso_uso.ejecutar(**argumentos)

    assert segunda.fragmentos_nuevos == 0
    assert segunda.total_indexado == 3


def test_un_documento_sin_capa_de_texto_se_marca_para_ocr():
    caso_uso = _caso_uso(_documento([(1, ""), (2, "")]))
    resultado = caso_uso.ejecutar(
        contenido=b"",
        nombre_archivo="escaneado.pdf",
        tipo=TipoFragmento.PROSA,
        titulo="Escaneado",
        entidad_publicadora="MINEDU",
        licenciamiento="Acceso publico",
    )
    assert resultado.requiere_ocr
    assert resultado.fragmentos_generados == 0


def test_un_documento_sin_licenciamiento_no_llega_al_indice():
    caso_uso = _caso_uso(_documento([(1, PAGINA_DICCIONARIO)]))
    with pytest.raises(ValueError):
        caso_uso.ejecutar(
            contenido=b"",
            nombre_archivo="prueba.pdf",
            tipo=TipoFragmento.LEXICOGRAFICO,
            titulo="Sin licencia",
            entidad_publicadora="MINEDU",
            licenciamiento="   ",
        )
