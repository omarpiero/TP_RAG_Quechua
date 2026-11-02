# Auditoría PR #9 · fix/privacidad-evidencias (BUG-03)

- **PR / rama:** #9 `fix/privacidad-evidencias` (diff `a6ca42e..bb2b2b2`)
- **Fecha:** 2026-10-29
- **Puerta de calidad:** SonarQube local sin análisis real; pendiente en B9.
- **Pruebas / cobertura / dependencias:** ver `PR-8-verificar.md` (última rama de la pila): 232 pasan, 89 % global, `domain/` ≈ 94 %, `salvaguarda` 18/18, pip-audit limpio. El diff solo toca datos de evidencia, una consulta del script de humo y un ejemplo de la interfaz; Vitest 21/21.

## Hallazgos

| # | Sev. | Archivo | Regla | Descripción | Corrección sugerida |
|---|---|---|---|---|---|
| 1 | Menor | `docs/11_CASOS_VIDEO_Y_CAPTURAS.md` líneas 27 y 77 | CLAUDE.md §8 | Siguen conteniendo una pregunta de `evaluacion_prosa.json`; está declarado y pendiente del archivista. | Sustituir por el id (`P001`). |
| 2 | Menor | Historial de Git | Privacidad | Los textos anteriores siguen en commits antiguos; es decisión declarada del usuario. El *squash merge* evita que lleguen a `main`, pero siguen en las referencias del PR. | Ninguna (decisión del usuario). |

Sin bloqueantes ni mayores.

## Verificación

- **Conteo sin imprimir textos.** Sobre los 382 archivos de texto versionados de la rama apilada (que incluye este PR) busqué las 179 cadenas de `evaluacion_prosa.json` de 12 o más caracteres que no están en los conjuntos versionados (`evaluacion_v2.json`, `negativas_prosa.json`), excluyendo el campo `documento`. Resultado: **1 coincidencia, solo en `docs/11` (líneas 27 y 77)**; 0 en cualquier otro archivo. Sin coincidencias de fragmentos del corpus de 60 o más caracteres (6 034 sondas en la revisión de #7; el registro del PR declara lo mismo).
- **Ejemplos de `PanelPrediccion.jsx`.** Los cuatro ejemplos son: «¿cómo se dice zorro…?», «¿cómo se dice criptomoneda…?», «¿Para qué sirven los sufijos en la gramática?» (propia, no figura en ningún conjunto) y «¿Cómo se conjugan los verbos en la forma negativa del presente?» (viene de `negativas_prosa.json`, versionado). Ninguno contiene formas quechuas (solo palabras en español).
- **Consulta C-05 del humo.** «¿Cuál es el procedimiento para renovar un pasaporte?», propia, esperada como abstención; sin forma quechua. Los CSV y el JSON de humo usan `[prosa:<id>]`.
- **Evidencia del PR.** `b_privacidad/` documenta el conteo antes (212 coincidencias en 6 archivos) y después (solo `docs/11`); coincide con mi conteo.

## Estado de reglas
RN-01…RN-10 y RS-01…RS-08: sin cambios; cumplen. RS-05: cumple.

## Veredicto: **apto** para revisión humana (0 bloqueantes · 0 mayores · 2 menores).
