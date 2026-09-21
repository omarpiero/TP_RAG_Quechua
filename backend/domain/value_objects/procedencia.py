from dataclasses import dataclass


@dataclass(frozen=True)
class Procedencia:
    documento: str
    pagina: int
    derivado_ocr: bool = False

    def __post_init__(self):
        if not self.documento:
            raise ValueError("Un fragmento no puede carecer de documento de origen")
        if self.pagina < 1:
            raise ValueError(f"Pagina invalida: {self.pagina}")

    def citar(self) -> str:
        cita = f"{self.documento}, p. {self.pagina}"
        if self.derivado_ocr:
            cita += " (texto derivado de OCR, puede contener errores de transcripcion)"
        return cita
