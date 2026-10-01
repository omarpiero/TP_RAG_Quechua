# 08 · Auditoría del repositorio base

> Repositorio auditado: `github.com/DalgomXD-byte/asistente-quechua-wanka` (rama `main`, último commit
> `8eb172b`, 2026-09-22). Auditoría del 2026-09-24 contra la **Lista de cotejo de la Unidad II (S7)**, la
> **Consigna (S6)**, la **Rúbrica de exposición (S8)**, la **Trazabilidad integradora (S6)** y la
> especificación de `docs/`. Todas las cifras de este archivo se **midieron** al ejecutar el código del
> repositorio; no se transcriben del README.
>
> Destino: el código es el **punto de partida** del repositorio entregable `github.com/omarpiero/TP_RAG_Quechua`
> (hoy vacío). **Esta auditoría describe el código base; no fija decisiones del producto.**
>
> **Actualización 2026-09-24 (línea base v2).** Tras esta auditoría el equipo entregó la **revisión 2** de los
> Documentos 0–6, que incorpora como especificación la mayoría de lo que aquí figuraba como divergencia
> (τ = 0,48, pasajes de prosa, tabla EN→ES, React, sin base vectorial, SQLite/PostgreSQL). Los §5 y §6 se
> reescribieron con esa referencia; los §1–§4 conservan lo auditado y se anotan donde cambió su lectura.
> Decisiones vigentes: `docs/09_LINEA_BASE_V2.md`. Las cifras del §3 son del código base y **no** se usan
> como resultados del PMV1.

---

## 1. Veredicto

**Punto de partida sólido; no apto para entregar tal cual.** Con la revisión 2, su **comportamiento coincide
con la especificación** salvo una regla no documentada (coincidencia de lema bajo τ, ADR-021) y un defecto de
segmentación (entradas truncadas). Le falta **la forma exigida por la rúbrica** (estructura `src/`, puertos de
entrada, dos patrones sin evidencia, commits del equipo), **una garantía de seguridad** que hoy depende solo de
la instrucción al modelo, y una **interfaz** que pase de prototipo a producto.

| Criterio de la lista de cotejo | Estado en el repo base | Brecha principal |
|---|---|---|
| E2 · estructura `src/domain`, `src/application`, `src/adapters`, `src/infrastructure` | ⚠ Parcial: `backend/domain`, `backend/application`, `backend/infrastructure/adapters/{input,output}` | Sin `src/`; adaptadores dentro de infraestructura; puertos en el dominio |
| E2 · dominio independiente de *frameworks* | ✅ Solo biblioteca estándar (`abc`, `dataclasses`, `uuid`, `datetime`, `enum`) | — |
| E2 · interfaces de **puertos de entrada** (casos de uso) | ❌ Los casos de uso son clases concretas; el controlador REST llama a la clase | Crear `application/ports/in/` |
| E2 · puertos de salida con inyección de dependencias | ✅ 8 puertos ABC; *composition root* en `infrastructure/contenedor.py` | Mover a `application/ports/out/` |
| E2 · servicio de IA funcional | ✅ Recuperación híbrida léxica + Ollama (Qwen3.5-4B) + traducción | Falta verificación automática de la forma quechua (ver §4) |
| E2 · commits constantes **del equipo** | ❌ 19 commits, **un solo autor** (James Saenz Castro), 21 y 22 de septiembre | Historial de los 5 integrantes en el repo nuevo |
| E2 · sin credenciales expuestas | ✅ `.env` ignorado; `.env.example` sin secretos | — |
| C6 · patrones Repository, Factory, DI, Strategy, Adapter | ⚠ Repository ✅ · DI ✅ · Adapter ✅ · Strategy implícito (traductor tabla/Ollama) · **Factory ❌** | Hacer explícitos Factory y Strategy |
| C6 · pruebas de casos de uso con *fakes* | ✅ `IndiceFalso`, `GeneradorFalso`, `RepositorioFalso`, etc. | — |
| C5 · SonarQube / cobertura | ❌ Sin análisis ni informe | Añadir CI con `pytest-cov` + SonarQube |
| C5 · Postman | ✅ Colección con 15 *endpoints* y comprobaciones | — |
| E1 · interfaz web | ⚠ React + Vite funcional (vigente, ADR-025) pero **prototipo**: p. ej. solo «A+» para el tamaño del texto, historial solo en estado local | Endurecer (PR 7 y §5.1 de `CONSIDERACIONES.md`) |
| E3 · guion del video | ✅ `docs/GUION_DEMO.md` (6–8 min) | Recortar a 1,5–2 min y mostrar el recorrido por capas |

---

## 2. Qué hay en el repositorio

| Área | Contenido |
|---|---|
| Dominio | Entidades `Consulta`, `Fragmento`, `FragmentoRecuperado`, `Fuente`, `Respuesta`; objetos de valor `Idioma`, `Procedencia`, `PuntuacionSimilitud`; 8 puertos ABC |
| Aplicación | Casos de uso `ConsultarCorpus`, `IngestarDocumento`, `GestionarFuentes`; servicios `DepuradorConsulta`, `EvaluadorConfianza`, `Segmentador` |
| Adaptadores de entrada | Un único `api.py` (FastAPI, 11 rutas bajo `/api`) + `esquemas.py` (Pydantic) |
| Adaptadores de salida | Índice híbrido léxico, Ollama generador y traductor, traductor por tabla, extractor pypdf, corpus JSONL, repositorios SQLAlchemy (PostgreSQL o SQLite) |
| Infraestructura | `config.py` (pydantic-settings; τ = 0,48 configurable), `contenedor.py` (inyección manual) |
| Interfaz | React 18 + Vite: `CajaConsulta`, `Respuesta`, `Historial`, `GestionFuentes`, `GestionCorpus` |
| Scripts | Calibración del umbral, evaluación de prosa y traducción, exportación móvil, reparación de OCR, generación de la tabla EN→ES |
| Datos versionados | `fragmentos_v2.jsonl`, `fragmentos_v3.jsonl` (texto del corpus), `evaluacion_v2.json`, `traduccion_en_es.json` (6 131 entradas), conjuntos de prosa |
| Tamaño | ≈ 3 200 líneas de Python en la aplicación + ≈ 1 600 en scripts |

Historias cubiertas según su README: HU-01, HU-02, HU-03, HU-05, HU-06, HU-07, RF-11 y RF-13. HU-04 funciona
parcialmente (pasajes de prosa) y **no está evaluada**.

---

## 3. Mediciones propias (2026-09-24)

| Medición | Resultado | Cómo se obtuvo |
|---|---|---|
| Pruebas | **40 de 40 en verde** (2,6 s) | `pytest` en `backend/` |
| Cobertura global | **51 %** | `pytest --cov` sobre `domain`, `application`, `infrastructure` |
| Cobertura de dominio y aplicación | 73 %–100 % por archivo (casos de uso 95–96 %) | ídem |
| Cobertura de adaptadores | 0 % en API, Ollama, persistencia, configuración y contenedor | ídem |
| Barrido del umbral | Primer τ sin falsos positivos = **0,48** → VP 167 · FN 13 · FP 0 · VN 28 · recall **0,928** · F1 **0,963** | `scripts/calibrar_umbral.py` |
| Punto de mayor F1 (descartado) | τ 0,25 · F1 0,997 · **1 FP** | ídem |
| Caso de uso completo, 248 consultas (sin generador real) | A 120/120 · B 60/60 · D 40/40 responden con el fragmento de referencia · **C 0/28 responden (0 FP)** | Script de auditoría con doble del generador |
| El generador no se invoca sin respaldo | 220 invocaciones = exactamente las 220 consultas con respaldo | ídem |
| Latencia del caso de uso sin generación | media 5,6 ms · P95 13,6 ms | ídem |
| Latencia con generación (README) | 3,5 s | **No verificada** en esta auditoría (requiere Ollama) |

**Por qué A, B y D llegan al 100 % aunque el umbral solo conserve el 92,8 %:** la «capa de coincidencia de
lema» responde cuando el término consultado es exactamente el lema de una entrada del diccionario, sin
pasar por τ (el usuario lo observó en vivo: «sol» respondido con similitud 0,351). La revisión 2 no la
recoge en RF-08; se **formaliza con ADR-021** o se retira, según decida el usuario. El τ = 0,48 de esta tabla
es el primer valor sin FP de esta implementación y es el **vigente** (ADR-020); la PoC dio 0,41 con otra
formulación del híbrido. **Precaución:** D alcanza 40/40 con una tabla EN→ES generada por un modelo a partir de los
mismos lemas del corpus, y las consultas de D se derivaron de esos mismos lemas. Es un **techo** por
construcción, no el desempeño esperable con consultas reales.

---

## 4. Hallazgos

### Bloqueantes para la entrega

| # | Hallazgo | Por qué importa | Corrección |
|---|---|---|---|
| B-1 | No hay **puertos de entrada**: `api.py` instancia y llama a los casos de uso concretos | La lista de cotejo (E2) y el video (E3: *Controller → Input Port → Use Case*) lo exigen expresamente | Una interfaz por caso de uso en `application/ports/in/`; los casos de uso la implementan; cada canal (REST, CLI, MCP) depende solo del puerto |
| B-2 | Estructura sin `src/` y con adaptadores dentro de infraestructura | E2 pide `src/domain`, `src/application`, `src/adapters`, `src/infrastructure` literalmente | Reestructurar (ver `CONSIDERACIONES.md` §4) |
| B-3 | Un solo autor en los 19 commits | E2 pide «historial de commits constante por los integrantes» | Repo nuevo con commits de los 5 integrantes, cada uno desde su cuenta |
| B-4 | La forma quechua literal **solo la protege la instrucción** al generador (RN-02) | El propio README reconoce que el modelo «interpretó de más» (`uña` leído como castellano). Una salvaguarda que depende del *prompt* no es verificable | Verificador en la aplicación: toda palabra de la respuesta que no sea castellano/inglés debe figurar en algún fragmento de respaldo; si no, se descarta la redacción y se muestra el fragmento literal |

### Mayores

| # | Hallazgo | Corrección |
|---|---|---|
| M-1 | **Factory** sin evidencia; **Strategy** solo implícito | `RespuestaFactory` (respuesta, abstención, idioma no soportado) y `EstrategiaTraduccion` (tabla / modelo) o `EstrategiaDecision` (umbral fijo / adaptativo en PMV2), nombrados como tales |
| M-2 | `UMBRAL_CALIBRADO = 0.48` repetido como literal en `evaluador_confianza.py` además de en la configuración | Un único origen: configuración versionada (RN-04) |
| M-3 | En la abstención se ofrecen **pasajes de prosa** «podrían tratarla; léelos y juzga tú» | Recogido por la revisión 2 (ADR-022). Falta rotularlos «no es una respuesta» y contarlos como abstención en el arnés |
| M-4 | La tabla `traduccion_en_es.json` fue generada por un modelo y tiene errores visibles (`abreast → adrede`, entradas como `abrevas`) | Un error de traducción puede devolver una entrada de otra palabra **con respaldo real**: no inventa quechua, pero responde a otra cosa. Mostrar siempre el término buscado (ya se hace) y revisar la tabla |
| M-5 | `scripts/evaluar_traduccion.py` y `validar_tabla_ingles.py` **no ejecutan** (API desactualizada; ruta inexistente) | La cifra «recall@5 D = 0,950» del README no es reproducible hoy. Reparar o retirar la afirmación |
| M-6 | Incoherencia en el README: «100 % de consultas atendibles conservadas» frente al comentario del código «92,8 %» | Declarar ambas: 92,8 % por umbral; 100 % con la capa de lema |
| M-7 | Adaptadores sin pruebas (0 %) | Pruebas de integración de la API con `TestClient` y del repositorio con SQLite en memoria |
| M-8 | Sin análisis estático, sin CI | GitHub Actions con `ruff`, `pytest --cov`, `pip-audit` y SonarQube |

### Menores

| # | Hallazgo |
|---|---|
| m-1 | El repo base es **público** y versiona el texto completo del corpus (`fragmentos_v*.jsonl`); conviene hacerlo privado (riesgo R-07, licencias) |
| m-2 | `fragmentos_v*.jsonl` no tiene el campo `procedencia` del contrato de datos; la procedencia OCR se modela en `Fuente`, no en el fragmento |
| m-3 | `scripts/reparar_ocr.py` modifica texto del corpus (tildes separadas en la prosa). Es legítimo, pero debe documentarse como transformación y comprobarse que no altera formas quechuas |
| m-4 | Nombres de rama/commit sin convención (no hay Conventional Commits ni referencias a historias) |
| m-5 | La app móvil vive en otro repositorio (`quechua-wanka-movil`); para la entrega del PMV1 no es necesaria y **no debe presentarse como PMV3 terminado** |

---

## 5. Qué se reutiliza (línea base v2)

| Se reutiliza moviendo de carpeta, con sus pruebas | Se reutiliza con cambios | No entra en el PMV1 |
|---|---|---|
| Entidades, objetos de valor, puertos de salida | Casos de uso (implementan puertos de entrada; usan `RespuestaFactory`) | `ejecutable.py`, `.spec` de PyInstaller |
| `Segmentador`, `DepuradorConsulta`, `ExtractorPdf`, `CorpusJsonl` | `IndiceHibridoLexico`: regla de lema como estrategia explícita `UmbralConLema` (ADR-021) | Repositorio móvil → PMV2/PMV3 (se cita, no se presenta como terminado) |
| `OllamaGenerador` (instrucción restrictiva) | `EvaluadorConfianza`: τ = 0,48 **solo** desde configuración | Afirmación «recall@5 D = 0,950» del README hasta que sus scripts se reparen (M-5) |
| `OllamaTraductor` y `TraductorTabla` | Traducción como Strategy tras `TraductorConsultaPort`; revisar errores de la tabla (M-4) | |
| Repositorios SQLAlchemy | SQLite por defecto, PostgreSQL como segundo adaptador (ADR-027); borrado del historial | |
| Pruebas con dobles (`IndiceFalso`, `GeneradorFalso`, `RepositorioFalso`…) | `api.py` → un controlador por recurso bajo `adapters/in/rest/` | |
| Colección Postman, `GUION_DEMO.md` como referencia | Ingesta: contrato RD-01 con `procedencia`; entradas léxicas completas | |
| Interfaz React + Vite | Endurecida según `CONSIDERACIONES.md` §5.1 | |
| Scripts de exportación y paridad del índice móvil | Promovidos a `backend/scripts/` y medidos (M13) | |

---

## 6. Brechas frente a la línea base v2

| Tema | Código base | Línea base v2 | Referencia | PR |
|---|---|---|---|---|
| Umbral | τ = 0,48 duplicado como literal | τ = 0,48 con un solo origen (configuración + barrido) | ADR-020, RN-04 | 3 |
| Coincidencia de lema | Responde bajo τ sin rótulo | Segunda vía de respaldo **explícita**, rotulada y probada (0 FP en C), o retirada | ADR-021 (propuesta) | 3 |
| Pasajes de prosa | Se ofrecen sin rótulo explícito | Rotulados «no es una respuesta»; cuentan como abstención | ADR-022 | 3, 7 |
| Forma literal | Solo protegida por la instrucción | `VerificadorFormaLiteral` | RN-02 | 4 |
| Traducción | Tabla (y Ollama) sin Strategy nombrada | `TraductorConsultaPort` con dos estrategias; todas las lecturas visibles | ADR-023 | 5 |
| Fragmentos | Sin `procedencia`; entradas truncadas (p. ej. «SOL: … (época de») | Contrato RD-01; entrada completa; prueba de regresión | RD-01, ADR-007 | 6 |
| Interfaz | Prototipo (solo «A+», historial local, sin estados de error) | Lista UI-01…UI-12 | ADR-025 | 7 |
| Historial | PostgreSQL | SQLite por defecto, PostgreSQL opcional, borrado y aviso | ADR-027, ADR-013, RNF-06 | 8 |
| Estructura y puertos de entrada | `backend/{domain,application,infrastructure}` | `backend/src/{domain,application,adapters,infrastructure}` + `ports/in` | Lista de cotejo E2 | 1, 2 |
