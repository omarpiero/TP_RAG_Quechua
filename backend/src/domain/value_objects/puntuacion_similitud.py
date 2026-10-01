from dataclasses import dataclass


@dataclass(frozen=True)
class PuntuacionSimilitud:
    """Similitud coseno acotada en [0,1]. No es una probabilidad ni una tasa de acierto:
    solo expresa cuanto se parecen dos textos bajo la representacion que la produjo, por lo
    que puntuaciones de estrategias distintas no son comparables entre si."""

    valor: float

    def __post_init__(self):
        if not 0.0 <= self.valor <= 1.0:
            raise ValueError(f"Similitud fuera del intervalo [0,1]: {self.valor}")

    def supera(self, umbral: float) -> bool:
        return self.valor >= umbral

    def __str__(self) -> str:
        return f"{self.valor:.3f}"
