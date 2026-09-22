import json
from pathlib import Path

from domain.entities.fragmento import Fragmento, TipoFragmento
from domain.ports.repositorio_corpus_port import RepositorioCorpusPort
from domain.value_objects.procedencia import Procedencia


def cargar_fragmentos(ruta: Path) -> list[Fragmento]:
    """Carga el corpus ya segmentado. El material lexicografico viene segmentado por entrada
    y el de prosa por bloques: esa distincion, medida en el experimento E6, pesa mas en el
    resultado que la eleccion de la estrategia de recuperacion."""
    if not ruta.exists():
        raise FileNotFoundError(f"No se encuentra el corpus en {ruta}")

    fragmentos = []
    with ruta.open(encoding="utf-8") as fh:
        for numero, linea in enumerate(fh, start=1):
            linea = linea.strip()
            if not linea:
                continue
            try:
                registro = json.loads(linea)
                fragmentos.append(
                    Fragmento(
                        id=registro["id"],
                        texto=registro["texto"],
                        procedencia=Procedencia(
                            documento=registro["documento"],
                            pagina=int(registro["pagina"]),
                            derivado_ocr=registro.get("derivado_ocr", False),
                        ),
                        tipo=TipoFragmento(registro["tipo"]),
                    )
                )
            except (json.JSONDecodeError, KeyError, ValueError) as exc:
                raise ValueError(f"Registro invalido en {ruta}:{numero} -> {exc}") from exc

    return fragmentos


class CorpusJsonl(RepositorioCorpusPort):
    def __init__(self, ruta: Path):
        self._ruta = ruta

    def cargar(self) -> list[Fragmento]:
        return cargar_fragmentos(self._ruta)

    def agregar(self, fragmentos: list[Fragmento]) -> int:
        existentes = {f.id for f in self.cargar()} if self._ruta.exists() else set()
        nuevos = [f for f in fragmentos if f.id not in existentes]
        if not nuevos:
            return 0

        with self._ruta.open("a", encoding="utf-8") as fh:
            for fragmento in nuevos:
                fh.write(
                    json.dumps(
                        {
                            "id": fragmento.id,
                            "documento": fragmento.procedencia.documento,
                            "pagina": fragmento.procedencia.pagina,
                            "texto": fragmento.texto,
                            "tipo": fragmento.tipo.value,
                            "derivado_ocr": fragmento.procedencia.derivado_ocr,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
        return len(nuevos)

    def documentos(self) -> list[str]:
        return sorted({f.procedencia.documento for f in self.cargar()})
