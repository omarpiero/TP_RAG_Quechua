# 05 · Tablero Kanban

> Estado vivo del trabajo. **Solo el archivista escribe en este archivo**; el resto de agentes informa al
> orquestador y este delega la actualización. Así se evitan ediciones concurrentes y estados
> contradictorios.
>
> Última actualización: **2026-10-01** · Sprint activo: **Sprint 1** (2026-09-21 → 2026-10-11) · Fase: cierre del PMV1 (`PROMPT_CIERRE_PMV1.md`, prioridades de `13_BRECHAS_RUBRICA.md` §7)

---

## 1. Reglas del tablero

### 1.1 Columnas y límites de trabajo en curso (WIP)

| Columna | Significa | Entra cuando | WIP |
|---|---|---|---|
| **Backlog** | Historia identificada, no comprometida | Existe en `03_HISTORIAS_USUARIO.md` | — |
| **Listo** | Comprometida en el sprint y cumple la DoR | Sprint Planning | — |
| **Especificando** | Se redacta `docs/specs/<ID>/spec.md` y su plan | El orquestador la toma | 2 |
| **En desarrollo** | El programador trabaja en su rama con TDD | Spec aprobada por el usuario | **1** |
| **En auditoría** | El auditor revisa seguridad, calidad y salvaguarda | PR abierto con CI en verde | 2 |
| **En revisión humana** | El usuario revisa y decide la fusión | Informe de auditoría sin bloqueantes | 2 |
| **Hecho** | Fusionada en `main` y DoD verificada | Fusión + checklist DoD completa | — |
| **Bloqueado** | No puede avanzar; se indica el motivo y qué lo desbloquea | En cualquier momento | — |

**Por qué WIP 1 en desarrollo.** Hay un único agente programador y cada historia toca el núcleo; dos
ramas abiertas a la vez sobre el mismo núcleo producen conflictos que consumen más tiempo del que ahorran.
Se revisa en cada retrospectiva.

### 1.2 Formato de tarjeta

```
[ID] Título breve · Sprint · Prior. · Agente · Rama · Desde (fecha)
```

- **Agente**: `orq` orquestador · `arc` archivista · `prg` programador · `aud` auditor · `hum` usuario.
- **Rama**: según ADR-011 (p. ej., `feat/HU-03-consulta-lexica`).
- Toda tarjeta en **Bloqueado** lleva `Motivo:` y `Desbloquea:`.
- Cada movimiento se anota también en `04_SPRINTS.md` §7.

---

## 2. Tablero

### Backlog

| Tarjeta | Sprint | Prior. | Nota |
|---|---|---|---|
| [HU-01] Cargar documentos con procedencia | S1 | Alta | Promover `poc/ingest2.py` |
| [HU-02] Segmentar e indexar el corpus | S1 | Alta | Depende de HU-01 |
| [HT-01] Arnés de evaluación reproducible | S1 | Alta | Reproducir línea base de la PoC |
| [HT-02] Conjunto de evaluación externo (docentes EIB) | S1–S2 | Alta | **Tarea humana** · ver HUM-02 |
| [NUC-01] Núcleo: normalización y depuración de la consulta | S1 | Alta | Sin dependencias externas |
| [HU-06] Salvaguarda de abstención | S2 | Alta | `@salvaguarda` |
| [HU-07] Trazabilidad documental | S2 | Alta | — |
| [HU-03] Consulta léxica | S2 | Alta | — |
| [HT-04] Servicio local e interfaz de escritorio | S2 | Alta | RS-01, RS-03 |
| [HT-03] Traducción de la consulta y recalibración de τ | S2 | Alta | Antes de HU-05 |
| [HU-05] Respuesta en el idioma de la consulta | S2 | Media | ADR-008 |
| [HU-04] Consulta de contenido cultural | S2 | Media | Requiere RD-05 |
| [HT-06a] Medición de rendimiento en escritorio | S2 | Alta | — |
| [HT-07] Espiga: bge-m3 como complemento | S2 | Baja | — |
| [HT-08] Servidor MCP de desarrollo (solo lectura) | S1–S2 | Media | ADR-017 · tras HU-02 y HT-01 |
| [ADR-018] Confirmar identificador de fragmento | S1 | Alta | Antes de iniciar HU-02 |
| [HT-05] Artefactos móviles y equivalencia | S3 | Alta | Requiere ADR-012 |
| [HU-08.1] Predicción de cobertura | S3 | Alta | Requiere ADR-013 |
| [HU-08.2] Umbral adaptativo | S3 | Alta | Tras HU-08.1 |
| [HU-09] Priorización del corpus | S3 | Media | Requiere ADR-013 |
| [HU-10.1] Consulta sin conexión en el teléfono | S4 | Alta | — |
| [HU-10.2] Salvaguarda en el teléfono | S4 | Alta | `@salvaguarda` |
| [HU-10.3] Instalación con verificación de espacio | S4 | Alta | — |
| [HU-11] Interfaz accesible | S4 | Media | — |
| [HT-06b] Medición en dispositivo | S4 | Alta | — |

**Cierre del PMV1 · lista P0 de `13_BRECHAS_RUBRICA.md` §7** (sustituye a la del prompt §5; las ramas que no figuran se fijan en la spec de cada PR):

| Tarjeta | Sprint | Prior. | Nota |
|---|---|---|---|
| [PR-03] Reglas de respuesta explícitas: τ solo desde configuración, `UmbralConLema` (ADR-021, 5 condiciones), `PasajesSinAfirmacion`, `RespuestaFactory`; corrige **D-1** y **D-6** | S1 | P0 | prg · depende de PR-01 y PR-02 · caso C-10 del video · prueba `@salvaguarda` con generador que lanza excepción |
| [PR-04] `VerificadorFormaLiteral` | S1 | P0 | prg · depende de PR-03 |
| [PR-06] Corregir entradas truncadas (**D-4**) con prueba de regresión | S1 | P0 | prg · requisito de la condición 3 de ADR-021 |
| [PR-07] Interfaz: UI-01…05, 07, 08, **10** (responsive) y **13** (indicadores de similitud frente a τ, latencia, vía de respaldo, nº de fragmentos) | S1 | P0 | prg · G-14, G-15 · corrige **D-5** |
| [PR-08] Historial: SQLite por defecto + borrado + aviso | S1 | P0 | prg · **bloqueada por decisión**: confirmar ADR-027 y ADR-013 (el usuario no expresó preferencia el 2026-10-01) |
| [PR-09] Prueba de arquitectura + Gherkin de HU-03, HU-06 y HU-07 | S1 | P0 | prg · incluye conteo de escenarios aprobados por HU (G-13) |
| [PR-10r] CI reducida: SonarQube + cobertura + Newman (M8, M9, M10) | S1 | P0 | prg + aud · G-07 · MCP de Sonar por JAR; el servidor Cloud necesita `SONARQUBE_ORG` y token (pendiente del usuario) |
| [PR-11] `medir_pmv1.py`: M1–M8, M13–M15, **M3-bis** y **M16** (cálculo) | S1 | P0 | prg · salida a `docs/evidencias/` |
| [GH-PRJ] GitHub Projects con tarjetas de los PR | S1 | P0 | hum ejecuta `.github/projects/crear_projects.ps1` · G-05 |
| [M16-MED] Medir M16 a mano (KPI AS-IS) con la hoja `docs/evidencias/m16/kpi_asis.csv` | S1 | P0 | **hum (equipo)**: dos integrantes que no hayan trabajado con el corpus · G-01 |
| [DOC-11-3] Rellenar `docs/11` §3 con salidas reales de cada caso del video | S1 | P0 | orq/arc · tras PR-03…PR-08 |
| [PR-INTEG] Un PR propio por integrante, desde su cuenta | S1 | P0 | **hum (equipo)** · G-17 · no delegable en agentes (`docs/10` §6) |
| [ARB-PTO] `docs/evidencias/arbol_src.txt` y `puertos.md` (puertos IN/OUT, adaptadores y cableado) | S1 | P0 | prg · al cerrar PR-02 · G-12 |

### Listo

| Tarjeta | Sprint | Prior. | Agente | Desde |
|---|---|---|---|---|
| [HT-00] Repositorio, CI y entorno de agentes (parte de configuración ya hecha) | S1 | Alta | hum + prg + aud | 2026-09-24 |
| [HUM-01] Completar licencias y fuentes del manifiesto del corpus | S1 | Alta | hum | 2026-09-24 |
| [HUM-02] Solicitar consultas a docentes de EIB (HT-02) | S1 | Alta | hum | 2026-09-24 |
| [PR-01] Estructura hexagonal `backend/src/` sin cambiar el comportamiento (HT-00) · rama `refactor/estructura-hexagonal` · spec `docs/specs/PR-01-estructura-hexagonal/spec.md` redactada (Borrador), **pendiente de aprobación del usuario** | S1 | P0 | prg | 2026-10-01 |
| [PR-02] Puertos de entrada, controladores REST por recurso y CLI (HT-00) · rama `feat/puertos-entrada` · spec `docs/specs/PR-02-puertos-entrada/spec.md` redactada (Borrador), **pendiente de aprobación del usuario** · depende de PR-01 | S1 | P0 | prg | 2026-10-01 |

### Especificando

| Tarjeta | Sprint | Agente | Desde |
|---|---|---|---|
| — | | | |

### En desarrollo · WIP 1

| Tarjeta | Sprint | Agente | Rama | Desde |
|---|---|---|---|---|
| — | | | | |

### En auditoría · WIP 2

| Tarjeta | Sprint | Agente | PR | Desde |
|---|---|---|---|---|
| — | | | | |

### En revisión humana · WIP 2

| Tarjeta | Sprint | Agente | Qué revisar | Desde |
|---|---|---|---|---|
| [DOC-00] Documentación SDD base (`docs/`) | S1 | hum | Contexto, requerimientos, historias, plan, modelo de agentes y ADR | 2026-09-24 |
| [DOC-01] `CLAUDE.md`, subagentes, `settings.json`, `.mcp.json`, corpus y `referencia_poc/` | S1 | hum | Que las reglas y el reparto de trabajo reflejen lo acordado | 2026-09-24 |

### Hecho

| Tarjeta | Sprint | Fusionada | Evidencia |
|---|---|---|---|
| [ADR-009/010/011/015/017] Agentes, SonarQube, Git, corpus fuera de Git, MCP de desarrollo | S1 | No aplica | Respuestas del usuario del 2026-09-24 · `07_DECISIONES.md` |
| [CP-01] Línea base del arnés congelada (pasos 1–3 del prompt): 40/40 pruebas, 248 consultas, barrido con y sin regla de lema | S1 | No aplica | `docs/evidencias/2026-10-01_base-integrante_pc-rtx4060/` (`resumen_arnes.json`, `arnes_por_consulta.csv`, `barrido_umbral.csv`, `junit.xml`, `meta.json`) generada con `backend/scripts/arnes_linea_base.py` |
| [CP-02] M16 preparado: lista de 25 consultas (20 de A, 5 de C; semilla 2026) y hoja `kpi_asis.csv` vacía. La **medición** es de `[M16-MED]` (Backlog) | S1 | No aplica | `docs/evidencias/m16/` (`lista_m16.csv`, `kpi_asis.csv`, `README.md`) |
| [DEC-02] Decisiones del usuario del 2026-10-01: ADR-021 aceptada (5 condiciones) · τ 0,48 confirmado · D-6 · `13_BRECHAS_RUBRICA.md` adoptado | S1 | No aplica | `07_DECISIONES.md` (ADR-020, ADR-021) · `13_BRECHAS_RUBRICA.md` |

### Bloqueado

| Tarjeta | Motivo | Desbloquea | Desde |
|---|---|---|---|
| — | | | |

---

## 3. Indicadores del sprint activo

| Indicador | Valor |
|---|---|
| Tarjetas comprometidas | 8 originales (HT-00, HU-01, HU-02, HT-01, HT-02, NUC-01, HUM-01, HUM-02) + 15 del cierre del PMV1 (2 en Listo: PR-01, PR-02; 13 en Backlog: PR-03, 04, 06, 07, 08, 09, 10r, 11, GH-PRJ, M16-MED, DOC-11-3, PR-INTEG, ARB-PTO) |
| Tarjetas en Listo (spec redactada, pendiente de aprobación) | PR-01, PR-02 (más HT-00, HUM-01, HUM-02) |
| Tarjetas en Hecho | 4 (decisiones del 2026-09-24, CP-01, CP-02, DEC-02) |
| Tarjetas bloqueadas | 0 (PR-08 depende de una decisión pendiente, aún en Backlog) |
| Pruebas del código base | 40/40 en verde (`junit.xml` de la línea base, 2026-10-01); no es `main` fusionado |
| Pruebas `@salvaguarda` en verde en `main` | por registrar (aún no existe prueba etiquetada) |
| Puerta de calidad de SonarQube en `main` | por registrar |

---

## 4. Registro de cambios

| Fecha | Cambio |
|---|---|
| 2026-10-01 | Tarjetas del P0 de `13_BRECHAS_RUBRICA.md` §7 (PR-01…PR-11, GH-PRJ, M16-MED, DOC-11-3, PR-INTEG, ARB-PTO); PR-01 y PR-02 a «Listo»; CP-01, CP-02 y DEC-02 a «Hecho»; indicadores |
