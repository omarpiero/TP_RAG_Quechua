import json
from pathlib import Path

from domain.entities.fragmento import Fragmento, TipoFragmento
from domain.value_objects.procedencia import Procedencia


def cargar_fragmentos(ruta: Path) -> list[Fragmento]:
    """Carga el corpus ya segmentado por la ingesta. El material lexicografico viene
    segmentado por entrada y el de prosa por bloques: esa distincion, medida en el
    experimento E6, pesa mas en el resultado que la eleccion de la estrategia."""
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
