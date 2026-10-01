# CONSIDERACIONES.md — Entrega de la Unidad II (PMV1) · Taller de Proyectos 1

> **Léelo después de `CLAUDE.md` y de `docs/09_LINEA_BASE_V2.md`, y antes de tocar código.** Este archivo
> traduce a tareas los cuatro instrumentos de evaluación del docente (consigna S6, lista de cotejo S7,
> rúbrica S8 y trazabilidad S6) **dentro de la especificación vigente**. No la sustituye: si algo de aquí
> contradice a la revisión 2 de los Documentos 0–6, manda la especificación y se avisa al usuario.
>
> Versión 3 (2026-09-24). La especificación vigente es la **revisión 2** de los Documentos 0–6, corregida
> por el equipo tras medir el sistema y adoptada como línea base (`docs/09_LINEA_BASE_V2.md`). Con ella,
> el código base del integrante **ya coincide en comportamiento** con la especificación; lo que falta es
> la forma que exige la rúbrica, formalizar dos reglas, endurecer la interfaz y medir.

---

## 0. Jerarquía de fuentes y punto de partida

| Prioridad | Fuente | Qué decide |
|---|---|---|
| 1 | **Revisión 2 de los Documentos 0–6** + `docs/09_LINEA_BASE_V2.md` + `docs/01…07` (ADR-019 a 027) | Qué se construye |
| 2 | `CLAUDE.md` | Cómo se trabaja |
| 3 | Este archivo | Cómo se cumple la evaluación de la Unidad II |
| 4 | Código base del integrante (`DalgomXD-byte/asistente-quechua-wanka`) | **Punto de partida**: su comportamiento coincide con la revisión 2; se reorganiza, se completa y se mide |

**Regla:** cualquier comportamiento que el código tenga y la revisión 2 no documente (hoy: la coincidencia
de lema bajo τ) se **formaliza con ADR** antes de presentarlo; no se oculta ni se elimina en silencio.

### 0.1 Qué se hace con cada pieza del código base

| Pieza | Estado frente a la revisión 2 | Acción |
|---|---|---|
| Recuperación híbrida léxica + depuración | Coincide (ADR-005, 019) | Mover a `adapters/out/recuperacion` |
| τ = 0,48 | Coincide (ADR-020) | **Un solo origen**: configuración (hoy está duplicado como literal) |
| Coincidencia exacta de lema bajo τ | **No documentada** en RF-08 | ADR-021: la interfaz la rotula «respaldo: entrada exacta del diccionario»; prueba `@salvaguarda` con 0 FP en C. Decide el usuario |
| Pasajes de prosa al abstenerse | Coincide (ADR-022) | Rotular «no es una respuesta»; contarlos como abstención |
| Tabla EN→ES | Coincide (ADR-023) | `TraductorTabla` como estrategia principal y `OllamaTraductor` como alternativa (Strategy); D se declara techo; revisar errores conocidos |
| Sin OCR + reparador de acentos | Coincide (ADR-024) | Verificar la cifra del 70,6 % (M1) |
| React + Vite | Coincide (ADR-025), pero es un **prototipo** | Endurecer (PR 7, lista del §5.1) |
| PostgreSQL / SQLite | Compatible; ADR-027 propone SQLite por defecto | SQLite por defecto; PostgreSQL como segundo adaptador |
| Qwen3.5-4B con instrucción restrictiva | Coincide | Añadir `VerificadorFormaLiteral` (la salvaguarda no puede depender solo del *prompt*) |
| Entradas lexicográficas truncadas («SOL: … (época de») | Defecto | Corregir la segmentación y añadir prueba de regresión |
| Estructura sin `src/` y sin puertos de entrada | No cumple la rúbrica E2 | §4 |
| Un solo autor en los commits | No cumple la rúbrica E2 | §7 |

Mediciones de la auditoría del código base: `docs/08_AUDITORIA_REPO_BASE.md`. **Esas cifras son del código
base**; las del informe y la exposición salen del §8 sobre el código final.

---

## 1. Situación de partida

| Elemento | Estado |
|---|---|
| Repositorio entregable | `github.com/omarpiero/TP_RAG_Quechua` — vacío. Aquí va todo. |
| Especificación | Documentos 0–6 · `docs/00…07` · `corpus/MANIFIESTO.yaml` · `referencia_poc/` |
| Código base | Repositorio del integrante: materia prima (§0) |
| Plazo | Exposición y entrega en la **semana del 2026-09-28** (fecha exacta: confirmar con el usuario). El PMV1 se cierra en esa semana |
| Hardware verificado | PC del proyecto: RTX 4060 8 GB. **PC de la universidad: sin GPU dedicada**; `ollama ps` mostró `qwen3.5:4b · 3,1 GB · 100% CPU` y el sistema respondió. Latencia en CPU **por medir** (M5). Móvil de prueba del equipo: POCO F8 Pro |

---

## 2. Qué se evalúa y cuánto vale

### 2.1 Entregables obligatorios (Consigna S6)

1. **Informe técnico documental (PDF)** que sustenta C1–C6 y el diseño. Carátula con título, integrantes
   **con sus roles**, enlace al repositorio y enlace al video.
2. **Repositorio GitHub** con el código en capas hexagonales y **commits del equipo**.
3. **Video demostrativo** del PMV1 de extremo a extremo con IA.

### 2.2 Lista de cotejo (S7) — 20 puntos

| Parte | Criterio | Pts | Qué debe verse |
|---|---|---|---|
| 1 | C1 Análisis del problema | 1,5 | KPIs, árbol de causas-efectos, matriz de restricciones, antecedentes indexados |
| 1 | C2 Conocimientos de ingeniería | 1,5 | RF (≥ 3 de IA/predicción) y RNF, fundamento matemático/estadístico, matriz tecnológica ponderada |
| 1 | C3 Ingeniero y sociedad | 1,0 | Stakeholders, impactos social/económico/ambiental/legal (LPDP), dilemas éticos y sesgos de la IA |
| 1 | C4 Gestión | 1,5 | *Tailoring* ágil, backlog en épicas/historias con Given/When/Then, roadmap de 3 PMV |
| 1 | C5 Herramientas | 1,5 | Ecosistema modelado (UML/BPMN, Git, Python, **SonarQube**), limitaciones y riesgos explícitos |
| 1 | **C6 PoC + arquitectura** | **3,0** | PoC (hipótesis, F1, latencia, Go/No-Go) + **UML de componentes y despliegue en 4 capas**, puertos y **patrones Repository, Factory, DI, Adapter** (y Strategy según S6) |
| 2 | E1 Capturas | 3,0 | Interfaz ejecutando los flujos del PMV1 con IA, trazables a historias |
| 2 | **E2 Código en GitHub** | **4,0** | `src/domain`, `src/application`, `src/adapters`, `src/infrastructure`; dominio sin *frameworks*; **interfaces de puertos de entrada** y de salida; DI; servicio de IA; sin credenciales; **commits constantes de los integrantes** |
| 2 | E3 Video | 3,0 | Flujo real *Usuario → Controller (Adapter IN) → Input Port → Use Case → Módulo IA → Output Port / Adapter OUT → Persistencia / Respuesta*, con validaciones y sustentación de patrones |

### 2.3 Exposición (Rúbrica S8) — 7 min + 3 min de preguntas, 5 integrantes

| Criterio | Pts | Nota |
|---|---|---|
| 1. Introducción: antecedentes, problema con KPIs y árbol, solución, objetivos medibles | 3,0 | Diapositivas esquemáticas, sin párrafos |
| 2. Trazabilidad C1 → C6 en un **esquema/matriz integradora** | 3,0 | §10.3 |
| 3. Arquitectura (diagrama de **paquetes** o despliegue UML), capturas de la estructura en GitHub, capturas de pruebas, **tabla consolidada de resultados** (cobertura, latencia, F1, criterios aceptados) | **6,0** | El de más peso. La tabla sale de las mediciones del §8 |
| 4. Video de **1,5 a 2 min** del flujo continuo | 4,0 | Sin cortes ni simulaciones estáticas |
| 5. Desempeño individual por rol | 4,0 | Cada integrante defiende **su** parte |

Roles: **PM / Scrum Master · Architect & System Designer · Lead Backend & AI Engineer · Lead Frontend &
Integration Engineer · QA & DevOps / Test Automation**.

---

## 3. Reglas que no se negocian (además de las de `CLAUDE.md` §2)

1. **La especificación vigente manda** (§0): la revisión 2. Todo comportamiento del código que ella no documente se formaliza con ADR antes de presentarlo.
2. **No inventar cifras.** Toda cifra del informe, las diapositivas, el README o GitHub Projects sale de una
   ejecución registrada del §8 (comando, fecha, *commit*, máquina). Lo no medido se escribe «por medir».
3. **No suplantar autoría.** El agente **nunca** crea commits con el nombre o correo de otro integrante ni
   reescribe historial para simularlo. Cada integrante hace sus commits desde su cuenta. El trabajo en
   pareja real puede declararse con `Co-authored-by:`; nunca como relleno.
4. **No marcar como hecho lo que no lo está.** En GitHub Projects el PMV1 queda al 100 % solo si cada
   historia cumple su DoD; PMV2 y PMV3 figuran como pendientes aunque exista trabajo exploratorio (la app
   móvil del integrante es una espiga, no el PMV3).
5. **Ninguna forma quechua se redacta, completa o corrige**, y ahora además **se verifica en código**
   (`VerificadorFormaLiteral`), no solo en la instrucción al modelo.
6. **τ se decide por 0 FP con el arnés**, sobre el código final (vigente 0,48, ADR-020). La única vía que responde bajo τ es la coincidencia exacta de lema, y solo si ADR-021 se acepta.
7. **Arquitectura al pie de la letra** (§4). Si una decisión práctica obliga a apartarse, ADR y consulta.
8. **Techos declarados.** A y B derivan del propio diccionario: se presentan como límite superior.

---

## 4. Arquitectura objetivo — al pie de la letra

### 4.1 Estructura del repositorio entregable

```
TP_RAG_Quechua/
├── CLAUDE.md · CONSIDERACIONES.md · README.md
├── docs/                                ← especificación SDD (00…08), specs/, auditorias/, evidencias/, diagramas/
├── backend/
│   ├── src/
│   │   ├── domain/                      ← SIN imports externos (solo biblioteca estándar)
│   │   │   ├── entities/                   Consulta, Fragmento, FragmentoRecuperado, Fuente, Respuesta
│   │   │   ├── value_objects/              Idioma, Procedencia, PuntuacionSimilitud, Umbral
│   │   │   └── services/                   EvaluadorConfianza (regla de abstención), DepuradorConsulta,
│   │   │                                   Segmentador, VerificadorFormaLiteral
│   │   ├── application/
│   │   │   ├── ports/
│   │   │   │   ├── in/                     ConsultarCorpusPort, IngestarDocumentoPort,
│   │   │   │   │                           GestionarFuentesPort, ConsultarHistorialPort, ReindexarCorpusPort
│   │   │   │   └── out/                    IndiceRecuperacionPort, GeneradorTextoPort, TraductorPort,
│   │   │   │                               DetectorIdiomaPort, ExtraccionDocumentalPort,
│   │   │   │                               RepositorioCorpusPort, RepositorioFuentesPort,
│   │   │   │                               RepositorioConsultasPort
│   │   │   ├── use_cases/                  implementan los puertos de entrada
│   │   │   └── factories/                  RespuestaFactory (Factory Method)
│   │   ├── adapters/
│   │   │   ├── in/
│   │   │   │   ├── rest/                   un controlador FastAPI por recurso + esquemas Pydantic
│   │   │   │   ├── cli/                    comandos: indexar, evaluar, consultar, medir
│   │   │   │   └── mcp/                    servidor MCP de solo lectura (desarrollo, ADR-017)
│   │   │   └── out/
│   │   │       ├── recuperacion/           IndiceHibridoLexico
│   │   │       ├── generacion/             OllamaGenerador (Qwen3.5-4B)
│   │   │       ├── traduccion/             TraductorTabla (lemas, tiempo de compilación) · OllamaTraductor (alternativa)
│   │   │       ├── idioma/                 DetectorIdiomaHeuristico
│   │   │       ├── documentos/             ExtractorPdf (pypdf), CorpusJsonl
│   │   │       └── persistencia/           RepositorioConsultasSqlite (por defecto) · RepositorioConsultasPostgres,
│   │   │                                   RepositorioFuentes (SQLite/PostgreSQL + corpus/MANIFIESTO.yaml)
│   │   └── infrastructure/
│   │       ├── config.py                   pydantic-settings: τ = 0,48, rutas, BD, Ollama, estrategias
│   │       ├── contenedor.py               composition root: inyección de dependencias
│   │       └── main.py                     arranque FastAPI en 127.0.0.1, montaje de routers
│   ├── tests/{unit,integration,acceptance,architecture}/
│   ├── scripts/                           calibrar_umbral, medir_pmv1 (§8), reparar_acentos, exportar_indice_movil,
│   │                                      validar_indice_movil (sin lógica de negocio)
│   └── pyproject.toml · requirements*.txt
├── frontend/                            ← React + Vite (cliente del adaptador REST; ADR-025) · Vitest
├── corpus/                              ← MANIFIESTO.yaml versionado; pdf/ fuera de Git
├── referencia_poc/                      ← solo lectura
└── .github/workflows/ci.yml             ← ruff · pytest-cov · npm test · pip-audit · npm audit · SonarQube
```

`data/` (fragmentos, índices) queda fuera de Git y se regenera con `cli indexar` (DoD-1, ADR-015).

### 4.2 Reglas por capa (se comprueban con una **prueba de arquitectura**)

| Capa | Puede importar | Nunca importa |
|---|---|---|
| `domain` | biblioteca estándar | `application`, `adapters`, `infrastructure`, FastAPI, SQLAlchemy, Pydantic, httpx, numpy, scikit-learn |
| `application` | `domain` | `adapters`, `infrastructure`, cualquier *framework* |
| `adapters` | `application` (puertos), `domain` (entidades), sus bibliotecas | `infrastructure` (salvo tipos de configuración inyectados) |
| `infrastructure` | todo | — |

Implementarla con un test que recorra los `import` de cada paquete (o `import-linter`). Es evidencia directa
para E2 y C6.

### 4.3 Un canal = un adaptador de entrada + los puertos de entrada que usa

| Canal | Adaptador IN | Puertos de entrada que invoca |
|---|---|---|
| Web (React) → HTTP | `adapters/in/rest/consultas_controller.py`, `historial_controller.py`, `fuentes_controller.py`, `corpus_controller.py` | `ConsultarCorpusPort`, `ConsultarHistorialPort`, `GestionarFuentesPort`, `IngestarDocumentoPort`, `ReindexarCorpusPort` |
| Terminal | `adapters/in/cli/` | `IngestarDocumentoPort`, `ReindexarCorpusPort`, `ConsultarCorpusPort` |
| Agentes (desarrollo) | `adapters/in/mcp/` | `ConsultarCorpusPort` (solo lectura) |

La interfaz React **no** es un adaptador del backend: es un cliente del canal REST. Los controladores solo traducen
HTTP ↔ DTO y llaman al puerto; **no** contienen lógica.

### 4.4 Patrones obligatorios y dónde deben verse

| Patrón | Dónde | Evidencia para la exposición |
|---|---|---|
| **Repository** | `application/ports/out/repositorio_*_port.py` + `adapters/out/persistencia/` | Un puerto, dos implementaciones (SQLite y PostgreSQL) seleccionables por configuración; en pruebas, repositorios falsos |
| **Dependency Injection** | `infrastructure/contenedor.py` (composition root) | El constructor de cada caso de uso recibe puertos, no clases concretas |
| **Factory Method** | `application/factories/respuesta_factory.py` | `crear_respuesta`, `crear_respuesta_por_lema`, `crear_abstencion`, `crear_abstencion_con_pasajes`, `crear_idioma_no_soportado`: toda respuesta sale completa y rotulada |
| **Strategy** | `EstrategiaDecision` (`UmbralConLema` ahora; `UmbralAdaptativo` en PMV2, RF-15, que solo añade abstenciones) y `TraductorPort` (`TraductorTabla` / `OllamaTraductor`) seleccionados por configuración | Cambio de estrategia en `config.py` sin tocar el caso de uso |
| **Adapter** | Todo `adapters/` | Cada adaptador implementa exactamente un puerto |

### 4.5 Flujo del video (E3) mapeado al código

```
Usuario (React) ──HTTP──▶ ConsultasController (adapters/in/rest)
      ──▶ ConsultarCorpusPort (application/ports/in)
      ──▶ ConsultarCorpusUseCase (application/use_cases)
            ├─ DetectorIdiomaPort / TraductorPort ─▶ TraductorTabla     (solo la consulta; ADR-023)
            ├─ IndiceRecuperacionPort ─▶ IndiceHibridoLexico            ← módulo de IA (recuperación)
            ├─ EvaluadorConfianza (domain/services)                      ← similitud ≥ τ = 0,48 o lema exacto, antes de generar
            ├─ GeneradorTextoPort ─▶ OllamaGenerador (Qwen3.5-4B)        ← módulo de IA (generación)
            ├─ VerificadorFormaLiteral (domain/services)                 ← salvaguarda comprobada en código
            ├─ RespuestaFactory
            └─ RepositorioConsultasPort ─▶ RepositorioConsultasSqlite    ← persistencia (RF-11)
      ◀── RespuestaDTO: forma quechua literal, fragmento, documento, página, vía de respaldo (τ o lema)
```

---

## 5. Plan de trabajo (orden de PR)

Cada PR sigue el ciclo de `CLAUDE.md` §4, con rama y commits convencionales. Entre paréntesis, el rol de la
rúbrica que debería hacer los commits. Los PR 1–3 **reorganizan y formalizan** el código base: su
comportamiento ya coincide con la revisión 2, de modo que el criterio de éxito es que el arnés dé **las
mismas cifras** antes y después (prueba de no regresión sobre `arnes_por_consulta.csv`).

| PR | Rama | Contenido | Rol |
|---|---|---|---|
| 0 | `main` (script) | **`crear_repo.ps1`** (`docs/10_REPOSITORIO.md`): importa el código base **conservando su historial**, quita del historial el texto del corpus y `movil/`, añade `docs/`, `corpus/MANIFIESTO.yaml`, `referencia_poc/`, `CLAUDE.md`, este archivo y la configuración de Claude Code. Después, el orquestador congela la **línea base del arnés** del código base (M2–M4) antes de mover nada (`PROMPT_CIERRE_PMV1.md` paso 3) | PM (usuario) |
| 1 | `refactor/estructura-hexagonal` | Mover a `backend/src/{domain,application,adapters,infrastructure}` y `frontend/`; puertos de salida a `application/ports/out`; servicios de regla a `domain/services`; pruebas en verde; arnés idéntico a la línea base | Architect |
| 2 | `feat/puertos-entrada` | Interfaces en `application/ports/in/`; casos de uso las implementan; controladores por recurso dependientes solo del puerto; CLI (`indexar`, `calibrar`, `exportar-movil`, `medir`) | Architect + Backend |
| 3 | `fix/HU-06-reglas-de-respuesta` | τ = 0,48 con **un solo origen** (configuración + barrido versionado); **regla de lema** como estrategia explícita `UmbralConLema` (ADR-021) con campo `via_respaldo ∈ {similitud, lema}` en la respuesta; **pasajes de prosa** como tipo de resultado propio `PasajesSinAfirmacion` que cuenta como abstención (ADR-022); `RespuestaFactory`. Pruebas `@salvaguarda`: 0 FP en C con la regla de lema activa; con similitud < τ y sin lema exacto el generador **no** se invoca; un pasaje de prosa nunca lleva forma quechua destacada | Backend & AI |
| 4 | `feat/HU-06-verificador-forma-literal` | `VerificadorFormaLiteral` (RN-02): si la redacción contiene una palabra que no es castellano/inglés y no figura en el fragmento de respaldo, se descarta y se muestra la plantilla con la forma literal. Contar aceptadas/descartadas (M5) | Backend & AI |
| 5 | `feat/HU-05-traductor-estrategia` | Puerto `TraductorConsultaPort` con `TraductorTabla` (principal, ADR-023) y `OllamaTraductor` (alternativa); recuperar con la original **y** con cada lectura, quedarse con la mejor; mostrar **todas** las lecturas y la usada; lista de errores conocidos de la tabla (p. ej. `boiled corn → huayco`) en `docs/`. D se reporta como **techo** | Backend & AI |
| 6 | `fix/HU-02-ingesta-contrato` | Reingesta con el contrato RD-01 (`procedencia` obligatoria; `id` compatible, ADR-018); **corregir entradas truncadas** («SOL: Inti. (rayo de sol) Intip shaplan. (época de») y prueba de regresión; páginas sin texto **señaladas**; reparador de acentos con su cifra medida (M1); `RepositorioFuentesManifiesto` | Backend & AI |
| 7 | `feat/HT-04-interfaz-react` | Endurecimiento de `frontend/` (React + Vite) según la **lista del §5.1** | Frontend |
| 8 | `feat/RF-11-historial-sqlite` | `RepositorioConsultasPort` con `RepositorioConsultasSqlite` (**por defecto**, ADR-027) y `RepositorioConsultasPostgres` (segundo adaptador, opcional). Sin identificadores de persona; `DELETE /api/historial`; aviso en la interfaz (RNF-06, ADR-013) | Backend |
| 9 | `test/arquitectura-e-integracion` | Prueba de arquitectura; pruebas de API con `TestClient`; Gherkin (`pytest-bdd`, `# language: es`) para HU-01…HU-07, incluidos los escenarios de lema y de prosa; Vitest + Testing Library en `frontend/` | QA |
| 10 | `ci/github-actions-sonarqube` | CI con `ruff`, `pytest --cov --cov-report=xml`, `npm test`, `npm audit --omit=dev`, `pip-audit`, SonarQube; `newman` para Postman | QA & DevOps |
| 11 | `test/HT-01-mediciones` | `scripts/medir_pmv1.py` y ejecución completa del **§8** (M1–M15); resultados en `docs/evidencias/` | QA + Backend |
| 12 | `docs/readme-resultados` | README con estructura, patrones, comandos y **tabla de resultados medidos** (§8); aplicar en `docs/` las correcciones L-1…L-9 de `docs/09` que afecten a la especificación viva | PM + QA |

**Recalibración de τ.** Los PR 5 y 6 cambian la distribución de similitudes (nuevas lecturas de traducción,
entradas completas). El PR 11 ejecuta el barrido (M3) **con y sin** la regla de lema. Si el primer τ sin FP
deja de ser 0,48, el orquestador **propone** el nuevo valor con su barrido y el usuario decide (ADR-020
se actualiza). No se cambia en silencio.

### 5.1 Lista de endurecimiento de la interfaz React (PR 7)

El usuario ha señalado que la interfaz actual es un prototipo (p. ej. hay control para **aumentar** el
tamaño del texto pero no para **reducirlo**: un único botón «A+» que cicla normal → grande → mayor). Antes
de empezar, **pedir al usuario su lista completa de fallos observados** y añadirla aquí. Mínimo exigido:

| # | Requisito | Verificación |
|---|---|---|
| UI-01 | Controles **A−**, **A+** y **restablecer**, con `aria-label`, límites visibles (deshabilitados en el extremo) y preferencia recordada (`localStorage` con `try/catch`) | Prueba Vitest de los tres botones y de los extremos |
| UI-02 | Estados de **carga**, **error** (API caída, tiempo agotado, 422) y **vacío**, con mensaje en español y botón de reintento | Pruebas con la API simulada (`msw` o `fetch` falso) |
| UI-03 | Vista de respuesta: forma quechua **literal** destacada · fragmento completo · documento y página · similitud frente a τ · **vía de respaldo** («similitud ≥ τ» o «entrada exacta del diccionario») · aviso de alcance | Prueba de render con una `RespuestaDTO` de cada vía |
| UI-04 | Abstención: mensaje de ausencia **sin ninguna forma quechua destacada**; si hay pasajes de prosa, rotulados **«Pasajes relacionados — no es una respuesta»** con documento y página | Prueba `@salvaguarda` de interfaz |
| UI-05 | Consulta en inglés: **todas** las lecturas de la traducción y la que se usó | Prueba de render |
| UI-06 | Aviso cuando el fragmento procede de una página señalada (sin capa de texto o con acentos reparados) | Prueba de render |
| UI-07 | Historial desde `GET /api/historial` (no solo estado local), con botón **Borrar historial** y aviso de que no se guardan datos personales | Prueba de integración contra la API |
| UI-08 | Validación: 1–300 caracteres, contador visible, envío con Enter, botón deshabilitado mientras carga | Prueba Vitest |
| UI-09 | Accesibilidad WCAG 2.1 AA: contraste ≥ 4,5:1, foco visible, navegación completa por teclado, `lang="es"`, regiones `aria-live` para la respuesta | `eslint-plugin-jsx-a11y` + revisión manual con captura |
| UI-10 | *Responsive* desde 360 px sin desplazamiento horizontal | Captura a 360 px y a 1366 px |
| UI-11 | Sin recursos de terceros en tiempo de ejecución (fuentes, CDN, analítica): todo empaquetado por Vite (RS-03, RF-12) | Revisión de `index.html` y de la pestaña de red sin conexión |
| UI-12 | Una sola fuente de configuración de la URL de la API (`VITE_API_URL`, por defecto `http://127.0.0.1:8000`) | Revisión |

---

## 6. Historias del PMV1: qué hace falta para declararlas cerradas

| Historia | Punto de partida (código base) | Para cerrarla |
|---|---|---|
| HU-01 Ingesta con procedencia | Ingesta PDF | Validar contra el manifiesto; rechazar PDF sin entrada; páginas sin texto señaladas; Gherkin |
| HU-02 Segmentación e indexación | Segmentador y reindexación | Contrato RD-01, entradas completas, prueba de regresión de identificadores y de truncamiento |
| HU-03 Consulta léxica | Funciona | Gherkin con `zorro/Atuq/37`, `cóncavo/Puklu/9`, `confesar/Kunfisay/9`; vía de respaldo visible |
| HU-04 Contenido cultural | Sin conjunto de referencia (RD-05) | **Declararla no evaluada**; no inflarla (corrección L-1) |
| HU-05 Consulta en inglés | Tabla EN→ES | Estrategia de traducción (PR 5); recall@5 en D medido (M2) y **declarado techo**; si el usuario aporta consultas en inglés independientes (partición D′), medirlas por separado |
| HU-06 Salvaguarda | τ 0,48 + lema + prosa | Reglas explícitas (PR 3), verificador de forma literal (PR 4), 0 FP en C con y sin regla de lema (M3, M4) |
| HU-07 Trazabilidad | Documento y página en la respuesta | 100 % medido (M4); aviso de página señalada |
| RF-11 Historial | Persistido | SQLite por defecto tras el puerto; borrado disponible; aviso de privacidad (PR 8) |

«PMV1 al 100 %» significa: historias de prioridad Alta cerradas con DoD; HU-04 y HU-05 cerradas o
declaradas con su limitación explícita.

---

## 7. Equipo, commits y GitHub

### 7.1 Roles (Rúbrica S8) — asignar nombres con el usuario

| Rol | Responsable de | Carpetas/artefactos que commitea | Defiende en la exposición |
|---|---|---|---|
| PM / Scrum Master | Backlog, GitHub Projects, trazabilidad social/ética | `docs/`, Projects, informe C3–C4 | Punto 1 y C3–C4 |
| Architect & System Designer | Hexagonal, puertos, patrones, UML | `application/ports`, `infrastructure/`, diagramas | Punto 3 (arquitectura) |
| Lead Backend & AI Engineer | Dominio, casos de uso, reglas de respuesta, IA | `domain/`, `use_cases/`, `adapters/out/{recuperacion,generacion,traduccion,persistencia}` | C2, C6-PoC |
| Lead Frontend & Integration | Adaptadores de entrada, interfaz React, consumo de API | `frontend/`, `adapters/in/rest` | E1, video |
| QA & DevOps | Pruebas, mediciones, capturas, CI/CD, SonarQube | `tests/`, `frontend/src/**/*.test.jsx`, `scripts/medir_pmv1.py`, `.github/`, `docs/evidencias/` | Tabla de resultados, C5 |

### 7.2 Convenciones

GitHub Flow, ramas `tipo/ID-descripcion`, Conventional Commits en español con `Refs: HU-xx`, PR revisado
por **otro** integrante antes de fusionar (DoD-10). Detalle: `docs/06_MODELO_AGENTES.md` §7.

### 7.3 Datos en el repositorio

- Repositorio **privado** (ADR-011); se invita al docente como colaborador para la revisión.
- Texto del corpus (`fragmentos_*.jsonl`), índices, binarios exportados, base SQLite y PDF: **fuera de Git**
  (ADR-015); se regeneran con el CLI.
- Nunca credenciales: `.env` ignorado, `.env.example` sin valores (incluida la cadena de PostgreSQL).

### 7.4 GitHub Projects alineado al roadmap

- Campos: `Estado` (Backlog / Listo / En curso / En revisión / Hecho), `PMV` (1/2/3), `Sprint`, `Rol`,
  `Inicio`, `Fin`, `Historia` (HU/HT), `Puntos`.
- Vistas: **Roadmap** (Gantt por `Inicio`/`Fin`, agrupado por PMV) y **Board** (por `Estado`).
- Ítems: épicas E-01…E-11, historias HU/HT de `docs/03_HISTORIAS_USUARIO.md`, enlazadas a sus PR.
- Estado a presentar: **PMV1 hecho** (solo lo que cumpla el §6); **PMV2**: exportación y paridad hechas,
  analítica RF-14–16 pendiente; **PMV3**: adelantado como *spike*, sin validar en dispositivo físico.
- Con `gh`: `gh project create`, `gh project field-create`, `gh project item-add` (requiere
  `gh auth refresh -s project`). El agente prepara los comandos; el usuario los ejecuta o autoriza.

---

## 8. Protocolo de mediciones del PMV1 — lo que alimenta el informe, las figuras y las diapositivas

Las figuras y documentos de la exposición se regeneran **solo** con lo que produzca este protocolo. El
usuario entregará la carpeta resultante para elaborar imágenes y documentos con datos reales. Además,
estas mediciones **verifican** las cifras nuevas de la revisión 2 (0,48; 92,8 %; 180/180; 90,2 %; 70,6 %;
21,5 MB; 2,5 × 10⁻⁸): si alguna no se reproduce, se informa al usuario con la cifra medida.

### 8.1 Dónde y cómo

- Script único: `backend/scripts/medir_pmv1.py` (invocable también como `cli medir`). Ejecuta M1–M8 y
  M13–M15 y deja todo en `docs/evidencias/<AAAA-MM-DD>_<commit-corto>_<maquina>/`. M9–M12 se añaden con
  sus comandos.
- **Todo valor lleva metadatos**: fecha y hora, *commit*, rama, τ usado, estado de la regla de lema,
  modelo y su **cuantización** (`ollama show qwen3.5:4b`, campo *quantization*), versiones (Python, Node,
  Ollama, bibliotecas clave), huella SHA-256 del archivo de fragmentos, del conjunto de evaluación y de la
  tabla EN→ES, y la máquina (CPU, RAM, GPU y la línea `PROCESSOR` de `ollama ps`).
- Si una medición falla o no se puede ejecutar, se registra `"estado": "no_medido"` con el motivo. **Nunca
  se rellena a mano ni se estima.**
- Se ejecuta **dos veces**: en la PC del proyecto (RTX 4060) y en una PC sin GPU dedicada (p. ej. la de la
  universidad). Solo M5 y M6 dependen del hardware; esa comparación es un resultado en sí.

### 8.2 Qué medir

| ID | Medición | Qué registrar | Para qué se usa |
|---|---|---|---|
| **M1** | Corpus e ingesta | Documentos, páginas, páginas con texto y **señaladas**, fragmentos por `tipo` y por `procedencia`, fragmentos de prosa **legibles** y con **acentos reparados** (verifica 723/1 135 y 70,6 %), entradas truncadas detectadas por la prueba de regresión, documentos sin entrada en el manifiesto | C1, HU-01/02, L-1 |
| **M2** | Recuperación por partición (A 120 · B 60 · D 40 · D′/E si existen) | recall@1, recall@5, MRR@10 por partición; D **sin** traducción, con **tabla** y con **Ollama**; tiempo de traducción por estrategia | Tabla de resultados, HU-05, C6 |
| **M3** | Barrido de τ de 0,00 a 1,00 en pasos de 0,01 (positivos: A+B; negativos: C 28) | Por cada τ: VP, FP, VN, FN, precisión, recall, F1, especificidad, **con y sin regla de lema**. Resultado en τ = 0,41 (PoC), en τ = 0,48 (vigente) y en el **primer τ con FP = 0**; repetir incluyendo D traducido | Figura del umbral, matriz de confusión, ADR-020/021 |
| **M4** | Caso de uso completo con generador **falso instrumentado** (248 consultas) | Por partición: respondidas por **similitud**, respondidas por **lema**, abstenciones **con** y **sin** pasajes de prosa, FP; invocaciones al generador sin respaldo (**debe ser 0**); respuestas sin documento o página (**debe ser 0**) | HU-06, HU-07, salvaguarda |
| **M5** | Caso de uso con **Qwen3.5-4B real** vía Ollama — muestra de 30 consultas (10 A, 10 B, 10 D) + 5 de C | Latencia extremo a extremo P50/P95/máx.; primera consulta en frío y en caliente; de `/api/generate`: `total_duration`, `load_duration`, `prompt_eval_count`, `eval_count`, `eval_duration` → tokens/s; redacciones aceptadas y descartadas por el verificador; `ollama ps` (CPU o GPU) | RNF-01 (≤ 8 s), GPU frente a CPU, RN-02 |
| **M6** | Recursos | Memoria de video usada (`nvidia-smi --query-gpu=memory.used --format=csv`), RAM máxima del proceso (psutil), tamaño del modelo, tamaño del índice de escritorio y de la base SQLite | RNF-10, C5 |
| **M7** | Pruebas | Total, aprobadas, fallidas y omitidas por carpeta (`unit`, `integration`, `acceptance`, `architecture`) y de `frontend/` (Vitest); escenarios Gherkin aprobados por HU; `pytest -m salvaguarda`; JUnit (`--junitxml`) | Tabla de resultados, E2 |
| **M8** | Cobertura | Global y por capa (`domain`, `application`, `adapters`, `infrastructure`) y del `frontend/`; `coverage.xml` y `lcov.info` | Tabla de resultados, C5 |
| **M9** | SonarQube | Quality gate, bugs, vulnerabilidades, *security hotspots*, *code smells*, duplicación %, cobertura según Sonar, líneas de código + captura del panel | C5, punto 3 |
| **M10** | Postman / Newman | Solicitudes, aserciones totales y fallidas, tiempo medio (`newman run … -r json`) + captura | C5 |
| **M11** | Dependencias | Vulnerabilidades de `pip-audit -f json` y `npm audit --json --omit=dev` | C5, RS |
| **M12** | Git y gestión | Commits por autor (`git shortlog -sne`), PR fusionados y su revisor, ítems de Projects por estado y sus fechas (lead/cycle time), puntos por sprint si se estimaron | C4 (métricas ágiles reales), E2 |
| **M13** | Paridad del índice exportado | `scripts/validar_indice_movil.py` sobre las 248 consultas: diferencia máxima de similitud, coincidencia del top-1 y del top-5; tamaños de cada binario y total (verifica 2,5 × 10⁻⁸ y 11,85 MB; resuelve L-6). Si existe `paridad_test.dart`, su salida | PMV2, RN-10 |
| **M14** | Extractor y compositor deterministas | Aciertos del extractor sobre A+B (verifica 180/180); % de fragmentos lexicográficos que analiza (verifica 90,2 %); lista de los que no analiza con su motivo; formas del compositor idénticas al fragmento (**debe ser 100 %**) | ADR-026, PMV3 |
| **M15** | Reglas auxiliares | Nº de respuestas por **lema** con similitud < τ y su lista (consulta, similitud, entrada) · Nº de abstenciones con pasajes y pasajes por abstención · FP de cada regla en C · si el usuario aporta el conjunto de preguntas de prosa, sus cifras | ADR-021, ADR-022, L-8 |

### 8.3 Formato de salida

```
docs/evidencias/2026-09-30_ab12cd3_pc-rtx4060/
├── mediciones.json          ← todas las cifras de M1–M15 con sus metadatos
├── MEDICIONES.md            ← resumen legible generado desde el JSON (no escrito a mano)
├── barrido_umbral.csv       ← tau,regla_lema,vp,fp,vn,fn,precision,recall,f1,especificidad
├── arnes_por_consulta.csv   ← id,particion,consulta,traduccion,rango_pertinente,similitud_max,decision,via_respaldo,pasajes,respaldo_correcto
├── latencias.csv            ← id,particion,fase(fria|caliente),total_ms,generacion_ms,tokens_s,procesador
├── paridad.csv              ← id,sim_escritorio,sim_exportado,diferencia,top5_igual
├── respuestas_por_lema.csv  ← id,consulta,similitud,entrada
├── junit.xml · coverage.xml · lcov.info · pip_audit.json · npm_audit.json · newman.json · sonar.json
└── capturas/                ← nombres fijos (§8.4)
```

Estructura mínima de `mediciones.json`:

```json
{
  "meta": {"fecha": "", "commit": "", "rama": "", "tau": 0.48, "regla_lema": true,
           "modelo": "qwen3.5:4b", "cuantizacion": "",
           "maquina": {"cpu": "", "ram_gb": 0, "gpu": "", "ollama_processor": ""},
           "versiones": {"python": "", "node": "", "ollama": ""},
           "sha256": {"fragmentos": "", "evaluacion": "", "tabla_en_es": ""}},
  "M1_corpus": {"estado": "medido", "documentos": 0, "paginas": 0, "paginas_con_texto": 0,
                "paginas_senaladas": 0, "fragmentos": {"lexicografico": 0, "prosa": 0},
                "prosa_legible": 0, "prosa_acentos_reparados": 0, "entradas_truncadas": 0},
  "M2_recuperacion": {"A": {"recall@1": 0, "recall@5": 0, "mrr@10": 0}, "B": {},
                      "D_sin_traduccion": {}, "D_tabla": {}, "D_ollama": {}},
  "M3_umbral": {"en_tau_0_41": {}, "en_tau_0_48": {"vp": 0, "fp": 0, "vn": 0, "fn": 0, "recall": 0, "f1": 0},
                "primer_tau_sin_fp": {"con_lema": {}, "sin_lema": {}}},
  "M4_caso_de_uso": {"por_particion": {}, "por_lema": 0, "abstenciones_con_pasajes": 0,
                     "invocaciones_sin_respaldo": 0, "respuestas_sin_fuente": 0},
  "M5_generacion": {"n": 0, "p50_ms": 0, "p95_ms": 0, "fria_ms": 0, "tokens_s": 0,
                    "verificador": {"aceptadas": 0, "descartadas": 0}},
  "M6_recursos": {}, "M7_pruebas": {}, "M8_cobertura": {}, "M9_sonarqube": {},
  "M10_newman": {}, "M11_auditoria_dependencias": {}, "M12_git": {},
  "M13_paridad": {"dif_max": 0, "top1_igual": 0, "top5_igual": 0, "tamano_mb": 0},
  "M14_extractor": {"aciertos_AB": 0, "n_AB": 180, "cobertura_lexicografica": 0, "formas_identicas": 0},
  "M15_reglas": {"respuestas_por_lema_bajo_tau": 0, "fp_lema_en_C": 0, "abstenciones_con_pasajes": 0}
}
```

### 8.4 Capturas con nombre fijo (evidencia E1 y punto 3)

| Archivo | Qué muestra |
|---|---|
| `E1-1_consulta_zorro.png` | «¿cómo se dice zorro en quechua wanka?» → «Atuq», fragmento, documento, página 37, similitud ≥ τ, vía «similitud» |
| `E1-2_abstencion.png` | «¿cómo se dice criptomoneda…?» → ausencia de información, sin forma quechua |
| `E1-3_consulta_ingles.png` | Consulta en inglés con **todas** las lecturas de la traducción y la forma literal |
| `E1-4_respaldo_lema.png` | Respuesta por **entrada exacta del diccionario** con similitud < τ, rotulada |
| `E1-5_pasajes_prosa.png` | Abstención con pasajes de prosa rotulados «no es una respuesta» |
| `E1-6_historial.png` | Historial persistido con el botón de borrado y el aviso |
| `E1-7_fuentes_ingesta.png` | Fuentes del manifiesto e incorporación de un documento |
| `E1-8_validacion.png` | Consulta vacía o de más de 300 caracteres rechazada |
| `E1-9_tamano_texto.png` | Controles A− / A+ / restablecer en sus tres estados |
| `E1-10_movil_360px.png` | Interfaz a 360 px |
| `GH-1_estructura_src.png` · `GH-2_domain_sin_frameworks.png` | Árbol de `backend/src` y un archivo de `domain/` en GitHub |
| `QA-1_pytest.png` · `QA-2_sonarqube.png` · `QA-3_newman.png` · `QA-4_vitest.png` | Ejecuciones y paneles |
| `PM-1_projects_roadmap.png` · `PM-2_projects_board.png` | GitHub Projects |
| `HW-1_ollama_ps_gpu.png` · `HW-2_ollama_ps_cpu.png` · `HW-3_ollama_show.png` | Dónde corrió el modelo y su cuantización |

---

## 9. Video demostrativo (E3) — 1,5 a 2 minutos, sin cortes

> Versión detallada, con los casos ya comprobados sobre el código base, los defectos que hay que evitar en
> cámara y la tabla de salidas reales: **`docs/11_CASOS_VIDEO_Y_CAPTURAS.md`**. Para qué sirve cada
> medición en las diapositivas: **`docs/12_MEDICIONES_PARA_DIAPOSITIVAS.md`**.

1. (10 s) Pantalla dividida: app React + estructura `backend/src/` en el editor.
2. (30 s) `¿cómo se dice zorro en quechua wanka?` → `Atuq`, fragmento, documento, página 37, vía
   «similitud». En la terminal del backend, el log por capas: controller → puerto → caso de uso → índice →
   evaluador → generador → verificador → repositorio.
3. (25 s) `¿cómo se dice criptomoneda en quechua wanka?` → abstención; similitud frente a τ; el generador no
   se invoca (log).
4. (20 s) Consulta en inglés («how do you say fox…», **no** «water» hasta corregir D-2) → lecturas de la
   traducción visibles; forma quechua literal.
5. (15 s) Historial (con borrado) y validación de negocio (consulta vacía o demasiado larga).
6. (15 s) `pytest` y `npm test` en verde + panel de SonarQube.

Grabar en la PC con GPU; si se graba en CPU, verificar antes con M5 que la latencia no rompe la
continuidad. Añadir un **log estructurado por capa** (nivel INFO) para que el recorrido sea visible.

---

## 10. Informe técnico documental y recursos para la exposición

### 10.1 Informe (PDF) = Documentos 0–6 (revisión 2) actualizados y consolidados

| Competencia | Qué hay ya (Doc.) | Qué falta según S6/S7 |
|---|---|---|
| C1 | Doc 1: F1–F6, Ishikawa, árbol de problemas, riesgos | **BPMN AS-IS y SIPOC**, **5 Porqués**, KPIs cuantitativos explícitos, **matriz de restricciones**, correspondencia problema ↔ objetivos; alinear R-06 (L-4) |
| C2 | Doc 2 y 5 (con el anexo de corrección por medición) | RF de IA (≥ 3), justificación de F1/recall frente a *accuracy*, matriz conocimiento → aplicación; precisar la cuantización (L-5) |
| C3 | Doc 3: stakeholders, normativa, cadena ética, riesgo residual | **Matriz de cumplimiento LPDP** (incluido el historial persistido, L-9), **matriz ética de la IA**, impacto económico y ambiental con indicadores |
| C4 | Doc 4: Scrum, 4 sprints, backlog, DoD, roadmap | Trazabilidad **Objetivo → Épica → HU → Given/When/Then → PMV1**, métricas ágiles **reales** (M12), registro **CHG** (§11), capturas de Projects; «recuperación léxica» (L-3) |
| C5 | Doc 5 + anexo: herramientas retiradas por medición | Ecosistema en 7 categorías con **SonarQube, Postman, GitHub Actions, Vitest**; **reportes reales** (M7–M11); matriz de limitaciones |
| C6 | Doc 6: PoC completa con Go con condiciones | **UML de componentes, despliegue y paquetes en 4 capas**, puertos IN/OUT, 5 patrones, pruebas con *fakes*, **resultados del PMV1 (M1–M8, M13–M15)** |

### 10.2 Recursos visuales

`Recursos_Visuales_Exposicion.docx`, las diapositivas y el guion (fuera del repo) se hicieron con la
versión 1 (Streamlit, τ 0,41, traducción por SLM, historial en memoria). **Se regeneran en dos pasos:**
(1) ahora, a la línea base v2 (React, τ 0,48, regla de lema, pasajes de prosa, tabla EN→ES, móvil sin
modelo, SQLite), dejando «por medir» lo del PMV1; (2) cuando el usuario entregue la carpeta del §8, con
las cifras reales. Fuentes de las figuras: `docs/diagramas/` (matplotlib `.py`, PlantUML `.puml`,
Graphviz `.dot`).

### 10.3 Matriz integradora C1 → C6 (Punto 2 de la exposición)

| Competencia | Entrada | Artefacto generado | Salida hacia la siguiente |
|---|---|---|---|
| C1 | Necesidad: material publicado pero no consultable; wanka seriamente en peligro | F1–F6, árbol de problemas, KPIs, restricciones | Problema cuantificado y acotado |
| C2 | Problema y restricciones de C1 | RF/RNF (IA: RF-05, 06, 08, 14–16), fundamento del umbral y F1, matriz tecnológica | Requisitos de ingeniería y tecnologías justificadas |
| C3 | Requisitos y dominio de C2 | Stakeholders I-01…I-09, LPDP, ética de la IA, salvaguarda | Restricciones éticas → requisito de abstención |
| C4 | Alcance técnico y restricciones de C3 | Backlog E-01…E-11 / HU-01…HU-11 con G/W/T, roadmap 3 PMV | Plan incremental priorizado |
| C5 | Plan de C4 | Ecosistema (Python, FastAPI, React + Vite, Ollama, SQLite, Git, SonarQube, Postman) y limitaciones | Entorno técnico configurado |
| C6 | Requisitos de IA de C2 + historias de C4 + herramientas de C5 | PoC (Go con condiciones) + arquitectura hexagonal + PMV1 | **PMV1 ejecutable** en GitHub y video |

---

## 11. Cambios respecto de la versión 1 de la serie (registro CHG)

Cada cambio con su origen. Los CHG-01…CHG-12 están ya en la revisión 2 de los Documentos 0–6; los
CHG-13…CHG-16 los introduce la entrega de la Unidad II.

| CHG | Elemento | Versión 1 | Vigente | Origen | Estado |
|---|---|---|---|---|---|
| CHG-01 | Recuperación | bge-m3 + ChromaDB | Híbrido léxico TF-IDF (palabras + caracteres, promediados) | Doc. 6, C-2; ADR-005 | Aplicado |
| CHG-02 | Segmentación | Bloques uniformes | Una entrada léxica por fragmento | Doc. 6, C-3; ADR-007 | Aplicado (corregir truncados, PR 6) |
| CHG-03 | Almacén | ChromaDB · sqlite-vec | Sin base vectorial; índice exportado en binario plano en el móvil | Revisión 2; ADR-019 | Aplicado |
| CHG-04 | τ | 0,41 (PoC) | 0,48 (implementación) | Barrido sobre 248 consultas; ADR-020 | Aplicado; se remide en M3 |
| CHG-05 | Coincidencia de lema | — | Segunda vía de respaldo bajo τ | Código base; ADR-021 | **Propuesta** (decide el usuario) |
| CHG-06 | Prosa | Responder o abstenerse | Pasajes literales sin afirmación, cuentan como abstención | Revisión 2; ADR-022 | Aplicado; rotular (PR 3, 7) |
| CHG-07 | Consulta en inglés | Traducir con el SLM en tiempo de consulta | Tabla EN→ES de 2 257 lemas (principal) + Ollama (alternativa) | Revisión 2; ADR-023 | Aplicado; Strategy (PR 5) |
| CHG-08 | OCR | Tesseract | No se incorpora; páginas señaladas y reparador de acentos | PoC + revisión 2; ADR-024 | Aplicado |
| CHG-09 | Interfaz | Streamlit | React + Vite sobre FastAPI | Revisión 2; ADR-025 | Aplicado; **endurecer** (PR 7) |
| CHG-10 | Generación móvil | Qwen3.5-0.8B cuantizado | Sin modelo; extractor y plantilla deterministas | Prueba de fidelidad; ADR-026 | Aplicado; revisión abierta en PMV3 |
| CHG-11 | Persistencia | Historial de sesión | SQLite en los tres PMV; PostgreSQL como segundo adaptador | Revisión 2; ADR-027 | **Propuesta** |
| CHG-12 | PMV2 | Cuantización + exportación del codificador | Exportación del índice + paridad (hecho); analítica RF-14–16 (pendiente) | Revisión 2 | Parcial |
| CHG-13 | Análisis estático | Excluido por proporción (Doc. 5) | SonarQube en CI | Consigna U-II; ADR-010 | En curso (PR 10) |
| CHG-14 | Estructura del código | Sin `src/` ni puertos de entrada | `backend/src/{domain,application,adapters,infrastructure}` + `frontend/` | Lista de cotejo E2 | En curso (PR 1–2) |
| CHG-15 | Salvaguarda en código | Solo instrucción al generador | `VerificadorFormaLiteral` | RN-02 | En curso (PR 4) |
| CHG-16 | Calendario | Hito 1 al cierre del sprint 2 | PMV1 en la semana del 2026-09-28 | Calendario de evaluación | Aplicado |

---

## 12. Lo que el agente no puede hacer y hará el equipo

Grabar el video · capturas finales en su equipo · commits de cada integrante · nombres y roles de la
carátula · invitar al docente al repo · ejecutar M5 en la GPU y en la CPU · **aprobar o rechazar ADR-021
(regla de lema), ADR-027 (SQLite), ADR-013 (registro anónimo) y cualquier cambio de τ** · entregar la lista
de fallos de la interfaz (§5.1) · aportar consultas de docentes de EIB (partición E) y, si se quiere, consultas
en inglés independientes (D′) · corregir L-1…L-9 en los `.docx` · completar licencias del manifiesto ·
entregar al asistente documental la carpeta de `docs/evidencias/` · probar el APK en el POCO F8 Pro si se
quiere mostrar el PMV3 · exponer.
