# Auditoría · PR #3 · BUG-02

- **PR y rama:** #3 `chore/deps-seguridad` (1 commit, `Refs: BUG-02`) · commit 81e7aa3
- **Fecha:** 2026-10-29
- **Alcance:** `backend/requirements*.txt`, una prueba de rutas, evidencias en `docs/evidencias/cierre_u3/b1_deps/`. No toca `src/`, `frontend/` ni τ.
- **Veredicto:** **APTO** para revisión humana (0 bloqueantes, 0 mayores, 4 menores).

## Evidencias

| Control | Resultado |
|---|---|
| Puerta de calidad SonarQube | **No verificable**: el MCP `sonarqube-local` no está disponible en esta sesión y el PR no tiene CI (`gh pr checks`: sin comprobaciones; no hay `.github/workflows` en la rama). Sustituido por análisis local de pruebas y cobertura. |
| Pruebas (worktree limpio, venv del repo principal) | 128 pasan · 3 omitidas (PostgreSQL, falta `POSTGRES_PRUEBAS_URL`) · 0 fallos |
| `pytest -m salvaguarda` | 18 pasan |
| Cobertura | global **78 %** (mínimo 70 %) · `domain/` **93,8 %** (mínimo 90 %) |
| `pip-audit -r requirements.txt` / `-r requirements-dev.txt` | "No known vulnerabilities found" en ambos |
| `pip check` | sin requisitos rotos |
| `npm audit` | no aplica (el PR no toca `frontend/`) |
| Arnés `scripts/arnes_linea_base.py` (248 consultas) | `arnes_por_consulta.csv` y `barrido_umbral.csv` **idénticos byte a byte** a `docs/evidencias/cierre_u3/00_linea_base_2980a81/arnes/` |
| `ruff` | prueba modificada limpia; el repo tiene 22 avisos preexistentes en otros archivos (no atribuibles al PR) |

## Saltos de versión mayor

- **pytest 8 → 9** (9.2.0) con `pytest-bdd 8.1.0` y `pytest-cov 7.1.0`: suite completa y escenarios Gherkin pasan. Sin hallazgo.
- **starlette 0.41 → 1.10 / fastapi 0.115 → 0.162:** la suite REST pasa; el servicio sigue ligado a `127.0.0.1` (`ejecutable.py:109`); la validación de entrada no cambió. Aparece `StarletteDeprecationWarning` (uso de `httpx` con `starlette.testclient`; sugiere `httpx2`). Ver H-2.
- **pypdf 5 → 6 (6.21.4):** ver sección siguiente.

## Riesgo de pypdf 6 sobre la extracción (solo cifras)

`ExtractorPdf` + `Segmentador` actuales sobre 2 PDF, comparado con `fragmentos_v3.jsonl` (sin escribir en corpus ni índice):

| Documento | Págs. | Págs. con texto (pypdf 6) | Fragmentos nuevos | Fragmentos en v3 | Págs. con distinto n.º de fragmentos |
|---|---|---|---|---|---|
| Diccionario wanka (`293274822-…`, lexicográfico) | 37 | 37 (100 %) | 2 360 | 2 351 (+0,4 %) | 33 de 37 (suma de diferencias: 63) |
| Saberes y Haceres VII (prosa) | 110 | 110 | 166 | 204 | 39 de 110 (suma: 40) |

- Diccionario: lemas detectados 2 327 (nuevo) frente a 2 267 (v3); 2 251 comunes, 76 solo en el nuevo, 16 solo en v3. Caracteres totales 75 782 frente a 75 604.
- Prosa: caracteres 105 802 frente a 99 196; la página 110 tiene texto nuevo (32 caracteres) y ningún fragmento en v3.
- Los identificadores no son comparables (v3 usa `md5(nombre|pág|índice)`, el segmentador actual usa hash del texto), por lo que la comparación es por página y por lema.
- **Limitación:** no se pudo aislar el efecto de pypdf 6 de las demás causas de diferencia (v3 es una reingesta con acentos reparados y distinta segmentación; la prosa difiere por tamaño de bloque). No hay pypdf 5.1.0 instalado y descargarlo requería autorización; no se hizo. Las diferencias en el diccionario (±0,4 % de fragmentos, 76 lemas nuevos frente a 16 perdidos) son pequeñas pero no nulas. Ninguna página con texto en v3 queda sin texto con pypdf 6 (la cobertura de páginas no empeora).
- pypdf 6 emite avisos "fontTools is required to fully parse the encoding of a CFF Type1 font" al leer el PDF de prosa; `fonttools` no está instalado. Puede degradar la codificación de esa fuente (no medido).
- Efecto sobre la salvaguarda: el arnés usa `fragmentos_v3.jsonl` ya extraído, de modo que **no ejercita pypdf**; su igualdad prueba que el PR no cambia el comportamiento de consulta, no que una reingesta con pypdf 6 dé el mismo índice.

## Hallazgos

| ID | Sev. | Archivo:línea | Regla | Descripción | Corrección sugerida |
|---|---|---|---|---|---|
| H-1 | Menor | `backend/src/adapters/out/documentos/extractor_pdf.py` · `backend/requirements.txt` | RN-02/RN-10 (calidad de extracción) | El PR sube pypdf a 6 sin medir una reingesta con 5.1.0 frente a 6.21.4; las cifras de arriba no aíslan el efecto. Avisos de `fontTools` ausente en el PDF de prosa. | Antes de reingestar el corpus con esta versión, comparar 5.1.0 frente a 6.21.4 por documento (páginas con texto, fragmentos, lemas); evaluar añadir `fonttools` a `requirements.txt`. No bloquea: el índice vigente no se regenera con este PR. |
| H-2 | Menor | `backend/tests/unit/adapters/in/rest/test_controladores.py:120-139` | Pruebas | La prueba de rutas ahora lee `app.openapi()["paths"]`, que omite rutas con `include_in_schema=False` (`/` y `/{recurso:path}` en `infrastructure/main.py:64,68`) y la comparación es `esperadas <= rutas` (subconjunto): no detecta rutas nuevas inesperadas. Las 14 rutas esperadas coinciden con las anteriores. Además, `StarletteDeprecationWarning` por `httpx` en `TestClient`. | Asumido el cambio (es equivalente para la API pública). Considerar igualdad estricta sobre `/api/*` y migrar a `httpx2` cuando se estabilice. |
| H-3 | Menor | `docs/evidencias/cierre_u3/b1_deps/justificacion.md` | Trazabilidad | El documento declara que los 3 saltos mayores "requieren ADR", pero el PR no incluye ni referencia ninguno (el registro es del archivista en `docs/07`). | Que el archivista registre el ADR de actualización (pypdf 6, starlette 1.x, pytest 9) antes o al fusionar. |
| H-4 | Menor | `backend/requirements.txt` (`pytest==9.2.0`) | RS (superficie de dependencias) | `pytest` figura entre las dependencias de ejecución (preexistente) y `starlette` queda fijada aparte de `fastapi`; ambos pines pueden divergir en futuras actualizaciones. | Mover `pytest` a `requirements-dev.txt` y anotar por qué se fija `starlette`. Deuda, no del PR. |

Adicional (informativo): sin CI en el repositorio, la regla 10 de `CLAUDE.md` ("CI en verde") no se puede comprobar en este PR; las pruebas se ejecutaron localmente.

## RN-01…RN-10

| RN | Estado |
|---|---|
| RN-01…RN-05, RN-07…RN-10 | Sin cambios en `src/`; pruebas de salvaguarda (18) y arnés idéntico. Cumplen. |
| RN-06 (predictores solo añaden abstenciones) | Sin cambios en `src/` ni en scikit-learn (1.6.0 fijado); pruebas `test_predictor_sklearn.py` y `test_prediccion_con_fakes.py` pasan. Cumple. |

## RS-01…RS-08

| RS | Estado |
|---|---|
| RS-01 (solo `127.0.0.1`) | Cumple (`ejecutable.py:109`). |
| RS-02 (validación 1–300) | Suite REST verde bajo starlette 1.10. |
| RS-03/04/05/06 (sin telemetría, secretos, PDF/pesos en Git, red saliente) | Sin cambios; no se leyó `backend/.env`. PR solo versiona requirements, una prueba y evidencias JSON/MD. Cumple. |
| RS-07 (dependencias) | Cumple: `pip-audit` limpio (75 avisos únicos → 0 según la evidencia; verificado hoy). |
| RS-08 (MCP) | No aplica. |

## Veredicto

**Apto** para revisión humana. Reservas a registrar: SonarQube no consultado (MCP no disponible) y ausencia de CI; efecto de pypdf 6 sobre una futura reingesta sin medir (H-1).
