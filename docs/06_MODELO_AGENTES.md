# 06 · Modelo operativo de agentes y desarrollo guiado por especificaciones

> Cómo se construye el software: quién hace qué, en qué orden, con qué controles y cómo se conserva el
> contexto entre sesiones. Aprobado por el usuario el 2026-09-24 (ADR-009, ADR-010, ADR-011, ADR-017). Las
> reglas operativas para Claude Code están en `CLAUDE.md`; este archivo explica el porqué y el detalle.
>
> Mantenido por: **archivista** · Última revisión: 2026-09-24 · Versión 1.1

---

## 1. Principios

1. **La especificación manda sobre el código.** Nada se programa sin `spec.md` aprobada; si el código y la
   especificación discrepan, se corrige uno de los dos de forma explícita, nunca se deja la discrepancia.
2. **La documentación es la memoria compartida.** Los subagentes de Claude Code trabajan en una ventana
   de contexto propia, no comparten memoria entre sí ni recuerdan invocaciones anteriores. Lo único que
   sobrevive de una sesión a otra es lo escrito en `docs/`, en el repositorio y en `CLAUDE.md`. Por eso el
   archivista es un rol, no un lujo.
3. **Una sola voz hacia el usuario.** Solo el orquestador conversa con el usuario. Los subagentes reciben
   un encargo, lo ejecutan y devuelven un informe al orquestador; no se comunican entre sí directamente.
4. **Las decisiones irreversibles las toma una persona.** Fusionar en `main`, aceptar un ADR, cambiar τ y
   dar por cumplido un hito requieren aprobación humana explícita.
5. **La salvaguarda se prueba siempre.** Las pruebas `@salvaguarda` se ejecutan en cada rama y bloquean la
   fusión si fallan (DoD-4).

---

## 2. Roles

| Rol | Modelo | Dónde vive | Responsabilidad | Nunca hace |
|---|---|---|---|---|
| **Orquestador** | Opus 5.5 (sesión principal de Claude Code) | Conversación con el usuario | Debate y planifica con el usuario; refina el encargo antes de delegar; delega; integra los informes; propone decisiones; lleva el Sprint Planning y la revisión | Fusionar sin aprobación; escribir el tablero directamente |
| **Archivista** | Sonnet 5 (`model: sonnet`) | `.claude/agents/archivista.md` | Mantiene vivos `docs/` (tablero, sprints, requerimientos, historias, ADR, specs) y `CLAUDE.md`; redacta specs a partir de lo acordado; registra cada movimiento con fecha y evidencia; comprueba la coherencia entre documentos | Programar; decidir por su cuenta; modificar criterios de aceptación sin decisión registrada |
| **Programador** | Sonnet 5 (`model: sonnet`) | `.claude/agents/programador.md` | Implementa con TDD en una rama por historia; escribe pruebas unitarias, de aceptación (Gherkin) y de arquitectura; mantiene la estructura hexagonal; abre el PR con la plantilla | Tocar `docs/` salvo docstrings y README técnicos; bajar τ; editar criterios de aceptación |
| **Auditor** | Sonnet 5 (`model: sonnet`) | `.claude/agents/auditor.md` | Revisa cada PR: salvaguarda, seguridad (RS-01…RS-08), arquitectura, calidad (SonarQube), dependencias, secretos; emite informe con severidades | Corregir el código él mismo (informa; corrige el programador) |

> Los nombres de modelo se fijan en el *frontmatter* de cada subagente con el alias (`sonnet`, `opus`)
> para no depender de un identificador de versión concreto.

### 2.1 Propiedad de archivos

| Ruta | Escribe | Lee |
|---|---|---|
| `docs/**` | archivista (por encargo del orquestador) | todos |
| `docs/specs/<ID>/spec.md` | archivista redacta · usuario aprueba | todos |
| `CLAUDE.md` del repositorio | archivista | todos |
| `src/**`, `tests/**`, `app_movil/**` | programador | todos |
| `backend/src/infrastructure/config.py` (τ) | programador, **solo** tras decisión registrada | todos |
| `docs/auditorias/<PR>.md` | auditor | todos |
| `.github/**` | programador (CI) · auditor revisa | todos |

---

## 3. Ciclo de desarrollo guiado por especificaciones

Cada historia recorre ocho pasos. Las compuertas (◆) no se saltan.

| Paso | Qué ocurre | Responsable | Salida | Compuerta |
|---|---|---|---|---|
| 1. Especificar | Se debate el alcance con el usuario; se aclaran dudas; se redacta la spec con la plantilla | Orquestador + usuario → archivista | `docs/specs/<ID>/spec.md` | ◆ **Usuario aprueba la spec** |
| 2. Planificar | Diseño técnico: puertos y adaptadores afectados, datos, riesgos, pruebas | Orquestador (+ programador si hace falta) | Sección «Plan técnico» de la spec | — |
| 3. Desglosar | Tareas pequeñas y ordenadas, cada una con su prueba | Orquestador → archivista | Sección «Tareas» de la spec; tarjeta en «En desarrollo» | — |
| 4. Implementar (TDD) | Rojo → verde → refactorizar, tarea a tarea, en la rama de la historia | Programador | Commits convencionales; PR abierto | ◆ **CI en verde** (incluye `@salvaguarda`) |
| 5. Auditar | Revisión de seguridad, calidad, arquitectura y salvaguarda; análisis de SonarQube | Auditor | `docs/auditorias/<PR>.md` | ◆ **Sin hallazgos bloqueantes** |
| 6. Corregir | El programador atiende los hallazgos; el auditor verifica | Programador ↔ auditor | Commits `fix:` sobre la misma rama | — |
| 7. Revisar y fusionar | El usuario revisa el PR y el informe | **Usuario** | Fusión por *squash* en `main` | ◆ **Aprobación humana (DoD-10)** |
| 8. Archivar | Tablero, sprint, trazabilidad, ADR y `CLAUDE.md` actualizados | Archivista | Entrada fechada en `04_SPRINTS.md` §7 | DoD-9 |

---

## 4. Protocolo de delegación

### 4.1 Encargo del orquestador a un subagente

El orquestador no delega hasta haber refinado el encargo con el usuario. Todo encargo sigue esta forma:

```markdown
## Encargo para <archivista | programador | auditor>
**Tarjeta:** HU-03 · **Rama:** feat/HU-03-consulta-lexica · **Sprint:** 2
**Objetivo:** <una frase, resultado observable>
**Lee primero:** docs/00_INDICE_MAESTRO.md · docs/specs/HU-03/spec.md · <otros>
**Criterios de aceptación:** los escenarios Gherkin de HU-03 (sin modificarlos)
**Restricciones:** RN-01…RN-10 · no tocar τ en config.py · <otras>
**Fuera de alcance:** <lo que no debe hacer>
**Entrega esperada:** <archivos, PR, informe>
**Formato de respuesta:** el del §4.2
```

### 4.2 Informe de vuelta de cualquier subagente

```markdown
## Informe · <rol> · <tarjeta> · <fecha>
**Estado:** terminado | parcial | bloqueado
**Hecho:** <lista breve>
**Evidencia:** <commits, PR, rutas, salida de pruebas>
**Pendiente o riesgos:** <lista>
**Decisiones que necesito del usuario:** <lista o «ninguna»>
**Movimientos de tablero propuestos:** <tarjeta: origen → destino>
```

El orquestador resume el informe al usuario y, si procede, encarga al archivista los movimientos.

---

## 5. El programador: TDD y estructura

### 5.1 Estructura del repositorio

La estructura vigente está en `CLAUDE.md` §6. Puntos clave: la raíz del repositorio es
`SDD_RAG_Quechua/`; `corpus/pdf/` y `referencia_poc/datos/fragmentos_v2.jsonl` están fuera de Git;
`corpus/MANIFIESTO.yaml`, `docs/`, `.claude/` y `.mcp.json` sí se versionan; el código vive en
`src/rag_quechua/{dominio,puertos,adaptadores,aplicacion,entrada}`.

### 5.2 Reglas de TDD

1. Cada tarea empieza con una prueba que falla (**rojo**), luego el mínimo código que la hace pasar
   (**verde**) y después la limpieza (**refactorizar**). Un commit por ciclo o por tarea.
2. Los escenarios Gherkin de la historia se automatizan **antes** de dar la historia por implementada.
3. El núcleo se prueba sin modelos reales: los puertos se sustituyen por dobles de prueba. Las pruebas
   con Ollama o modelos reales llevan `@lento` y se ejecutan en el cierre del sprint.
4. **Prueba de arquitectura** obligatoria: `dominio/` no importa nada fuera de la biblioteca estándar.
5. Cobertura mínima propuesta: **90 % en `dominio/`**, 70 % global. Se revisa en la retrospectiva del
   sprint 1 con datos reales.
6. Herramientas: `pytest`, `pytest-bdd` (o `behave`, ver `03_HISTORIAS_USUARIO.md` §1.3), `ruff`
   (formato y reglas), `mypy` en `dominio/` y `puertos/`; en Flutter, `flutter_test` e
   `integration_test`.

---

## 6. El auditor: qué revisa y cómo informa

### 6.1 Lista de revisión por PR

| Bloque | Comprobaciones |
|---|---|
| **Salvaguarda** | Las pruebas `@salvaguarda` existen y pasan; RN-01…RN-10 intactas; τ no aparece como literal; el generador no se invoca sin respaldo (S < τ y sin lema exacto); ninguna forma quechua fuera de los fragmentos. |
| **Seguridad** | RS-01…RS-08; entradas validadas; sin secretos; sin llamadas de red salientes; texto del corpus tratado como dato en la plantilla del generador. |
| **Arquitectura** | El núcleo no depende de adaptadores; cada dependencia entra por un puerto. |
| **Calidad** | Puerta de calidad de SonarQube; duplicación; complejidad; cobertura del código nuevo. |
| **Dependencias** | `pip-audit` sin vulnerabilidades altas; licencias compatibles. |
| **Trazabilidad** | Commits con `Refs: <ID>`; PR enlazado a la spec; criterios Gherkin cubiertos. |

### 6.2 Severidades

| Severidad | Efecto |
|---|---|
| **Bloqueante** | Impide la fusión. Toda violación de la salvaguarda es bloqueante. |
| **Mayor** | Se corrige en el mismo PR salvo excepción aprobada por el usuario y registrada. |
| **Menor** | Se registra como deuda en el backlog. |

### 6.3 SonarQube: opciones y decisión

| Criterio | SonarQube **Cloud** (plan gratuito) | SonarQube **Community Build** (local, ya instalado) |
|---|---|---|
| Código privado | Hasta **50 000 líneas** | Sin límite |
| Ramas y PR | Solo rama principal; PR analizados **si su destino es la rama principal** | Sin análisis de ramas ni de PR |
| Decoración del PR en GitHub y bloqueo por puerta de calidad | Sí | No |
| Dart / Flutter (PMV3) | Soportado en Cloud (verificar en el plan gratuito durante HT-00) | El personal de Sonar indicó que **no hay planes** de incluirlo |
| Servidor MCP oficial para Claude Code | Sí (`SONARQUBE_TOKEN` + `SONARQUBE_ORG`) | Sí (`SONARQUBE_TOKEN` de usuario + `SONARQUBE_URL`) |
| Costo | 0 | 0 |

**Decisión (usuario, 2026-09-24).** SonarQube Cloud gratuito como puerta de calidad en integración
continua, con repositorio **privado** en GitHub y **GitHub Flow** (todo PR apunta a `main`, que es lo que
el plan gratuito analiza), y el **Community Build local** como respaldo sin conexión. Cloud es además la
única opción que cubre el código Dart del PMV3.

**Cobertura de las pruebas TDD.** SonarQube no ejecuta pruebas: **importa** el informe que genera
`pytest --cov --cov-report=xml` (`sonar.python.coverage.reportPaths=coverage.xml`). Por eso el análisis en
Cloud se lanza **desde GitHub Actions**, después de las pruebas; el análisis automático de Sonar no
importa cobertura. En local, el mismo `coverage.xml` se envía con `sonar-scanner`. Los mínimos propios
(90 % en `dominio/`, 70 % global) se exigen con `--cov-fail-under` en CI, de modo que la regla no depende
de si el plan gratuito permite personalizar la puerta de calidad. En el PMV3 se añade el informe `lcov`
de `flutter test --coverage`.

**Servidores MCP.** Ya declarados en `.mcp.json`: `sonarqube` (Cloud, variables `SONARQUBE_TOKEN` y
`SONARQUBE_ORG`) y `sonarqube-local` (`SONARQUBE_TOKEN_LOCAL`, contra `http://localhost:9000`). Desde el
2026-10-01 **ya no requieren Docker**: se ejecutan con el JAR oficial (`java -jar ${SONARQUBE_MCP_JAR}`,
Java 21), con las variables de usuario `SONARQUBE_MCP_HOME` y `SONARQUBE_MCP_JAR` y en modo de solo lectura
(`SONARQUBE_READ_ONLY=true`). Proyecto local creado en el Community: clave `omarpiero_rag-quechua-wanka`. El
servidor Cloud necesita aún `SONARQUBE_ORG` y un token de SonarQube Cloud (pendiente del usuario). Claude
Code no lee `.env`: las variables deben existir en el entorno de Windows antes de abrirlo.

*Registro:* 2026-10-01, párrafo «Servidores MCP» corregido (sin Docker; JAR oficial). Fuente: encargo del
orquestador del 2026-10-01 y `.mcp.json`.

## 7. Convención de Git y GitHub

### 7.1 Flujo: GitHub Flow

- `main` protegida: solo se fusiona por PR, con CI en verde, informe de auditoría sin bloqueantes y
  aprobación humana. Fusión por *squash* para que cada historia sea un commit en `main`.
- Una rama por historia o historia técnica, corta y creada desde `main`.

### 7.2 Nombres de rama

`<tipo>/<ID>-<descripcion-corta>` en minúsculas y con guiones:

| Tipo | Uso | Ejemplo |
|---|---|---|
| `feat/` | Funcionalidad de una historia | `feat/HU-03-consulta-lexica` |
| `fix/` | Corrección | `fix/HU-01-entradas-fusionadas` |
| `test/` | Solo pruebas o arnés | `test/HT-01-arnes-evaluacion` |
| `refactor/` | Sin cambio de comportamiento | `refactor/NUC-01-depuracion` |
| `docs/` | Documentación | `docs/sprint-1-cierre` |
| `ci/` | Integración continua | `ci/HT-00-sonarqube` |
| `chore/` | Mantenimiento | `chore/actualizar-dependencias` |
| `spike/` | Espiga exploratoria (no se fusiona sin decisión) | `spike/HT-07-bge-m3` |

### 7.3 Commits: Conventional Commits

```
<tipo>(<ámbito>): <descripción en imperativo, en español, ≤ 72 caracteres>

<cuerpo opcional: qué y por qué>

Refs: HU-03
```

Tipos: `feat`, `fix`, `test`, `refactor`, `docs`, `ci`, `build`, `chore`, `perf`. Ámbitos: `dominio`,
`ingesta`, `indice`, `recuperacion`, `abstencion`, `traduccion`, `generacion`, `api`, `ui`, `evaluacion`,
`prediccion`, `movil`. Ejemplo: `feat(abstencion): leer τ desde la configuración`.
Un cambio de τ usa siempre `feat(abstencion)` o `fix(abstencion)` y enlaza el informe del arnés.

### 7.4 Etiquetas de versión por hito

| Hito | Etiqueta | Contenido |
|---|---|---|
| Hito 1 | `v0.1.0` | PMV1 escritorio validado |
| Hito 2 | `v0.2.0` | PMV2 analítica y artefactos móviles |
| Hito 3 | `v1.0.0` | PMV3 aplicación móvil sin conexión |

### 7.5 Plantilla de PR

```markdown
## <ID> · <título>
Spec: docs/specs/<ID>/spec.md
### Qué cambia
### Criterios de aceptación cubiertos
- [ ] Escenario …
### Salvaguarda
- [ ] Pruebas @salvaguarda en verde  - [ ] τ sin cambios (o ADR enlazado)
### Evidencia
Resultados del arnés (si aplica), capturas, métricas.
### DoD
- [ ] DoD-1 … - [ ] DoD-10
```

---

## 8. Conservar el contexto entre sesiones

| Mecanismo | Qué contiene | Quién lo mantiene |
|---|---|---|
| `CLAUDE.md` del repositorio | Reglas no negociables, estructura, comandos, enlaces a `docs/` y **estado actual en cinco líneas** | Archivista |
| `docs/00_INDICE_MAESTRO.md` §2 | Estado del proyecto: sprint, hito, bloqueos | Archivista |
| `docs/05_KANBAN.md` | Qué está en curso y quién lo tiene | Archivista |
| `docs/07_DECISIONES.md` | Por qué se hizo cada cosa | Archivista |
| `docs/specs/<ID>/` | Todo lo acordado de una historia | Archivista |
| `docs/auditorias/` | Hallazgos y su resolución | Auditor |

**Al abrir cada sesión**, el orquestador lee `CLAUDE.md`, el índice maestro y el tablero, y resume al
usuario dónde se quedó el trabajo. **Al cerrar cada sesión**, encarga al archivista actualizar el tablero,
el registro de §7 de `04_SPRINTS.md` y el estado de `CLAUDE.md`.

---

## 9. Lo que los agentes no pueden hacer y hará una persona

| Tarea | Por qué |
|---|---|
| Aprobar specs, ADR y fusiones | Decisiones irreversibles (principio 4). |
| Obtener consultas de docentes de EIB (HT-02) y el conjunto cultural (RD-05) | Deben proceder de personas reales; fabricarlas invalidaría la evaluación. |
| Incorporar nuevos documentos al corpus con su licencia | Responsabilidad de gobernanza (CARE). |
| Crear tokens de GitHub y SonarQube | Credenciales. |
| Pruebas en el dispositivo físico y con usuarios (HU-10, HU-11) | Requieren hardware y personas. |
| Contacto con comunidades (I-01) | Registrado como pendiente de establecer. |

---

## 10. Definición de los subagentes

Creados el 2026-09-24 en `.claude/agents/`: `archivista.md`, `programador.md` y `auditor.md`, con
`model: sonnet`. El archivista y el programador tienen la lista de herramientas restringida; el auditor
hereda todas para poder usar las herramientas MCP de SonarQube y, por instrucción, solo escribe en
`docs/auditorias/`. Cualquier cambio en esos archivos se registra en `07_DECISIONES.md`.

## 11. Servidor MCP de desarrollo (ADR-017)

FastAPI es la API del producto. Además, un adaptador de entrada MCP (SDK oficial de MCP para Python,
transporte `stdio`) expone los casos de uso como herramientas **de solo lectura** para que el programador
y el auditor prueben el sistema real desde Claude Code: `estado_indice`, `buscar_fragmentos`,
`ejecutar_arnes`, `consultar`, `verificar_salvaguarda`. Se construye en HT-08. Advertencia: los
fragmentos que devuelven viajan a la API de Claude; por eso es solo de desarrollo y nunca forma parte del
producto (RS-08).

## Fuentes consultadas para §6.3 y §11 (2026-09-24)

- Sonar, *Subscription plans · SonarQube Cloud*: https://docs.sonarsource.com/sonarqube-cloud/administering-sonarcloud/managing-subscription/subscription-plans
- SonarSource, *sonarqube-mcp-server* (repositorio oficial): https://github.com/SonarSource/sonarqube-mcp-server
- Sonar, *Claude Code · SonarQube MCP Server*: https://docs.sonarsource.com/sonarqube-mcp-server/setup/quickstart-guides/claude-code
- Sonar Community, *Dart/Flutter support availability in SonarQube Community Edition*: https://community.sonarsource.com/t/dart-flutter-support-availability-in-sonarqube-community-edition/130038
- Sonar, *Dart · SonarQube Cloud*: https://docs.sonarsource.com/sonarqube-cloud/analyzing-source-code/languages/dart
- FastMCP, *FastAPI integration*: https://gofastmcp.com/integrations/fastapi
- tadata-org, *fastapi_mcp*: https://github.com/tadata-org/fastapi_mcp
