from datetime import date

import pytest

from application.use_cases.gestionar_fuentes import GestionarFuentesUseCase
from domain.entities.fuente import Fuente
from domain.ports.repositorio_fuentes_port import RepositorioFuentesPort


class RepositorioFalso(RepositorioFuentesPort):
    def __init__(self):
        self.almacen = {}

    def crear(self, fuente):
        self.almacen[fuente.id] = fuente
        return fuente

    def obtener(self, fuente_id):
        return self.almacen.get(fuente_id)

    def listar(self):
        return list(self.almacen.values())

    def actualizar(self, fuente):
        if fuente.id not in self.almacen:
            raise KeyError(fuente.id)
        self.almacen[fuente.id] = fuente
        return fuente

    def eliminar(self, fuente_id):
        return self.almacen.pop(fuente_id, None) is not None


def _fuente(**cambios):
    datos = {
        "titulo": "Diccionario Huanca",
        "entidad_publicadora": "MINEDU",
        "licenciamiento": "Acceso publico con finalidad educativa",
        "fecha_extraccion": date(2026, 9, 14),
        "nombre_archivo": "diccionario.pdf",
        "paginas_totales": 60,
        "paginas_con_texto": 58,
    }
    return Fuente(**{**datos, **cambios})


def test_una_fuente_sin_licenciamiento_no_puede_registrarse():
    """RNF-11 y principios CARE: la obligacion de gobernanza se hace cumplir en el dominio,
    de modo que ninguna interfaz pueda saltarsela."""
    with pytest.raises(ValueError):
        _fuente(licenciamiento="   ")


def test_cobertura_de_extraccion():
    assert _fuente().cobertura_extraccion == pytest.approx(58 / 60)
    assert _fuente(paginas_totales=0, paginas_con_texto=0).cobertura_extraccion == 0.0


def test_ciclo_completo_de_gestion():
    gestor = GestionarFuentesUseCase(RepositorioFalso())
    fuente = gestor.registrar(_fuente())

    assert gestor.obtener(fuente.id) == fuente
    assert len(gestor.listar()) == 1

    gestor.actualizar(_fuente(id=fuente.id, titulo="Diccionario Huanca revisado"))
    assert gestor.obtener(fuente.id).titulo == "Diccionario Huanca revisado"

    assert gestor.eliminar(fuente.id) is True
    assert gestor.eliminar(fuente.id) is False
    assert gestor.listar() == []
