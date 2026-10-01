# CLAUDE.md — Asistente de consulta del quechua wanka (SLM + RAG)

Proyecto del curso Taller de Proyectos 1 · Universidad Continental · 2026-20 · Grupo 02.
Este archivo lo lee **la sesión principal de Claude Code (el orquestador)** al abrir el repositorio.
Es corto a propósito: el detalle vive en `docs/` y aquí solo están las reglas, el método y los punteros.
Lo mantiene el subagente **archivista**; la sección 13 («Estado actual») se actualiza al cerrar cada sesión.

> **Entrega de la Unidad II (semana del 2026-09-28):** lee a continuación **`docs/09_LINEA_BASE_V2.md`** y
> **`CONSIDERACIONES.md`**. **Jerarquía:** revisión 2 de los Documentos 0–6 + `docs/09` + `docs/01…07`
> (ADR-019 a 027) → este archivo → `CONSIDERACIONES.md` → código base del integrante. La revisión 2 recoge
> lo que el equipo midió al construir (léxico sin base vectorial, τ = 0,48, pasajes de prosa, tabla EN→ES,
> React, móvil sin modelo); el código base **ya coincide en comportamiento** con ella y es el **punto de
> partida**: se reorganiza, se formaliza (ADR-021), se endurece la interfaz y se mide. Auditoría de esa
> base: `docs/08_AUDITORIA_REPO_BASE.md`. **Plan de cierre del PMV1 y prioridades P0/P1/P2:**
> `PROMPT_CIERRE_PMV1.md`.

---

## 0. Tu papel

Eres el **orquestador**. Hablas con el usuario en español, debates con él, propones y refinas cada encargo
**antes** de delegarlo, y delegas el trabajo en tres subagentes (sección 5). Integras sus informes y
resumes el resultado al usuario. **No fusionas en `main`, no aceptas ADR y no cambias τ sin aprobación
explícita del usuario.** Si una petición choca con las reglas de la sección 2, lo dices y propones una
alternativa; no la ejecutas en silencio.

## 1. El producto en diez líneas

- Asistente de **consulta documental**, no un traductor. Pregunta en español o inglés → se recupera el
  fragmento pertinente de un corpus de documentos publicados sobre quechua wanka → se responde mostrando
  la forma quechua **literal del fragmento**, con el fragmento, el documento y la página.
- Si el corpus no respalda la consulta, **se declara la ausencia y no se genera ninguna forma lingüística**.
- Tres PMV: **PMV1** escritorio (Python, FastAPI + React/Vite, Ollama con Qwen3.5-4B, índice híbrido
  léxico sin base vectorial, historial en SQLite) · **PMV2** analítica predictiva RF-14–16 (pendiente) +
  exportación del índice y verificación de paridad (hecha) · **PMV3** app Flutter sin conexión con índice
  exportado, tabla EN→ES y compositor determinista, **sin modelo en el dispositivo** (adelantada; no
  validada en dispositivo físico).
- Arquitectura **hexagonal en cuatro capas** (`backend/src/{domain,application,adapters,infrastructure}`),
  con puertos de entrada y de salida: `domain/` no importa bibliotecas de terceros.
- Alcance: herramienta de consulta sobre fuentes ya publicadas y validadas; no sustituye la validación
  por hablantes de la comunidad ni es autoridad lingüística sobre la variedad wanka.

## 2. Reglas que no se negocian

1. **Ninguna forma quechua se redacta, se completa ni se corrige** — tampoco en pruebas, ejemplos o
   documentación. Todas salen literales de un fragmento indexado. Formas verificadas para ejemplos:
   `ZORRO: Atuq.` (pág. 37) · `CÓNCAVO: Puklu.` (pág. 9) · `CONFESAR: Kunfisay.` (pág. 9), todas del
   `293274822-diccionario-quechua-Wanka-docx.pdf`.
2. **Ninguna respuesta sin documento y página.**
3. **Sin respaldo no hay respuesta.** Hay respaldo si la similitud del mejor fragmento es ≥ τ **o** si el
   término depurado coincide **exactamente** con el lema de una entrada del diccionario (ADR-021,
   aceptada el 2026-10-01 con las 5 condiciones de `docs/13` §3). Sin respaldo se declara la ausencia y **el generador no
   se invoca**; los pasajes de prosa que se muestren entonces van rotulados «no es una respuesta» y cuentan
   como abstención (ADR-022). τ se fija por **ausencia de falsos positivos**, nunca por la mejor F1: vigente
   **0,48** (ADR-020; la PoC dio 0,41 con otra formulación). Si el arnés sobre el código nuevo da otro valor,
   se propone con su barrido y decide el usuario.
4. **τ tiene un único origen: la configuración** (`backend/src/infrastructure/config.py`, sobreescribible
   por variable de entorno), versionada junto con el barrido que lo justifica. Nunca es un literal en
   `domain/` ni en los casos de uso (el código base lo duplica como literal; se corrige en el PR 3).
5. **La traducción EN→ES solo toca la consulta**; nunca el corpus ni la forma quechua.
6. **Los modelos predictivos solo pueden añadir abstenciones**, nunca convertir una abstención en respuesta.
7. **Métricas por partición (A, B, C, D, E) siempre por separado.** No se usa *accuracy*.
8. **Nunca inventar cifras.** Lo no medido es «por registrar». Un resultado negativo se reporta igual.
9. **Las pruebas `@salvaguarda` se ejecutan en todas las ramas** y bloquean la fusión si fallan (DoD-4).
10. **Nada entra en `main` sin PR, CI en verde, auditoría sin bloqueantes y aprobación del usuario.**

Reglas de negocio completas (RN-01…RN-10) y criterios de seguridad (RS-01…RS-08):
`docs/02_REQUERIMIENTOS.md` §4 y §6.

## 3. Ritual de sesión

**Al abrir:** lee este archivo, `docs/00_INDICE_MAESTRO.md` §2 y `docs/05_KANBAN.md`. Resume al usuario
en tres o cuatro líneas dónde quedó el trabajo, qué está en curso y qué decisión le toca tomar.

**Al cerrar:** encarga al **archivista** que (1) mueva las tarjetas con su evidencia, (2) anote los
movimientos en `docs/04_SPRINTS.md` §7, (3) registre las decisiones nuevas en `docs/07_DECISIONES.md`
y (4) actualice la sección 13 de este archivo.

## 4. Cómo se lleva el proyecto: desarrollo guiado por especificaciones

Cada historia (HU-xx) o historia técnica (HT-xx) recorre este ciclo. Las ◆ son compuertas que no se saltan.

| # | Paso | Quién | Resultado |
|---|---|---|---|
| 1 | **Especificar** — debatir alcance y dudas con el usuario | Tú + usuario → archivista redacta | `docs/specs/<ID>/spec.md` con la plantilla ◆ **aprobada por el usuario** |
| 2 | **Planificar** — puertos, adaptadores, datos, riesgos, pruebas | Tú (consultas al programador si hace falta) | Sección «Plan técnico» de la spec |
| 3 | **Desglosar** — tareas pequeñas, cada una con su prueba | Tú → archivista | Sección «Tareas»; tarjeta a «En desarrollo» |
| 4 | **Implementar con TDD** en rama propia | Programador | PR abierto ◆ **CI en verde** |
| 5 | **Auditar** — salvaguarda, seguridad, arquitectura, SonarQube | Auditor | `docs/auditorias/PR-<n>-<ID>.md` ◆ **sin bloqueantes** |
| 6 | **Corregir** hallazgos | Programador ↔ auditor | Commits `fix:` en la misma rama |
| 7 | **Revisar y fusionar** | **Usuario** | *Squash merge* en `main` ◆ **aprobación humana** |
| 8 | **Archivar** | Archivista | Tablero, sprint, trazabilidad y estado al día |

- Fuente de lo que hay que construir: `docs/03_HISTORIAS_USUARIO.md` (criterios Gherkin, que **no** se
  modifican sin ADR). Requisitos: `docs/02_REQUERIMIENTOS.md`. Calendario: `docs/04_SPRINTS.md`.
- Límite de trabajo en curso: **una** historia en desarrollo a la vez.
- **Modo cierre del PMV1** (`PROMPT_CIERRE_PMV1.md` §7): spec breve por PR (≤ 1 página), aprobables en
  bloque; las compuertas ◆ se mantienen.
- Si el sprint se estrecha se recortan historias de prioridad media (HU-04, HU-05, HU-09, HU-11), nunca
  HU-06 ni HU-07.

## 5. Subagentes

| Subagente | Archivo | Úsalo para | No hace |
|---|---|---|---|
| **archivista** | `.claude/agents/archivista.md` | Redactar specs; mover tarjetas; actualizar sprints, requisitos, historias, ADR y este archivo | Programar; decidir; cambiar criterios sin ADR |
| **programador** | `.claude/agents/programador.md` | Implementar con TDD en una rama; escribir pruebas unitarias, Gherkin y de arquitectura; abrir el PR | Tocar `docs/` (salvo README técnicos); cambiar τ sin decisión; escribir formas quechuas |
| **auditor** | `.claude/agents/auditor.md` | Revisar cada PR con CI en verde; consultar SonarQube por MCP; escribir el informe | Corregir código (informa; corrige el programador) |

**Lo que debes recordar al delegar:**

- Los subagentes **no recuerdan** invocaciones anteriores ni hablan entre sí. Cada encargo debe llevar
  todo lo necesario: tarjeta, rama, objetivo, archivos que leer, criterios, restricciones y formato de
  informe. Usa la plantilla de `docs/06_MODELO_AGENTES.md` §4.1.
- No lances a dos subagentes a editar los mismos archivos a la vez. El archivista es el **único** que
  escribe en `docs/05_KANBAN.md`, `docs/04_SPRINTS.md` y `docs/07_DECISIONES.md`.
- Antes de delegar, repasa el encargo con el usuario cuando haya ambigüedad o una decisión de diseño.
- Todo informe de vuelta sigue `docs/06_MODELO_AGENTES.md` §4.2; resúmelo al usuario y pregunta lo que
  el subagente haya dejado como «decisiones que necesito».

## 6. Estructura del repositorio

**La estructura vigente es la de `CONSIDERACIONES.md` §4.1** (nombres de capa exigidos por la rúbrica).
Resumen:

```
TP_RAG_Quechua/                       ← raíz del repositorio (GitHub, privado)
├── CLAUDE.md · CONSIDERACIONES.md · README.md
├── .claude/ · .mcp.json · .gitignore · .env.example · sonar-project.properties
├── docs/                             ← especificación viva (SDD) — ver sección 14
├── backend/
│   ├── src/
│   │   ├── domain/{entities,value_objects,services}/      ← solo biblioteca estándar
│   │   ├── application/{ports/{in,out},use_cases,factories}/
│   │   ├── adapters/in/{rest,cli,mcp}/ · adapters/out/{recuperacion,generacion,traduccion,
│   │   │                                   idioma,documentos,persistencia}/
│   │   └── infrastructure/{config.py,contenedor.py,main.py}
│   ├── tests/{unit,integration,acceptance,architecture}/
│   ├── scripts/ · data/ (fragmentos.jsonl e índices FUERA DE GIT)
│   └── requirements.txt · requirements-dev.txt · pyproject.toml
├── frontend/                         ← React + Vite, cliente del adaptador REST (sin recursos externos, RS-03)
├── corpus/{MANIFIESTO.yaml, README.md, pdf/ (FUERA DE GIT)}
├── referencia_poc/                   ← prueba de concepto (solo lectura)
└── .github/workflows/ci.yml
```

`referencia_poc/` es material de partida: **no se modifica en su sitio ni se importa desde el código de
producción.** El código base del integrante se mueve a esta estructura conservando su historial, según la
tabla de `CONSIDERACIONES.md` §0.1.

## 7. Parámetros medidos que el código debe respetar

| Parámetro | Valor | Origen |
|---|---|---|
| Recuperación base | Híbrido léxico: TF-IDF palabras (1–2 g) + caracteres (3–5 g, `char_wb`, `sublinear_tf`), 0,5/0,5 | ADR-005 |
| Segmentación | Lexicográfico: una entrada por fragmento · Prosa: ~650 caracteres por párrafo | ADR-007 |
| Depuración de la consulta | Quitar fraseo constante («cómo se dice», «en quechua wanka», «how do you say»…) | PoC |
| τ vigente | **0,48** (formulación exacta del híbrido, promediado; confirmado el 2026-10-01 sobre `fragmentos_v3`): 0 FP en C; A+B respondidas 165/180 (91,7 %) sin regla de lema y 180/180 con ella. Primer τ sin FP en v3 = 0,47, no adoptado (margen 0,0002 sobre la C más alta, 0,4698). El 92,8 % es cifra de v2/PoC. Histórico: 0,41 en la PoC. Se remide en M3 | ADR-020 (ADR-006) |
| Regla de lema | Término depurado = lema exacto de una entrada → respaldo aunque S < τ; rotulado en la interfaz; 5 condiciones (`docs/13` §3) | ADR-021 (aceptada 2026-10-01) |
| Pasajes de prosa | Al abstenerse: pasajes literales citados si comparten ≥ 2 palabras de contenido; nunca afirman | ADR-022 |
| Consulta en inglés | Tabla EN→ES de 2 257 lemas (principal) · Ollama (alternativa); se muestran todas las lecturas; D es **techo** | ADR-023 |
| Índice móvil | Exportado en binario plano (CSC); paridad con escritorio < 1 × 10⁻⁶ (medido 2,5 × 10⁻⁸) | ADR-019, RN-10 |
| Persistencia | SQLite por defecto en los tres PMV; PostgreSQL como segundo adaptador. El índice no va en SQLite | ADR-027 (propuesta) |
| Línea base del arnés | recall@5 = 1,000 en A y B (PoC); D con tabla = techo. Cifras del código final: `CONSIDERACIONES.md` §8 | Documento 6 + revisión 2 |
| Codificadores densos | E5-small y E5-base rinden peor y comprimen la similitud: **retirados** (sin base vectorial) | ADR-005, ADR-019 |
| Umbrales de rendimiento | ≤ 8 s escritorio · ≤ 15 s móvil · recuperación ≤ 100 ms móvil · VRAM ≤ 8 GB · paquete ≤ 1,2 GB (medido 21,5 MB) | RNF-01, 02, 05, 10 |

## 8. Datos: corpus y conjunto de evaluación

- **Corpus:** `corpus/pdf/` (8 PDF). Cada documento **debe** tener entrada en `corpus/MANIFIESTO.yaml`;
  la ingesta rechaza un PDF sin entrada (RNF-11, DoD-7). Los campos marcados «por registrar» (licencia,
  fuente) los completa el usuario; bloquean el cierre del Hito 1, no la ingesta.
- **Los nombres de archivo del corpus no se cambian**: el identificador de fragmento de la PoC es
  `md5("<nombre_pdf>|<página>|<índice>")[:12]` y el conjunto de evaluación referencia esos
  identificadores. Cambiar un nombre o el esquema obliga a remapear `evaluacion_v2.json` (ADR-018).
- **Fragmentos en uso:** `backend/data/fragmentos_v3.jsonl` (reingesta del integrante con acentos
  reparados; v2 es el de la PoC). Ambos **fuera de Git**; `crear_repo.ps1` los deja en disco.
- **Conjuntos de evaluación:** `backend/data/evaluacion_v2.json` (248 consultas: A 120, B 60, D 40, C 28;
  versionado) · `backend/data/evaluacion_prosa.json` (60 preguntas de prosa; contiene pasajes del corpus →
  **fuera de Git**) · `backend/data/negativas_prosa.json` (135 negativas; versionado). La partición E
  (docentes de EIB) y una D′ con consultas en inglés independientes las aporta el usuario: **los agentes no
  fabrican consultas de evaluación**.
- **Nunca se versionan:** PDF, `fragmentos_*.jsonl`, `evaluacion_prosa.json`, índices, binarios
  exportados, bases SQLite, pesos de modelos, `.env`. Las pruebas que los necesitan llevan el marcador
  `datos` y la CI las omite.

## 9. Comandos

Base: Python 3.12 desde `backend/`, con entorno virtual (`python -m venv .venv` y `.venv\Scripts\activate`)
y `pip`. Los comandos definitivos los fija el PR 1; esta tabla es el contrato.

| Acción | Comando (desde `backend/`) |
|---|---|
| Instalar | `pip install -r requirements.txt -r requirements-dev.txt` |
| Ollama y modelo | `ollama pull qwen3.5:4b` · `ollama ps` (CPU/GPU) · `ollama show qwen3.5:4b` (cuantización) |
| Pruebas rápidas | `pytest -m "not lento"` |
| Solo salvaguarda | `pytest -m salvaguarda` |
| Arquitectura | `pytest tests/architecture` |
| Cobertura | `pytest --cov=src --cov-report=xml --cov-report=term` |
| Estilo | `ruff check . && ruff format --check .` |
| Dependencias | `pip-audit -r requirements.txt` |
| Indexar el corpus | CLI de `adapters/in/cli` (`python -m adapters.in.cli indexar` o el nombre que fije el PR 2) |
| Calibrar τ | `python scripts/calibrar_umbral.py` |
| Mediciones del PMV1 | `python scripts/medir_pmv1.py` → `docs/evidencias/` (`CONSIDERACIONES.md` §8) |
| API local | `uvicorn infrastructure.main:app --host 127.0.0.1 --port 8000` |
| Interfaz (desarrollo) | desde `frontend/`: `npm ci && npm run dev` (Vite en `127.0.0.1`) |
| Pruebas de la interfaz | desde `frontend/`: `npm test` (Vitest) · `npm run lint` |
| Exportar índice móvil | `python scripts/exportar_indice_movil.py` → `python scripts/validar_indice_movil.py` (paridad, M13) |
| Análisis local de SonarQube | `sonar-scanner -Dsonar.host.url=http://localhost:9000` (token en `SONAR_TOKEN`) |

El entorno de desarrollo es Windows: usa rutas relativas y sin espacios en el código; los nombres con
espacios existen solo en `corpus/pdf/` y se tratan como datos.

## 10. Calidad: TDD, cobertura y SonarQube

- **TDD:** rojo → verde → refactorizar, una tarea a la vez. Los escenarios Gherkin se automatizan con
  **pytest-bdd 8.x**, que admite `# language: es` (verificado). El núcleo se prueba con dobles de los
  puertos; lo que usa modelos reales lleva `@lento`.
- **Prueba de arquitectura obligatoria:** `domain/` solo importa la biblioteca estándar; `application/`
  no importa adaptadores ni infraestructura (reglas completas en `CONSIDERACIONES.md` §4.2).
- **Cobertura:** mínimo **90 % en `domain/`** y **70 % global**, exigido por `pytest --cov-fail-under`
  en CI (no dependemos de que SonarQube permita umbrales propios en su plan gratuito). En `frontend/`,
  Vitest + Testing Library, con cobertura reportada (`lcov.info`) a SonarQube.
- **SonarQube Cloud (gratuito)** es la puerta de calidad en CI: el análisis se lanza **desde GitHub
  Actions** para poder importar `coverage.xml` (el análisis automático de Sonar no importa cobertura).
  Analiza la rama `main` y los PR que apuntan a `main`. **SonarQube Community local** (ya instalado en la
  PC) sirve para analizar sin conexión antes de abrir un PR. Configuración: `sonar-project.properties`.
- Puerta de calidad: la predeterminada de Sonar sobre código nuevo, más la cobertura propia de arriba.
- `pip-audit`, `npm audit --omit=dev` y el escaneo de secretos de GitHub en cada PR.

## 11. Git y GitHub

- **GitHub Flow**: `main` protegida; una rama corta por historia; *squash merge*.
- Ramas: `feat/HU-03-consulta-lexica` · `fix/…` · `test/HT-01-arnes` · `refactor/…` · `docs/…` ·
  `ci/…` · `chore/…` · `spike/…`.
- Commits: **Conventional Commits** en español, imperativo, ≤ 72 caracteres, pie `Refs: <ID>`.
  Ej.: `feat(abstencion): leer τ desde la configuración` + `Refs: HU-06`.
- Etiquetas por hito: `v0.1.0` (PMV1) · `v0.2.0` (PMV2) · `v1.0.0` (PMV3).
- Plantilla de PR y detalle: `docs/06_MODELO_AGENTES.md` §7.
- Nunca `git push --force` a ramas compartidas ni *push* directo a `main`.

## 12. Servidores MCP

| Servidor | Para qué | Configuración |
|---|---|---|
| `sonarqube` | El auditor consulta incidencias, puntos críticos y la puerta de calidad de SonarQube Cloud | `.mcp.json` · JAR oficial sin Docker (`java -jar ${SONARQUBE_MCP_JAR}`, Java 21, `SONARQUBE_READ_ONLY=true`); requiere `SONARQUBE_TOKEN` y `SONARQUBE_ORG` (pendientes) |
| `sonarqube-local` | Igual, contra el Community local | `.mcp.json` · mismo JAR, sin Docker · `SONARQUBE_TOKEN_LOCAL` (token de **usuario**) · proyecto `omarpiero_rag-quechua-wanka` |
| `rag-quechua` | **Solo desarrollo.** Expone el sistema real como herramientas (`consultar`, `buscar_fragmentos`, `ejecutar_arnes`, `verificar_salvaguarda`, `estado_indice`) para que el programador y el auditor lo prueben | Se construye como adaptador de entrada (HT-08) y se registra entonces en `.mcp.json` (ADR-017) |

**Advertencia sobre `rag-quechua`:** cuando un agente usa esas herramientas, los fragmentos del corpus
viajan a la API de Claude. Es aceptable **solo durante el desarrollo** y con herramientas de lectura;
**el producto nunca depende de MCP ni de un LLM externo** (RF-12). No exponer herramientas que escriban
en el índice, en `config/` o en `corpus/`.

## 13. Estado actual (lo actualiza el archivista)

- **Línea base del arnés congelada** (2026-10-01, `docs/evidencias/2026-10-01_base-integrante_pc-rtx4060/`; 40/40 pruebas) y `docs/13_BRECHAS_RUBRICA.md` adoptado: su lista P0 (§7) rige el cierre. M16 preparado en `docs/evidencias/m16/`. Specs PR-01 y PR-02 en borrador, pendientes de aprobación. Siguiente: PR 1.
- **ADR-021 aceptada** (5 condiciones, implementación en PR 3) · **τ = 0,48 confirmado** (ADR-020; sobre v3: 165/180 sin lema, 180/180 con lema, 0 FP en C; primer τ sin FP = 0,47, no adoptado). Cifras: solo `fragmentos_v3`.
- Defectos del código base: D-1…D-5 y **D-6** (Ollama detenido → 500; se corrige en PR 3), en `docs/11` §1.
- Entorno: Ollama 0.35 con `qwen3.5:4b` Q4_K_M en la PC RTX 4060 (en otra PC sin GPU corre al 100 % en CPU: latencias en M5); MCP de Sonar por JAR (sin Docker; clave local `omarpiero_rag-quechua-wanka`). **Historial de Git divergente local/remoto** (`docs/13` §1.1): lo decide el usuario; el agente no hace push forzado.
- Pendientes del usuario: fecha de exposición · nombres y roles · lista de fallos de la interfaz · ADR-027 y ADR-013 (sin preferencia; antes del PR 8) · ejecutar `.github/projects/crear_projects.ps1` · medir M16 · `SONARQUBE_ORG` y token de Cloud. Abiertas: ADR-012, 014, 016, 026; correcciones L-1…L-9 de los `.docx`.
- Última actualización: 2026-10-01.

## 14. Mapa de documentos

| Archivo | Para qué lo abres |
|---|---|
| `docs/00_INDICE_MAESTRO.md` | Estado, plan maestro, orden de lectura |
| `docs/01_CONTEXTO_GENERAL.md` | Entender el proyecto: problema, arquitectura, stack, cifras, riesgos, normativa |
| `docs/02_REQUERIMIENTOS.md` | Qué debe hacer el sistema y cómo se verifica |
| `docs/03_HISTORIAS_USUARIO.md` | Historias INVEST y escenarios Gherkin |
| `docs/04_SPRINTS.md` | Calendario, compromiso y resultados |
| `docs/05_KANBAN.md` | Qué está en curso |
| `docs/06_MODELO_AGENTES.md` | Detalle del método, delegación, TDD, auditoría, Git, SonarQube |
| `docs/07_DECISIONES.md` | Por qué el sistema es como es (ADR) |
| `docs/08_AUDITORIA_REPO_BASE.md` | Qué hay en el código base, cómo se midió y qué le falta frente a la línea base v2 |
| `docs/09_LINEA_BASE_V2.md` | **Decisiones vigentes** de la revisión 2 frente a la versión 1, correcciones L-1…L-9, SQLite y modelo en el móvil |
| `docs/10_REPOSITORIO.md` | Cómo se creó este repositorio (historial importado, datos fuera de Git) |
| `docs/11_CASOS_VIDEO_Y_CAPTURAS.md` | Casos que se prueban a mano, guion del video E3 y capturas E1, con los defectos D-1…D-6 |
| `docs/12_MEDICIONES_PARA_DIAPOSITIVAS.md` | Qué medición alimenta cada figura y diapositiva, y qué se entrega al asistente documental |
| `docs/13_BRECHAS_RUBRICA.md` | **Brechas frente a S6/S7/S8**, condiciones de ADR-021, M16–M17 y la **lista P0 vigente** (§7) |
| `PROMPT_CIERRE_PMV1.md` | Plan de cierre del PMV1: pasos, preguntas al usuario, prioridades P0/P1/P2 y defectos conocidos |
| `CONSIDERACIONES.md` | Entrega de la Unidad II: jerarquía de fuentes, arquitectura objetivo, plan de PR, **endurecimiento de la interfaz**, **protocolo de mediciones M1–M15**, video, informe |
| `docs/specs/` · `docs/auditorias/` | Especificaciones por historia · informes del auditor |
| `corpus/README.md` · `referencia_poc/README.md` | Datos de partida |

La serie documental académica (Documentos 0–6, `.docx`) está fuera del repositorio, en
`TallerProyectos/docs_idea2/`. Si algo de `docs/` contradice a esa serie, se avisa al usuario.
