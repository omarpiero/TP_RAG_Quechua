import re
import unicodedata
from dataclasses import dataclass

from domain.entities.fragmento import FragmentoRecuperado

# Recalibrado sobre esta implementacion: 0,48 es el primer umbral sin falsos positivos y
# conserva el 92,8 % de las consultas atendibles. La prueba de concepto reporto 0,41 con un
# 85,6 %; la diferencia proviene de que el Documento 6 no fija la formula exacta de E2 y E3,
# y aqui ambas se calculan como coseno sobre TF-IDF. El propio documento establece que el
# umbral es un parametro calibrado sobre un corpus, una segmentacion y un conjunto de
# consultas concretos, y que cualquier cambio en esos elementos obliga a recalibrarlo.
UMBRAL_CALIBRADO = 0.48

# Piso por debajo del cual un pasaje de prosa ni siquiera se ofrece. No es un umbral de
# confianza y no autoriza ninguna afirmacion: solo descarta lo degenerado.
#
# Deliberadamente bajo. Un umbral de coseno no sirve para decidir si un pasaje merece
# mostrarse: las preguntas sinteticas con las que se calibro son largas y puntuan hacia
# 0,35, mientras que una pregunta real de usuario es corta y puntua la mitad. Con un piso
# de 0,26, "que es el sufijo ablativo" no mostraba el pasaje que define el ablativo, que
# el indice habia recuperado en segunda posicion con 0,208.
PISO_PASAJES = 0.12

# Longitud minima de una palabra para considerarla de contenido. Por debajo son articulos,
# preposiciones y desinencias, que comparten todos los pasajes del corpus.
LARGO_PALABRA_CONTENIDO = 5

# Palabras de contenido que la consulta y el pasaje deben compartir. Con una sola bastaba
# un termino suelto para sacar un pasaje ante cualquier consulta; medido sobre 60 preguntas
# de prosa y 135 negativas, exigir dos elimina los falsos positivos del subconjunto C
# (1/28 -> 0/28) y reduce a la mitad los de gramatica (88,8 % -> 45,8 %), a cambio de
# perder tres puntos de cobertura (88,3 % -> 85,0 %). Exigir tres rebaja la cobertura al
# 81,7 % sin compensacion suficiente.
PALABRAS_COMPARTIDAS = 2


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

    def ofrecer_pasajes(
        self,
        recuperados: list[FragmentoRecuperado],
        consulta: str = "",
        piso: float = PISO_PASAJES,
    ) -> list[FragmentoRecuperado]:
        """Pasajes que merece la pena mostrar sin afirmar que responden a la consulta.

        La condicion no es de similitud sino de solapamiento explicito: el pasaje debe
        compartir con la consulta al menos una palabra de contenido. Es una regla que se
        puede explicar y auditar, a diferencia de un umbral de coseno, y distingue lo que
        el coseno no distinguia: "que es el sufijo ablativo" comparte *ablativo* con el
        pasaje que lo define, y "cual es la capital de Francia" no comparte nada con
        ninguno."""
        del_usuario = self._palabras_de_contenido(consulta)
        # Una consulta con una sola palabra de contenido no puede compartir dos.
        exigidas = min(PALABRAS_COMPARTIDAS, len(del_usuario))
        return [
            r
            for r in recuperados
            if r.puntuacion.valor >= piso
            and len(del_usuario & self._palabras_de_contenido(r.texto)) >= exigidas
        ]

    @staticmethod
    def _palabras_de_contenido(texto: str) -> set[str]:
        normalizado = "".join(
            c
            for c in unicodedata.normalize("NFD", texto.lower())
            if unicodedata.category(c) != "Mn"
        )
        return {
            p
            for p in re.findall(r"[a-z]+", normalizado)
            if len(p) >= LARGO_PALABRA_CONTENIDO
        }

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
