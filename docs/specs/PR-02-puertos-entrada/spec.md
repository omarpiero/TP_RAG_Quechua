# Spec · PR-02 · Puertos de entrada, controladores REST por recurso y CLI

> Modo cierre del PMV1 (`CLAUDE.md` §4; `PROMPT_CIERRE_PMV1.md` §7): spec breve. **No entra en desarrollo
> sin la aprobación del usuario** (§9). Depende de PR-01.

| Campo | Valor |
|---|---|
| Historia | HT-00 — [Repositorio, integración continua y entorno de agentes](../../03_HISTORIAS_USUARIO.md) (E2 «interfaces de puertos de entrada»; E3 flujo Controller → Input Port → Use Case; hallazgo B-1 de `08_AUDITORIA_REPO_BASE.md`; G-11 y G-12 de `13_BRECHAS_RUBRICA.md`) |
| Épica · PMV · Sprint | — (habilitador) · PMV1 · Sprint 1 |
| Requisitos | ADR-002 · ADR-017 (segundo adaptador de entrada) · `CONSIDERACIONES.md` §4 y §5 (PR 2) · RS-01 |
| Rama | `feat/puertos-entrada` |
| Rol | Architect + Backend (ejecuta el programador) |
| Estado | **Borrador** |
| Versión · fecha | 0.1 · 2026-10-01 |

## 1. Contexto y objetivo

Hoy `api.py` llama a casos de uso, al repositorio y al contenedor directamente, y no existen puertos de entrada.
Se introducen los puertos de entrada, se parte la API por recurso y se añade un segundo adaptador de entrada
(CLI), de modo que el flujo sea Controlador → Puerto de entrada → Caso de uso → Puerto de salida → Adaptador,
sin cambiar reglas ni respuestas.

## 2. Alcance

**Incluye:**
- **Puertos de entrada** (ABC en `application/ports/in/`): `ConsultarCorpusPort`, `IngestarDocumentoPort`,
  `GestionarFuentesPort`, `ConsultarHistorialPort`, `ReindexarCorpusPort`. Cada caso de uso de
  `application/use_cases/` implementa **exactamente uno**; se crean `ConsultarHistorialUseCase` y
  `ReindexarCorpusUseCase`.
- **REST:** `api.py` se divide en `adapters/in/rest/{consultas_controller,historial_controller,
  fuentes_controller,corpus_controller,sistema_controller}.py` + `esquemas.py`. Cada controlador solo traduce
  HTTP ↔ DTO y depende **del puerto** (obtenido del contenedor con `Depends`), sin lógica. **Mismas rutas,
  mismos códigos y mismos esquemas**: la colección Postman de `docs/` sigue valiendo.
- **CLI** `adapters/in/cli/` (`python -m adapters.in.cli <comando>` desde `backend/src`): `indexar`,
  `consultar "<texto>"`, `calibrar` (envuelve `scripts/calibrar_umbral.py` o el arnés) y `exportar-movil`.
  `medir` se añade en el PR-11.
- `infrastructure/contenedor.py` cablea puertos → implementaciones (inyección de dependencias); `main.py`
  monta los routers.
- **Log estructurado por capa**, nivel INFO: controlador → puerto → caso de uso → índice → evaluador →
  generador → repositorio (necesario para el video, `CONSIDERACIONES.md` §9).
- Al cerrar: exportar `docs/evidencias/arbol_src.txt` y `docs/evidencias/puertos.md` (puertos IN/OUT,
  adaptadores y cableado) — G-12.

**Excluye:** reglas de respuesta (PR-03), SQLite (PR-08), cambios de interfaz, servidor MCP (HT-08).

## 3. Criterios de aceptación

HT-00 no tiene escenarios Gherkin en `03_HISTORIAS_USUARIO.md`; criterio literal: «**Hecho cuando** un PR de
prueba recorre todo el circuito y SonarQube Cloud comenta el PR». Los criterios medibles de este PR están en el
§5 (criterio de éxito). Sin cambios a `03`.

## 4. Plan técnico

- **Puertos afectados:** nuevos los cinco de entrada; los de salida no cambian.
- **Adaptadores:** REST dividido; CLI nuevo; contenedor modificado.
- **Núcleo (`domain/`):** sin cambios.
- **Datos y configuración:** τ no cambia (0,48, ADR-020); sin cambios de datos.
- **Riesgos:** cambio involuntario de rutas, códigos o esquemas (mitigación: pruebas de controladores con
  `TestClient` y colección Postman); dependencia circular contenedor ↔ controladores; que la CLI y la API
  difieran (se prueba contra el mismo caso de uso).

## 5. Plan de pruebas

| Tipo | Qué se prueba | Archivo |
|---|---|---|
| Unitaria (TDD) | Casos de uso con **fakes** de los puertos de salida, sin BD ni Ollama (G-11); en la captura `QA-1` se ve que no hay BD ni Ollama | `backend/tests/unit/application/test_consultar_corpus_con_fakes.py` |
| Unitaria | Controladores con `TestClient`: mismas rutas, códigos y esquemas | `backend/tests/unit/adapters/in/rest/…` |
| Unitaria | CLI `consultar "<texto>"` devuelve lo mismo que la API para «zorro» | `backend/tests/unit/adapters/in/cli/…` |
| Estructura | Ningún controlador importa `use_cases` ni `adapters/out` (solo puertos); comprobación con `grep` (prueba formal en PR-09) | salida adjunta al PR |
| Arnés | **Comparar con la línea base** `docs/evidencias/2026-10-01_base-integrante_pc-rtx4060/`: `arnes_por_consulta.csv` y `barrido_umbral.csv` idénticos; si cambia algo, se detiene y se informa | `docs/evidencias/…` |
| Previas | Las pruebas del PR-01 siguen en verde | `backend/tests/` |

**Criterio de éxito:** arnés idéntico a la línea base · pruebas previas en verde + pruebas nuevas · controladores
solo dependen de puertos · CLI y API coinciden para «¿cómo se dice zorro en quechua wanka?» (`ZORRO: Atuq.`,
pág. 37) · `arbol_src.txt` y `puertos.md` generados.

## 6. Tareas (en orden, cada una con su prueba)

| # | Tarea | Prueba que la guía | Estado |
|---|---|---|---|
| 1 | Definir los cinco puertos de entrada | Prueba de que cada caso de uso implementa uno | Pendiente |
| 2 | Crear `ConsultarHistorialUseCase` y `ReindexarCorpusUseCase` | Pruebas con fakes | Pendiente |
| 3 | Pruebas de casos de uso con fakes (`test_consultar_corpus_con_fakes.py`) | Sin BD ni Ollama | Pendiente |
| 4 | Dividir `api.py` en controladores por recurso con `Depends` sobre el puerto | `TestClient`: mismas rutas, códigos y esquemas | Pendiente |
| 5 | Cablear en `contenedor.py` y montar routers en `main.py` | Arranque de la API; humo «zorro» | Pendiente |
| 6 | CLI (`indexar`, `consultar`, `calibrar`, `exportar-movil`) | CLI = API para «zorro» | Pendiente |
| 7 | Log por capa a nivel INFO | Prueba de que la secuencia aparece en el log | Pendiente |
| 8 | Exportar `arbol_src.txt` y `puertos.md`; ejecutar el arnés | CSV idénticos a la línea base | Pendiente |

## 7. Seguridad y calidad (para el auditor)

RS-01 (API solo en `127.0.0.1`); validación de entradas en los controladores (RS-02) sin cambios; que el log
INFO no escriba datos personales ni texto íntegro del corpus; la CLI no expone herramientas que escriban en
`config/` ni en `corpus/`.

## 8. Definición de Terminado

- [ ] DoD-1 · [ ] DoD-2 · [ ] DoD-3
- [ ] **DoD-4 salvaguarda** (arnés idéntico a la línea base) · [ ] DoD-5 operación local · [ ] DoD-6 n/a
- [ ] DoD-7 n/a · [ ] DoD-8 · [ ] DoD-9 docs al día (`arbol_src.txt`, `puertos.md`)
- [ ] DoD-10 auditoría sin bloqueantes + aprobación humana

## 9. Aprobación y registro

| Fecha | Evento | Quién |
|---|---|---|
| 2026-10-01 | Spec redactada (Borrador) | Archivista |
| | Spec aprobada | Usuario |
