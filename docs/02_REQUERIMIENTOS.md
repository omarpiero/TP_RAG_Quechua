# 02 · Especificación de requerimientos

> Fuente de verdad de **qué** debe hacer el sistema y **cómo se comprueba**. Los requerimientos proceden
> del Documento 0 (Tablas 4 y 5), la priorización del Documento 4 (Tabla 8) y los parámetros medidos en
> el Documento 6. Todo requerimiento lleva un criterio de verificación observable; si no se puede
> verificar, no está listo para desarrollarse.
>
> Mantenido por: **archivista** (solo modifica tras decisión registrada en `07_DECISIONES.md`) ·
> Última revisión: 2026-09-24 · Versión 1.1

---

## 1. Convenciones

| Campo | Valores |
|---|---|
| ID | `RF-nn` funcional · `RNF-nn` no funcional · `RN-nn` regla de negocio (invariante) · `RS-nn` criterio de seguridad derivado · `RD-nn` requisito de datos |
| Prioridad (MoSCoW) | **M** debe · **S** debería · **C** podría · **W** no en este proyecto. Derivada de la prioridad Alta/Media del Documento 4. |
| PMV | 1, 2, 3 o T (transversal) |
| Estado | `Especificado` → `En desarrollo` → `Verificado` → `Aceptado` · también `Bloqueado` o `Pospuesto` |
| Verificación | **P** prueba automatizada (pytest / flutter_test) · **A** arnés de evaluación · **M** medición instrumentada · **R** revisión (auditor o humano) · **D** demostración en Sprint Review |

Los identificadores son **estables**: no se reutilizan ni se renumeran. Si un requerimiento se divide, se
usan sufijos (`RF-15.1`).

---

## 2. Requerimientos funcionales

| ID | Nombre | Descripción (Documento 0) | Criterio de verificación | Verif. | Prior. | PMV | HU | Estado |
|---|---|---|---|---|---|---|---|---|
| RF-01 | Ingesta documental | Cargar PDF del corpus y extraer su texto; **señalar** los documentos sin capa de texto y **reparar los acentos** separados por la extracción (v2, ADR-024). | Todo PDF de `corpus/` produce fragmentos con `documento`, `pagina` y `procedencia`; las páginas sin texto se señalan (no se aplica OCR). Recomponer capas rotas cuando la longitud media de línea sea < 12 caracteres. Ninguna entrada lexicográfica queda truncada (prueba de regresión). | P | M | 1 | HU-01 | Especificado |
| RF-02 | Segmentación e indexación | Dividir el texto en fragmentos, generar sus **representaciones léxicas** y almacenarlas en un **índice de recuperación persistente** (v2, ADR-019). | Material `lexicografico`: una entrada por fragmento. `prosa`: bloques de ~650 caracteres por límite de párrafo. El índice reporta el número de fragmentos (referencia actual: 3 605). | P + A | M | 1 | HU-02 | Especificado |
| RF-03 | Consulta en lenguaje natural | Recibir consultas en español o inglés mediante interfaz gráfica. | La interfaz acepta texto libre de 1 a 300 caracteres y lo envía al núcleo. Fuera de ese rango, mensaje de validación sin invocar la recuperación. | P | M | 1 | HU-03 | Especificado |
| RF-04 | Detección de idioma | Identificar el idioma de la consulta y responder en ese idioma. | Español e inglés se detectan correctamente en el conjunto de evaluación; otro idioma recibe el aviso «solo se admiten consultas en español o inglés». La consulta en inglés se **traduce al español antes de recuperar** con la **tabla de lemas** calculada en tiempo de compilación, mostrando todas las lecturas (ADR-008, ADR-023). Meta: recall@5 ≥ 0,80 en D, declarado como **techo** mientras D derive de los mismos lemas. | P + A | S* | 1 | HU-05 | Especificado |
| RF-05 | Recuperación **léxica** (v2) | Recuperar los fragmentos con mayor relevancia. | Híbrido léxico: coseno sobre TF-IDF de palabras y de n-gramas de caracteres 3–5, promediados; depuración del fraseo; capa de coincidencia de lema. recall@5 ≥ 0,80 en A y B (PoC: 1,000). Particiones reportadas por separado. | A | M | 1 | HU-02, HU-03 | Especificado |
| RF-06 | Generación contextualizada | Elaborar la respuesta exclusivamente a partir de los fragmentos recuperados, mostrando la forma quechua. Escritorio: Qwen3.5-4B. Móvil: plantilla determinista (ADR-026). | Toda forma quechua de la salida aparece literalmente en algún fragmento recuperado (verificador automático). El generador **no se invoca** sin respaldo (RN-01). | P + A | M | 1 | HU-03, HU-04 | Especificado |
| RF-07 | Trazabilidad de la fuente | Mostrar con cada respuesta el fragmento original, el documento y la página. | El 100 % de las respuestas incluye `documento`, `pagina` y fragmento literal. Si `procedencia = reconocimiento óptico`, se muestra la advertencia de posible error de transcripción. | P | M | 1 | HU-07 | Especificado |
| RF-08 | Declaración de ausencia de información | Si la consulta no tiene respaldo, informarlo y no generar traducción. Ante material de prosa, entregar pasajes literales y citados **sin afirmar** (v2, ADR-022). | Respaldo = coseno ≥ τ (0,48, ADR-020) **o** coincidencia exacta de lema (ADR-021, propuesta). **0 falsos positivos** en C. La abstención —con o sin pasajes— no contiene ninguna forma quechua redactada y cuenta como abstención en las métricas. | P + A | M | 1 | HU-06 | Especificado |
| RF-09 | Consulta de vocabulario | Atender consultas léxicas (equivalencia español/inglés → quechua). | Cubierto por los criterios de RF-05 y RF-06 sobre las particiones A, B y D. | A | M | 1 | HU-03 | Especificado |
| RF-10 | Consulta de contenido cultural | Atender consultas sobre relatos, saberes y expresiones del corpus. | Existe un conjunto de referencia de consultas culturales anotado (hoy **no existe**: ver RD-04). Las consultas ambiguas solicitan precisión en lugar de responder. | A + R | S | 1 | HU-04 | Especificado |
| RF-11 | Historial de sesión | Conservar consultas y respuestas de la sesión activa. | Historial tras `RepositorioConsultasPort` (SQLite por defecto, ADR-027 propuesta). Sin identificadores de persona; aviso en la interfaz; opción de borrar el historial (RNF-06). | P | S | 1 | HU-03 | Especificado |
| RF-12 | Operación local | Todo el procesamiento en el equipo, sin transmitir consultas ni corpus a terceros. | Con la red desactivada, el flujo completo funciona. Ninguna dependencia hace llamadas salientes en ejecución (verificable con prueba de red bloqueada). | P + R | M | T | todas | Especificado |
| RF-13 | Gestión del corpus | Reconstruir el índice al incorporar nuevos documentos. | Un único comando reconstruye el índice; reindexar dos veces no duplica fragmentos (identificador determinista, ADR-018). | P | M | 1 | HU-02 | Especificado |
| RF-14 | Predicción de cobertura documental | Estimar, antes de invocar al generador, la probabilidad de respaldo a partir de la similitud máxima, la dispersión de los k fragmentos, la longitud y el campo semántico de la consulta. | En validación cruzada, la decisión combinada (τ + predictor) **no produce más FP** que τ solo y reduce invocaciones innecesarias del generador. Ver RN-06. | A | M | 2 | HU-08.1 | Especificado |
| RF-15 | Riesgo de alucinación y umbral adaptativo | Estimar un puntaje de confianza y ajustar τ a partir de las decisiones registradas. | El umbral adaptado **nunca** produce FP sobre la partición C ni desciende del último τ sin FP calibrado con el arnés. Si no mejora al umbral fijo, se conserva el fijo y se reporta el resultado negativo. | A | M | 2 | HU-08.2 | Especificado |
| RF-16 | Demanda léxica y priorización del corpus | Proyectar con series temporales los campos semánticos con mayor demanda insatisfecha y recomendar qué incorporar. | Con historial ≥ 100 consultas, informe ordenado; con menos, el sistema lo declara y no proyecta (HU-09, escenario 2). | P + A | S | 2 | HU-09 | Especificado |

\* RF-04 figura como prioridad media en el Documento 4, pero la especificación de construcción exige
recall@5 ≥ 0,80 en D para cerrar el Hito 1. **Tensión abierta**: se trata en `07_DECISIONES.md`
(ADR-008) y la resuelve el orquestador con el usuario en la planificación del sprint 2.

---

## 3. Requerimientos no funcionales

| ID | Atributo | Métrica y umbral | Cómo se mide | Verif. | Prior. | PMV | DoD | Estado |
|---|---|---|---|---|---|---|---|---|
| RNF-01 | Rendimiento | Respuesta completa ≤ **8 s** en escritorio y ≤ **15 s** en móvil, desde el envío hasta la presentación. | Percentil 95 sobre el conjunto de evaluación, en el equipo de referencia (RTX 4060) y en el dispositivo de prueba. | M | M | 1, 3 | DoD-6 | Especificado |
| RNF-02 | Latencia de recuperación | Búsqueda sobre el índice **precalculado** ≤ **100 ms** en móvil. | Medido en **dispositivo físico** (hoy solo hay medición en emulador); referencia escritorio: 5,2 ms. | M | M | 3 | DoD-6 | Especificado |
| RNF-03 | Operación sin conexión | Móvil totalmente operativo sin red (índice exportado, tabla EN→ES y compositor determinista). | Prueba en modo avión con el conjunto C y una muestra de A. | M + D | M | 3 | DoD-5 | Especificado |
| RNF-04 | Portabilidad | Android ARM64, mínimo 4 GB de RAM y 2 GB de almacenamiento. | Instalación y ejecución en el dispositivo de prueba; se declaran los mínimos **verificados**, no los estimados. | M | M | 3 | DoD-6 | Especificado |
| RNF-05 | Tamaño del paquete | APK + índice ≤ **1,2 GB**. | Tamaño del artefacto ARM64 (medido en v2: 21,5 MB; índice exportado 11,85 MB). | M | M | 3 | DoD-6 | Especificado |
| RNF-06 | Privacidad y seguridad | Ninguna consulta ni fragmento sale del dispositivo; no se recolectan datos personales. | Revisión del auditor + prueba de red bloqueada + criterios RS-01…RS-08. | R + P | M | T | DoD-5 | Especificado |
| RNF-07 | Mantenibilidad | Sustituir motor de inferencia, índice de recuperación o extractor no modifica el núcleo. | Prueba de arquitectura: el paquete `dominio` no importa bibliotecas de terceros. Deuda técnica y duplicación bajo la puerta de calidad de SonarQube (ADR-010). | P + R | M | T | DoD-8 | Especificado |
| RNF-08 | Trazabilidad | Toda respuesta vinculable a documento, página y fragmento. | Igual que RF-07; además, la traducción de la consulta queda en la traza (ADR-008). | P | M | T | DoD-3 | Especificado |
| RNF-09 | Usabilidad | Consulta completada en ≤ **3 interacciones** sin instrucciones. | Prueba con usuarios representativos (tarea humana) + prueba de interfaz automatizada del número de pasos. | M + D | S | 3 | — | Especificado |
| RNF-10 | Eficiencia computacional | Inferencia dentro de **8 GB** de VRAM, sin nube. | Pico de memoria de video medido durante el conjunto de evaluación. | M | M | 1 | DoD-6 | Especificado |
| RNF-11 | Gobernanza ética (CARE) | Cada fuente con procedencia, fecha de extracción y licencia. | Manifiesto del corpus completo; la ingesta rechaza un PDF sin entrada en el manifiesto. | P | M | T | DoD-7 | Especificado |
| RNF-12 | Escalabilidad del corpus | Incorporar documentos sin modificar código, solo reindexando. | Añadir un PDF + entrada de manifiesto + comando de reindexación; ninguna modificación en `src/`. | P | M | 1 | DoD-1 | Especificado |

---

## 4. Reglas de negocio (invariantes del núcleo)

Son propiedades que **ningún incremento puede romper**. Cada una debe tener al menos una prueba
automatizada en el núcleo y ejecutarse en integración continua en todas las ramas.

| ID | Regla | Origen | Prueba mínima |
|---|---|---|---|
| RN-01 | Sin respaldo —S(mejor fragmento) < τ **y** sin coincidencia exacta de lema (ADR-021)— se declara ausencia de información y **no se invoca** al generador. | RF-08, DoD-4 | Doble de prueba del generador que falla si se invoca sin respaldo. |
| RN-02 | Toda forma quechua de la salida es subcadena literal de un fragmento recuperado. | RF-06, salvaguarda | Comprobación de subcadena sobre la respuesta generada (o respuesta sin generador en PoC). |
| RN-03 | Ninguna respuesta se emite sin `documento` y `pagina`. | RF-07, DoD-3 | Validación de esquema de la respuesta. |
| RN-04 | τ se lee de configuración versionada; no existe como literal en el código. | C-4 | Búsqueda estática del literal + prueba de carga de configuración. |
| RN-05 | La traducción solo actúa sobre la consulta; nunca sobre el corpus ni sobre la forma quechua. Se recupera con la consulta original **y** con la traducida, conservando la mejor puntuación. | ADR-008 | Prueba de que la salida es idéntica en la forma quechua con y sin traductor. |
| RN-06 | Los modelos predictivos (RF-14, RF-15) **solo pueden añadir abstenciones**, nunca convertir una abstención de τ en respuesta. | Salvaguarda; ADR-014 | Prueba de monotonía: con predictor activo, el conjunto de respuestas es subconjunto del obtenido sin él. |
| RN-07 | Las métricas se reportan por partición (A, B, C, D, y la externa cuando exista); nunca solo un promedio global. | Documento 4, C-6 | El arnés falla si falta alguna partición. |
| RN-08 | Toda respuesta muestra la frase de alcance (ver `01_CONTEXTO_GENERAL.md` §1). | HU-06 escenario 2 | Prueba de presencia en la respuesta. |
| RN-09 | Los pasajes de prosa ofrecidos al abstenerse se rotulan «no es una respuesta», no van acompañados de ninguna afirmación y se cuentan como abstención. | ADR-022 | Prueba: una abstención con pasajes sigue siendo una abstención. |
| RN-10 | El índice del móvil es el del escritorio exportado; la puntuación de ambos motores coincide (diferencia < 1 × 10⁻⁶, top-5 idéntico). | ADR-019 | Validador de paridad sobre las 248 consultas. |

---

## 5. Requisitos de datos

| ID | Requisito | Criterio |
|---|---|---|
| RD-01 | Contrato del fragmento | Campos `id`, `documento`, `pagina`, `texto`, `tipo`, `procedencia` obligatorios. `id = md5("<archivo>\|<página>\|<índice>")[:12]`, compatible con el conjunto de evaluación de la PoC (ADR-018). Validación de esquema en la ingesta. `fragmentos_v2.jsonl` de la PoC no trae `procedencia`: la nueva ingesta la añade. |
| RD-02 | Manifiesto del corpus | `corpus/MANIFIESTO.yaml` (versionado) con, por documento: archivo, título, autoría, fuente, fecha de incorporación, licencia, tipo, páginas y SHA-256. Sin entrada, el documento no se ingiere (RNF-11); si la huella no coincide, se avisa. Los campos «por registrar» no bloquean la ingesta pero sí el Hito 1. |
| RD-03 | Registro de consultas para analítica | Necesario para RF-14…RF-16. Local, sin identificador de persona, sin marca de dispositivo. **Conflicto potencial con RNF-06**: se trata en ADR-013 antes del sprint 3. |
| RD-04 | Conjunto de evaluación externo | Consultas formuladas por docentes de EIB (tarea **humana**; los agentes no pueden fabricarlas). Sin formas quechuas redactadas por el equipo. Partición propia `E`. |
| RD-05 | Conjunto de referencia cultural | Consultas culturales con pasajes anotados para evaluar HU-04. Requiere criterio lingüístico humano. Si no se obtiene, HU-04 se declara no evaluada. |
| RD-06 | Artefactos de la prueba de concepto | En `referencia_poc/`: `datos/evaluacion_v2.json`, `datos/fragmentos_v2.jsonl` (fuera de Git), `scripts/` y `resultados/`. Se promueven a código de producción; no se rehacen ni se importan. |

---

## 6. Criterios de seguridad derivados

No figuran como requisitos en el Documento 0; se derivan de RNF-06 y RNF-07 para que el auditor tenga
criterios verificables. Su incorporación supone revisar la exclusión del análisis estático del
Documento 5 (ver ADR-010).

| ID | Criterio | Por qué |
|---|---|---|
| RS-01 | FastAPI escucha solo en `127.0.0.1`; sin CORS abierto. | La premisa del Documento 5 «sin servicios en red» es inexacta: el PMV1 expone un servicio HTTP local. |
| RS-02 | Validación de longitud y tipo de toda entrada (consulta 1–300 caracteres). | Evita abusos del servicio y de la ventana de contexto. |
| RS-03 | Sin telemetría: desactivar la de Vite/React, Ollama y cualquier dependencia que la tenga por defecto; la interfaz no carga recursos de terceros en ejecución. | RF-12, RNF-06. |
| RS-04 | Auditoría de dependencias en integración continua (`pip-audit`; avisos de GitHub). | Cadena de suministro. |
| RS-05 | Ningún secreto en el repositorio; los tokens de SonarQube y GitHub viven en variables de entorno o secretos de CI. | Buenas prácticas; escaneo de secretos activo. |
| RS-06 | El texto del corpus se trata como **dato**, no como instrucción, en la plantilla del generador. | Un fragmento podría contener texto que el modelo interprete como orden (inyección indirecta). |
| RS-07 | Los PDF del corpus y los pesos de modelos no se versionan en Git. | Licenciamiento (R-07) y tamaño. |
| RS-08 | El servidor MCP de desarrollo (ADR-017) solo expone herramientas de lectura, usa transporte `stdio` y no forma parte del producto ni de su paquete. | Los fragmentos que devuelve viajan a la API de Claude; el producto no puede depender de un servicio externo (RF-12). |

---

## 7. Restricciones

| Restricción | Consecuencia |
|---|---|
| Plazo de 12 semanas, inamovible | El alcance se ajusta repriorizando historias de prioridad S (E-04, E-05, E-09, E-11), no ampliando plazo. |
| Hardware: RTX 4060 8 GB, 32 GB RAM | Modelo de escritorio ≤ 4 B parámetros cuantizado; sin nube. |
| Sin presupuesto de pago | Solo herramientas libres o con plan gratuito (SonarQube Cloud gratuito: hasta 50 000 líneas privadas, solo rama principal y PR hacia ella; respaldo con el Community local). |
| Corpus con licencias heterogéneas | El repositorio no redistribuye los PDF. |

---

## 8. Matriz de trazabilidad

| Requisito | Historias | Criterio DoD | Condición PoC | Tipo de prueba principal |
|---|---|---|---|---|
| RF-01, RF-13, RNF-11, RNF-12 | HU-01 | DoD-1, DoD-7 | — | Unitaria + integración de ingesta |
| RF-02, RF-05 | HU-02 | DoD-1 | C-2, C-3 | Arnés A/B |
| RF-03, RF-06, RF-09, RF-11 | HU-03 | DoD-2, DoD-4 | C-2 | Aceptación Gherkin + arnés |
| RF-10 | HU-04 | DoD-2 | — | Arnés cultural (RD-05) |
| RF-04 | HU-05 | DoD-2 | C-1, C-4 | Arnés D + recalibración τ |
| RF-08 | HU-06 | **DoD-4** | C-4 | Arnés C (0 FP) + RN-01 |
| RF-07, RNF-08 | HU-07 | DoD-3 | — | Validación de esquema |
| RF-14, RF-15 | HU-08.1, HU-08.2 | DoD-4 | C-4 | Validación cruzada + RN-06 |
| RF-16 | HU-09 | DoD-2 | — | Unitaria con historial sintético de prueba (solo para probar el código, nunca para reportar resultados) |
| RNF-03, RNF-04, RNF-05, RNF-02 | HU-10.1…10.3 | DoD-5, DoD-6 | C-5 | Medición en dispositivo |
| RNF-09 | HU-11 | — | — | Prueba con usuarios |
| RF-12, RNF-06 | todas | DoD-5 | — | Prueba con red bloqueada + auditoría |
| RNF-07 | todas | DoD-8 | — | Prueba de arquitectura + SonarQube |

---

## 9. Registro de cambios

| Fecha | Versión | Cambio | Decisión |
|---|---|---|---|
| 2026-09-24 | 1.0 | Creación a partir de los Documentos 0, 4, 5 y 6 | — |
| 2026-09-24 | 1.1 | Identificador de fragmento (RD-01, RF-13), manifiesto del corpus (RD-02), rutas de la PoC (RD-06), RS-08 | ADR-015, 017, 018 |
