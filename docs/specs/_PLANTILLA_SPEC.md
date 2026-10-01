# Spec · <ID> · <título de la historia>

> Copiar a `docs/specs/<ID>/spec.md`. La redacta el archivista con lo acordado entre el usuario y el
> orquestador. **No entra en desarrollo sin la aprobación del usuario** (sección 9).

| Campo | Valor |
|---|---|
| Historia | <ID> — enlace a `03_HISTORIAS_USUARIO.md` |
| Épica · PMV · Sprint | |
| Requisitos | RF-…, RNF-…, RN-…, RS-… |
| Rama | `<tipo>/<ID>-<descripcion>` |
| Estado | Borrador · Aprobada · En desarrollo · En auditoría · Terminada |
| Versión · fecha | 0.1 · AAAA-MM-DD |

## 1. Contexto y objetivo

Qué problema resuelve y qué cambia para la persona usuaria. Una o dos frases.

## 2. Alcance

**Incluye:** …
**Excluye:** …

## 3. Criterios de aceptación

Copia literal de los escenarios Gherkin de la historia. **No se modifican aquí**: si hay que cambiarlos,
se registra un ADR y se actualiza `03_HISTORIAS_USUARIO.md`.

```gherkin
# language: es
```

## 4. Plan técnico

- **Puertos afectados:** …
- **Adaptadores nuevos o modificados:** …
- **Cambios en el núcleo (`dominio/`):** … (justificar; el núcleo no depende de terceros)
- **Datos y configuración:** esquema, `config/umbral.yaml` (¿cambia τ? → ADR obligatorio)
- **Riesgos técnicos y cómo se mitigan:** …

## 5. Plan de pruebas

| Tipo | Qué se prueba | Archivo |
|---|---|---|
| Unitaria (TDD) | | `tests/unitarias/…` |
| Aceptación (Gherkin) | | `tests/aceptacion/<ID>.feature` |
| Salvaguarda | RN-01…RN-08 afectadas | `@salvaguarda` |
| Arquitectura | Núcleo sin dependencias externas | `tests/arquitectura/…` |
| Arnés | Particiones afectadas y métricas esperadas | `evaluacion/…` |

## 6. Tareas (en orden, cada una con su prueba)

| # | Tarea | Prueba que la guía | Estado |
|---|---|---|---|
| 1 | | | Pendiente |

## 7. Seguridad y calidad (para el auditor)

Criterios RS aplicables, datos sensibles, entradas externas, dependencias nuevas.

## 8. Definición de Terminado

- [ ] DoD-1 ejecutable de principio a fin · [ ] DoD-2 Gherkin en verde · [ ] DoD-3 trazabilidad
- [ ] **DoD-4 salvaguarda** · [ ] DoD-5 operación local · [ ] DoD-6 rendimiento (si cierra PMV)
- [ ] DoD-7 procedencia del corpus · [ ] DoD-8 versionado y reproducible · [ ] DoD-9 docs al día
- [ ] DoD-10 auditoría sin bloqueantes + aprobación humana

## 9. Aprobación y registro

| Fecha | Evento | Quién |
|---|---|---|
| | Spec aprobada | Usuario |
