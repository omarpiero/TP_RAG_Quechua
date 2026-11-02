# Auditoría PR #14 · test/paridad-movil (B12, HU-08.3)

- **PR / rama:** #14 `test/paridad-movil` (commit propio `441db3b`: solo evidencia en `docs/evidencias/cierre_u3/b12_paridad/`; no cambia código)
- **Fecha:** 2026-10-29
- **Puerta de calidad:** sin cambios de código; ver `PR-11-calidad.md` (OK tras la corrección).
- **Pruebas (última rama de la pila):** 296 pasan, 0 omitidas, cobertura global 89 %; `salvaguarda` 35/35; Vitest 22/22; pip-audit y `npm audit` limpios.

## Comprobación de las cifras (reejecutada)

Exporté el índice a una carpeta temporal con `exportar_indice_movil.py` y lo validé con `validar_indice_movil.py` sobre las 248 consultas del conjunto de evaluación:

| Medida | Informe del PR | Reejecución propia | Coincide |
|---|---|---|---|
| Diferencia máxima absoluta | 2,533 × 10⁻⁸ | 2,533 × 10⁻⁸ (mismo caso, consulta de la partición léxica) | Sí |
| Desajustes en el top-5 | 0 | 0 (248 consultas comparadas) | Sí |
| Tamaño del índice | 11,67 MB | `TOTAL 11.67 MB` del script; 11,68 MiB (12,24 MB decimales) con `du` | Sí (el script usa MiB) |
| Veredicto | EQUIVALENTE | EQUIVALENTE | Sí |

Umbral de paridad del RN-10: < 1 × 10⁻⁶; el valor medido es 40 veces menor. La referencia histórica (ADR-019: 2,5 × 10⁻⁸ y 11,85 MB) es coherente con el resultado actual.

## Hallazgos

| # | Sev. | Archivo | Regla | Descripción | Corrección sugerida |
|---|---|---|---|---|---|
| 1 | Menor | `b12_paridad/registro.md` | Unidades | «MB» en el registro son MiB (el script divide por 2²⁰); la referencia de 11,85 MB del informe puede usar la misma convención, pero conviene decirlo. La reducción de 0,18 MB se atribuye implícitamente a «los cambios del cierre» sin explicarla. | Aclarar la unidad y la causa de la diferencia de tamaño. |
| 2 | Menor | alcance de la prueba | RN-10 | La paridad compara el motor de referencia de scikit-learn con el motor portable **en Python** (`MotorPortable`), no con la implementación Dart, y sobre las particiones A, B, C y D del conjunto v2 (no cubre E ni consultas sin conjunto). El registro lo reconoce (HU-08.3 sigue en QA hasta validarse en un dispositivo físico). | Mantener HU-08.3 en QA; añadir la paridad Dart cuando exista el dispositivo. |

Sin bloqueantes ni mayores. `exportar_indice_movil.py` sigue funcionando con el estado atómico del índice (lee `_vec_*`, `_matriz_*` y `_lemario` mediante las propiedades); no hay artefactos binarios versionados (la carpeta `artefactos_movil/` queda fuera de Git).

## Estado de reglas
RN-10 (paridad < 1 × 10⁻⁶): cumple en el motor portable de Python. RN-01…RN-09 y RS-01…RS-08: sin cambios.

## Veredicto: **apto** para revisión humana (0 bloqueantes · 0 mayores · 2 menores).
