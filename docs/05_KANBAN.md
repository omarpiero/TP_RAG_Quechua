# 05 · Tablero Kanban

> Estado vivo del trabajo. **Solo el archivista escribe en este archivo**; el resto de agentes informa al
> orquestador y este delega la actualización. Así se evitan ediciones concurrentes y estados
> contradictorios.
>
> Última actualización: **2026-09-24** · Sprint activo: **Sprint 1 · semana 1** (2026-09-21 → 2026-10-11)

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

### Listo

| Tarjeta | Sprint | Prior. | Agente | Desde |
|---|---|---|---|---|
| [HT-00] Repositorio, CI y entorno de agentes (parte de configuración ya hecha) | S1 | Alta | hum + prg + aud | 2026-09-24 |
| [HUM-01] Completar licencias y fuentes del manifiesto del corpus | S1 | Alta | hum | 2026-09-24 |
| [HUM-02] Solicitar consultas a docentes de EIB (HT-02) | S1 | Alta | hum | 2026-09-24 |

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

### Bloqueado

| Tarjeta | Motivo | Desbloquea | Desde |
|---|---|---|---|
| — | | | |

---

## 3. Indicadores del sprint activo

| Indicador | Valor |
|---|---|
| Tarjetas comprometidas | 8 (HT-00, HU-01, HU-02, HT-01, HT-02, NUC-01, HUM-01, HUM-02) |
| Tarjetas en Hecho | 1 (decisiones) |
| Tarjetas bloqueadas | 0 |
| Pruebas `@salvaguarda` en verde en `main` | por registrar (aún no existe `main`) |
| Puerta de calidad de SonarQube en `main` | por registrar |
