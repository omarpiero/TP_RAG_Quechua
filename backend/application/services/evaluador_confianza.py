from dataclasses import dataclass

from domain.entities.fragmento import FragmentoRecuperado

# Recalibrado sobre esta implementacion: 0,48 es el primer umbral sin falsos positivos y
# conserva el 92,8 % de las consultas atendibles. La prueba de concepto reporto 0,41 con un
# 85,6 %; la diferencia proviene de que el Documento 6 no fija la formula exacta de E2 y E3,
# y aqui ambas se calculan como coseno sobre TF-IDF. El propio documento establece que el
# umbral es un parametro calibrado sobre un corpus, una segmentacion y un conjunto de
# consultas concretos, y que cualquier cambio en esos elementos obliga a recalibrarlo.
UMBRAL_CALIBRADO = 0.48


@dataclass(frozen=True)
class Veredicto:
    responder: bool
    similitud_maxima: float
    umbral: float
    por_lema: bool = False

    @property
    def motivo(self) -> str:
        if self.por_lema:
            return "coincidencia exacta con el lema de una entrada lexicografica"
        if self.responder:
            return f"similitud {self.similitud_maxima:.3f} >= umbral {self.umbral:.2f}"
        return f"similitud {self.similitud_maxima:.3f} < umbral {self.umbral:.2f}"


class EvaluadorConfianza:
    """Unico punto del sistema donde se decide entre generar una respuesta y abstenerse.

    El punto de operacion no es el que maximiza F1, sino el primero que no produce ningun
    falso positivo. Los dos errores no son simetricos: una consulta legitima sin respuesta
    deja al usuario donde estaba, mientras que una forma inventada sobre una lengua
    seriamente en peligro entra en circulacion y no se retira."""

    def __init__(self, umbral: float = UMBRAL_CALIBRADO):
        if not 0.0 <= umbral <= 1.0:
            raise ValueError(f"Umbral fuera del intervalo [0,1]: {umbral}")
        self._umbral = umbral

    @property
    def umbral(self) -> float:
        return self._umbral

    def evaluar(self, recuperados: list[FragmentoRecuperado]) -> Veredicto:
        if not recuperados:
            return Veredicto(responder=False, similitud_maxima=0.0, umbral=self._umbral)

        maxima = max(r.puntuacion.valor for r in recuperados)
        # La coincidencia de lema no puede producir un falso positivo: solo se activa cuando
        # el termino consultado figura literalmente como entrada del corpus indexado.
        por_lema = any(r.coincidencia_lema for r in recuperados)

        return Veredicto(
            responder=por_lema or maxima >= self._umbral,
            similitud_maxima=maxima,
            umbral=self._umbral,
            por_lema=por_lema,
        )
