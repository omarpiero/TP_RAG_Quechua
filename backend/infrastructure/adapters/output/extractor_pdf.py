import io

from pypdf import PdfReader
from pypdf.errors import PdfReadError

from domain.ports.extraccion_documental_port import (
    DocumentoExtraido,
    ExtraccionDocumentalPort,
    PaginaExtraida,
)


class ExtractorPdf(ExtraccionDocumentalPort):
    """Extrae la capa de texto del PDF pagina a pagina.

    Se emplea pypdf porque conserva la correspondencia entre el texto extraido y su pagina
    de origen, que es el dato sin el cual el requisito de trazabilidad RF-07 no se cumple.

    Las paginas sin capa de texto se devuelven vacias y quedan contabilizadas: la medicion
    del corpus real dio un 88,4 % de paginas con texto, de modo que el reconocimiento
    optico se mantiene como contingencia declarada y no como parte del flujo ordinario."""

    def extraer(self, contenido: bytes, nombre_archivo: str) -> DocumentoExtraido:
        try:
            lector = PdfReader(io.BytesIO(contenido))
        except (PdfReadError, ValueError) as exc:
            raise ValueError(f"El archivo '{nombre_archivo}' no es un PDF legible") from exc

        if lector.is_encrypted:
            raise ValueError(f"El archivo '{nombre_archivo}' esta cifrado y no puede leerse")

        paginas = []
        for numero, pagina in enumerate(lector.pages, start=1):
            try:
                texto = pagina.extract_text() or ""
            except Exception:  # noqa: BLE001 - una pagina corrupta no invalida el documento
                texto = ""
            paginas.append(PaginaExtraida(numero=numero, texto=texto.strip()))

        if not paginas:
            raise ValueError(f"El archivo '{nombre_archivo}' no contiene paginas")

        return DocumentoExtraido(nombre_archivo=nombre_archivo, paginas=paginas)
