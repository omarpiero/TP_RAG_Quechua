# Spec · PR-01 · Estructura hexagonal `backend/src/` sin cambiar el comportamiento

> Modo cierre del PMV1 (`CLAUDE.md` §4; `PROMPT_CIERRE_PMV1.md` §7): spec breve. **No entra en desarrollo
> sin la aprobación del usuario** (§9).

| Campo | Valor |
|---|---|
| Historia | HT-00 — [Repositorio, integración continua y entorno de agentes](../../03_HISTORIAS_USUARIO.md) (estructura que exige la lista de cotejo E2; brecha G-10 de `13_BRECHAS_RUBRICA.md`) |
| Épica · PMV · Sprint | — (habilitador) · PMV1 · Sprint 1 |
| Requisitos | ADR-002 (hexagonal) · `CONSIDERACIONES.md` §4.1 y §5 (PR 1) · RN-10 no afectada |
| Rama | `refactor/estructura-hexagonal` |
| Rol | Architect & System Designer (ejecuta el programador) |
| Estado | **Borrador** |
| Versión · fecha | 0.1 · 2026-10-01 |

## 1. Contexto y objetivo

El código base del integrante tiene las capas repartidas en `backend/{domain,application,infrastructure}` y no
coincide con los nombres de capa que exige la rúbrica. Se mueve todo a `backend/src/{domain,application,
adapters,infrastructure}` (`CONSIDERACIONES.md` §4.1) **sin cambiar el comportamiento** y conservando el
historial con `git mv`.

## 2. Alcance

**Incluye** (mapa de movimientos; nombres de clase sin cambios):

| Origen | Destino |
|---|---|
| `backend/domain/{entities,value_objects}` | `backend/src/domain/…` |
| `backend/domain/ports/*` | `backend/src/application/ports/out/*` |
| `backend/application/services/{depurador_consulta,evaluador_confianza,segmentador}.py` (solo usan biblioteca estándar) | `backend/src/domain/services/` |
| `DocumentoExtraido` (hoy en `domain/ports/extraccion_documental_port.py`) | `domain/entities/`, para que `Segmentador` no importe de `application` |
| `backend/application/use_cases` | `backend/src/application/use_cases` |
| `infrastructure/adapters/input/{api.py,esquemas.py}` | `src/adapters/in/rest/` (no se divide aquí: es del PR-02) |
| `indice_hibrido_lexico` | `adapters/out/recuperacion/` |
| `ollama_generador` | `adapters/out/generacion/` |
| `traductor_tabla`, `ollama_traductor` | `adapters/out/traduccion/` |
| `detector_idioma_heuristico` | `adapters/out/idioma/` |
| `extractor_pdf`, `corpus_jsonl` | `adapters/out/documentos/` |
| `persistencia/*` | `adapters/out/persistencia/` (el renombrado a SQLite es del PR-08) |
| `infrastructure/{config.py,contenedor.py}` y `backend/main.py` | `src/infrastructure/{config.py,contenedor.py,main.py}`; la raíz de datos sigue siendo `backend/` (ajustar `parents[…]`) |
| Pruebas | `backend/tests/unit/…` por capa; `conftest.py` ajustado; los scripts añaden `src/` al `sys.path` |
| `ejecutable.py`, `QuechuaWankaWeb.spec` | quedan en `backend/` con rutas actualizadas; no entran en el PMV1 ni en la CI |

**Añade:** `backend/pyproject.toml` (pytest con `pythonpath = ["src"]` y marcadores `salvaguarda`, `lento`,
`datos`; configuración de ruff) · `backend/requirements-dev.txt` (pytest, pytest-cov, pytest-bdd 8.x, ruff,
pip-audit) · `.gitattributes` con `* text=auto` (`13_BRECHAS_RUBRICA.md` §1: 149 archivos aparecen modificados
solo por fin de línea) · los comandos definitivos de `CLAUDE.md` §9; la API arranca con
`uvicorn infrastructure.main:app --app-dir src --host 127.0.0.1 --port 8000`.

**Excluye:** puertos de entrada y división de `api.py` (PR-02); cualquier cambio de reglas, τ, interfaz o
datos; prueba de arquitectura formal (PR-09).

## 3. Criterios de aceptación

HT-00 no tiene escenarios Gherkin en `03_HISTORIAS_USUARIO.md`; su criterio literal es: «**Hecho cuando** un PR
de prueba recorre todo el circuito y SonarQube Cloud comenta el PR». Este PR aporta la parte de estructura; los
criterios medibles de esta spec están en el §5 (criterio de éxito).

> Nota: el texto de HT-00 en `03` nombra `src/rag_quechua/{dominio,puertos,…}`; rige `CONSIDERACIONES.md` §4.1
> y `CLAUDE.md` §6 (jerarquía de `CLAUDE.md`). No se edita `03` sin ADR.

## 4. Plan técnico

- **Puertos afectados:** los de salida pasan a `application/ports/out/`; solo cambian de ruta de importación.
- **Adaptadores:** solo cambian de ruta.
- **Núcleo (`domain/`):** reciben los tres servicios y `DocumentoExtraido`; siguen usando solo la biblioteca
  estándar (se comprueba con `grep`; la prueba formal es del PR-09).
- **Datos y configuración:** τ no cambia (0,48, ADR-020). Los datos siguen en `backend/data/`.
- **Riesgos:** rutas de datos al cambiar de profundidad (`parents[…]`); importaciones circulares al mover
  servicios; finales de línea (mitigado con `.gitattributes`).

## 5. Plan de pruebas

| Tipo | Qué se prueba | Archivo |
|---|---|---|
| Unitaria | Las 40 pruebas existentes, movidas por capa, siguen en verde | `backend/tests/unit/…` |
| Arnés | **Comparar con la línea base** `docs/evidencias/2026-10-01_base-integrante_pc-rtx4060/`: `scripts/arnes_linea_base.py` debe producir `arnes_por_consulta.csv` y `barrido_umbral.csv` **idénticos byte a byte**. Si cambia algo, **se detiene y se informa** | `docs/evidencias/…` |
| Humo | La API arranca en `127.0.0.1`; `POST /api/consultas` con «¿cómo se dice zorro en quechua wanka?» responde `ZORRO: Atuq.`, pág. 37 | manual + registro |
| Historial | `git log --follow` conserva la historia de los archivos movidos | salida adjunta al PR |
| Arquitectura | `grep`: ninguna importación de `domain/` fuera de la biblioteca estándar | salida adjunta al PR |

**Criterio de éxito:** 40/40 en verde · arnés idéntico byte a byte · historial conservado · `domain/` sin
terceros · API operativa con el caso «zorro».

## 6. Tareas (en orden, cada una con su prueba)

| # | Tarea | Prueba que la guía | Estado |
|---|---|---|---|
| 1 | `.gitattributes`, `pyproject.toml`, `requirements-dev.txt` | `pytest` descubre las pruebas con `pythonpath = ["src"]` | Pendiente |
| 2 | Mover `domain/` (entidades, objetos de valor, servicios; `DocumentoExtraido`) | Pruebas de dominio en verde; `grep` de importaciones | Pendiente |
| 3 | Mover puertos y casos de uso a `application/` | Pruebas de casos de uso en verde | Pendiente |
| 4 | Mover adaptadores a `adapters/{in,out}/…` y `infrastructure/` | Pruebas de adaptadores en verde; rutas de datos | Pendiente |
| 5 | Mover pruebas y ajustar scripts y `conftest.py` | 40/40 | Pendiente |
| 6 | Arnés y humo de la API | CSV idénticos; «zorro» → `ZORRO: Atuq.`, pág. 37 | Pendiente |

## 7. Seguridad y calidad (para el auditor)

Sin entradas externas nuevas. Verificar RS-01 (API solo en `127.0.0.1`) tras mover `main.py`; que no se
versione ningún dato (PDF, `fragmentos_*.jsonl`, índices, `.db`, `.env`); ruff y `pip-audit` con los comandos
de `CLAUDE.md` §9.

## 8. Definición de Terminado

- [ ] DoD-1 · [ ] DoD-2 (pruebas previas en verde) · [ ] DoD-3
- [ ] **DoD-4 salvaguarda** (arnés idéntico a la línea base) · [ ] DoD-5 operación local · [ ] DoD-6 n/a
- [ ] DoD-7 n/a · [ ] DoD-8 versionado y reproducible · [ ] DoD-9 docs al día (`CLAUDE.md` §9)
- [ ] DoD-10 auditoría sin bloqueantes + aprobación humana

## 9. Aprobación y registro

| Fecha | Evento | Quién |
|---|---|---|
| 2026-10-01 | Spec redactada (Borrador) | Archivista |
| | Spec aprobada | Usuario |
