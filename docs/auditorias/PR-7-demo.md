# Auditoría PR #7 · chore/demo-data-masiva (B5)

- **PR / rama:** #7 `chore/demo-data-masiva` (diff `test/procedimientos-postgres..78382ad`)
- **Fecha:** 2026-10-29
- **Puerta de calidad:** SonarQube local sin análisis real; pendiente en B9.
- **Cobertura:** global 89 %, `domain/` ≈ 94 % (sin cambios en `domain/`).
- **Pruebas:** con `POSTGRES_PRUEBAS_URL` (base `quechua_wanka_pruebas`, credencial leída con pydantic-settings, sin imprimirla): 216 pasan, 0 omitidas. `salvaguarda` 18/18; arquitectura 4/4; Vitest 21/21. **Arnés de 248 consultas reejecutado: `arnes_por_consulta.csv` y `barrido_umbral.csv` idénticos a la línea base 2980a81** (τ = 0,48 intacto). pip-audit sin vulnerabilidades.

## Hallazgos

| # | Sev. | Archivo | Regla | Descripción | Corrección sugerida |
|---|---|---|---|---|---|
| 1 | Menor | `backend/scripts/generar_transacciones.py:36,157,178` | Estilo | I001 (import de `OrigenConsulta` desordenado, ya señalado en el PR #5) y dos E501. | `ruff check --fix` y partir las líneas largas. |
| 2 | Menor | `scripts/demo/04_metricas.ps1` | Red / reproducibilidad | `npx --yes newman` descarga el paquete de la red en tiempo de ejecución (herramienta de desarrollo, no del producto; RS-03 no aplica al producto). | Documentarlo o fijar la versión (`newman@x.y.z`). |
| 3 | Menor | `scripts/demo/01_arrancar_app.ps1` | Robustez | Con `-Base sqlite` sin `-BaseDemo` no limpia `RUTA_SQLITE`/`POSTGRES_DB` heredados del entorno del usuario, que podrían redirigir la «base real». | Eliminar esas variables en la rama de uso real. |
| 4 | Menor | `data_masiva/*/consola.txt` | Evidencia | Se publican los nombres de los PDF del corpus (metadatos, no texto). Aceptable. | Ninguna. |

Sin bloqueantes ni mayores.

## Verificación por foco

1. **Scripts `scripts/demo/*.ps1`.**
   - *Idempotencia:* 01 no arranca otra API si la actual responde y detecta puertos ocupados; 02 recrea `carga.db` (dos corridas seguidas dan 800 filas, no 1600; el CSV coincide salvo la columna de latencia); 03 recrea siempre la misma base; 04 trabaja en una carpeta temporal.
   - *Base real y modelos:* ninguno toca `backend/quechua_wanka.db` (02 lo comprueba además con una defensa explícita). 03 solo ejecuta `DROP/CREATE DATABASE quechua_wanka_demo` (nombre constante, no parametrizable) y fuerza `POSTGRES_DB` por variable de entorno, que prevalece sobre `.env`. 04 entrena con `QW_MODELOS_SALIDA` en una carpeta temporal y compara `git status` de `backend/modelos` antes y después; el PR no cambia ningún modelo versionado.
   - *Credenciales:* ningún script las lee ni las imprime (solo comprueban que exista `.env`); la salida versionada no contiene contraseñas, tokens ni URL con clave (búsqueda).
   - *01 en 127.0.0.1:* uvicorn con `--host 127.0.0.1 --port 8000` y Vite con `--host 127.0.0.1 --strictPort`. Cumple RS-01.
   - **Ejecución propia** de `02_carga_sqlite.ps1 -Forzar` (dos veces) en el worktree temporal: genera 800 transacciones `carga`, y el SHA-256 y la fecha de `backend/quechua_wanka.db` del repositorio principal quedan idénticos antes y después (no se creó ninguna base real en el worktree).
2. **Privacidad.** Conteo sin imprimir textos, de las 124 cadenas de `evaluacion_prosa.json` (≥ 15 caracteres) y de 6 034 sondas de fragmentos del corpus (completos, inicio, medio y final) sobre toda la carpeta `data_masiva/`: 0 preguntas o pasajes de prosa y 0 fragmentos. La única coincidencia es el **nombre de archivo** de un PDF (campo `documento`, metadato). En el CSV las particiones E, `lema_es` y `lema_en` salen como `[huella:…]`; solo A, B, C, D y F publican texto (conjuntos versionados). El informe JSON de Newman, con respuestas completas, no se versiona (carpeta temporal). Los JSON de resumen solo traen agregados.
3. **Interfaz.** El panel de demanda añade distribución por idioma (español/inglés) y por vía, con `data-testid`; sigue mostrando el aviso rotulado de demostración y la casilla «no es demanda real» (HU-09). Prueba nueva de Vitest para ambas distribuciones (21/21). El lint solo repite el aviso `exhaustive-deps` ya conocido.
4. **Verificación de siempre.** Ver cabecera. Sin cambios en `domain/` ni en la salvaguarda; las modificaciones de `generar_transacciones.py` solo afectan a la evidencia (huellas) y a pedir las estadísticas con `incluir_sinteticas=True`, coherente con ADR-013.

## Estado de reglas
RN-01…RN-10 y RS-01…RS-08: sin cambios; cumplen (RS-01 verificada en 01, RS-05 sin secretos versionados).

## Veredicto: **apto** para revisión humana (0 bloqueantes · 0 mayores · 4 menores).

## Re-auditoría de la corrección 96e87bd (2026-10-29)

`fix(evidencia): quitar rutas del equipo de la salida de las metricas`. **Cerrado el menor 5 de `PR-10-e2e.md` (heredado de #7).** `git grep` sobre todo el árbol versionado (salvo los informes de auditoría) ya no encuentra `<usuario>` ni `C:\Users` en `docs/evidencias`; `entrenar_predictores.txt`, `pip_audit.txt` y `pytest.txt` salen con rutas genéricas y `_comun.ps1` las sustituye al guardar. Los hallazgos 1 a 4 de este informe siguen igual. **Veredicto: apto.**
