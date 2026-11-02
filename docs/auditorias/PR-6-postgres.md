# Auditoría PR #6 · test/procedimientos-postgres (B4)

- **PR / rama:** #6 `test/procedimientos-postgres` (diff `feat/HU-09-origen-consultas..6a0512e`)
- **Fecha:** 2026-10-29
- **Puerta de calidad:** SonarQube local sin análisis real (solo SQ_UPGRADE); pendiente en B9.
- **Cobertura:** global 89 %, `domain/` ≈ 94 % (sin cambios en `domain/`).
- **Pruebas:** con `POSTGRES_PRUEBAS_URL` (base `quechua_wanka_pruebas`, credencial leída con pydantic-settings, sin imprimirla): **216 pasan, 0 omitidas**. `salvaguarda` 18/18. Ruff limpio en los archivos nuevos.
- **pip-audit:** sin vulnerabilidades conocidas. `npm audit`: no aplica (sin cambios de frontend).

## Hallazgos

| # | Sev. | Archivo | Regla | Descripción | Corrección sugerida |
|---|---|---|---|---|---|
| 1 | Mayor | `docs/evidencias/cierre_u3/b4_postgres/salida_consultas_postgres.txt` (§8) | CLAUDE.md §8 (datos fuera de Git) | La consulta 8 (`fn_demanda_insatisfecha(10, FALSE)`) imprime textos de las consultas sintéticas tomados de los conjuntos de evaluación. Uno, «¿Qué grafías empleó el autor para representar…», sale de `evaluacion_prosa.json`, que está **fuera de Git** porque contiene pasajes del corpus; otros proceden de `negativas_prosa.json` (versionado, sin problema). La salida revela contenido derivado del corpus no versionable. | Regenerar §8 sin esas filas (p. ej. `WHERE` por origen o `LIMIT` sobre abstenciones de `usuario`), o mostrar solo el recuento. |
| 2 | Menor | `tests/architecture/test_arquitectura.py` | Cobertura de la prueba | La prueba detecta de verdad (ver abajo), pero no ve `__import__("sqlalchemy")`, importaciones relativas (`level > 0`) ni rutas con prefijo `src.`. Ninguna es plausible en este código. | Anotar la limitación en el docstring. |
| 3 | Menor | `infrastructure/config.py`, `contenedor.py` | Cableado | `base_datos` es `str`: cualquier valor distinto de `sqlite` construye la URL de PostgreSQL, pero solo `"postgres"` elige el repositorio de procedimientos (con otro valor, p. ej. `pg`, queda el adaptador SQLAlchemy sobre PostgreSQL). | Usar `Literal["sqlite","postgres"]`. |
| 4 | Menor | `salida_consultas_postgres.txt:1` | Evidencia | Codificación rota en la primera línea (`�(nulo)�`). | Regenerar con `PGCLIENTENCODING=UTF8`. |
| 5 | Menor | `salida_consultas_postgres.txt` §7-8 | Privacidad | Se publican textos de 5 consultas reales de la base de desarrollo (`dron`, `criptomoneda`); son pruebas del propio equipo, sin datos personales. | Aceptable; mencionarlo en el registro. |

Sin bloqueantes.

## Verificación por foco

1. **`consultas_postgres.sql`.** El `CALL` va entre `BEGIN` y `ROLLBACK` (más un `SAVEPOINT` para el caso sin respaldo, con `ON_ERROR_STOP` restablecido); si el script se interrumpe, la sesión se cierra y la transacción se revierte. La evidencia lo confirma: usuario 5 → 6 dentro → 5 después, y el rechazo RNF-08 aparece como error esperado. Sin credenciales (la contraseña va en `PGPASSWORD`, solo mencionada) ni URL con clave en el SQL ni en `b4_postgres/` (búsqueda de password/token/secret/URL con clave: nada). La única forma quechua es `ZORRO: Atuq.` (pág. 37, del diccionario, forma verificada de CLAUDE.md §2) en un registro que se revierte; la salida no muestra otras. No hay texto del corpus en el SQL; ver hallazgo 1 para la salida.
2. **Prueba de arquitectura.** Mutaciones en el worktree sin commitear (restauradas, árbol limpio): `requests` en `domain` → falla; `sqlalchemy` en `domain` → falla (2 pruebas); `adapters.*` e `infrastructure` en `application` → falla; `psycopg` en `application` → falla; `import_module('adapters.out')` → falla; importación dentro de función → falla; comentario «postgres» en `application` → falla. No detecta `__import__(...)`, relativas ni prefijo `src.` (hallazgo 2). Detecta lo que importa.
3. **Cableado `BASE_DATOS=postgres`.** `_conectar_base_datos` usa `pool_pre_ping`, instala los procedimientos y elige `RepositorioConsultasPostgres`; por defecto SQLite + SQLAlchemy. Los dos casos están probados con un motor falso, y el de variable de entorno también. La contraseña no se registra (el mensaje de fallo solo toma la primera línea de la excepción). Ver hallazgo 3.
4. **Verificación de siempre.** Ver cabecera. El cambio en `src/` es solo un docstring de `repositorio_fuentes_port.py` (neutral respecto a PostgreSQL); no toca salvaguarda, τ ni RN-06.

## Estado de reglas
RN-01…RN-10 y RS-01…RS-08: sin cambios; cumplen. RS-05 (sin secretos): cumple.

## Veredicto: **apto** para revisión humana, con el mayor 1 a corregir en este PR (regenerar §8 de la salida) o aceptar por escrito. 0 bloqueantes · 1 mayor · 4 menores.

## Re-auditoría f1957d9 (2026-10-29)

Corrección `fix(evidencia): no exponer textos de evaluacion_prosa en la salida SQL`.

- **Hallazgo 1 (mayor): cerrado.** La sección 8 del guion y de la salida muestra ahora `left(md5(texto), 8)` y la probabilidad de cobertura; ya no hay texto de las consultas sintéticas. Conteo sin imprimir textos sobre `b4_postgres/`: 0 cadenas de `evaluacion_prosa.json` (preguntas o pasajes) y 0 fragmentos del corpus en cualquiera de los 4 archivos.
- Los textos de las consultas reales de desarrollo (§7) siguen visibles; son pruebas del propio equipo y no contienen datos personales (hallazgo 5, aceptado).
- **Observación:** la rama conserva en el historial del commit 6a0512e la versión anterior de la salida. El *squash merge* la elimina de `main`; mientras el PR esté abierto sigue alcanzable en GitHub. No requiere acción si la fusión es *squash*.
- Los menores 2, 3 y 4 siguen abiertos como deuda.

**Veredicto actualizado: apto** (0 bloqueantes · 0 mayores · 4 menores).
