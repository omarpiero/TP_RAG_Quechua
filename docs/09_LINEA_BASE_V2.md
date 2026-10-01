# 09 · Línea base v2 — especificación revisada por medición

> **Qué es.** Resumen operativo de la **revisión 2 de los Documentos 0–6**, preparada por el equipo tras
> construir y medir el sistema (84 cambios, marcados en azul oscuro en cada `.docx`, más el anexo
> «Documento 5 — Corrección por medición»). Adoptada como línea base el 2026-09-24.
>
> **Jerarquía.** Donde este archivo contradiga a `docs/01…07` o a la versión 1 de la serie, **manda este
> archivo** hasta que el archivista propague los cambios (tarea HT-00b). Los criterios Gherkin afectados se
> actualizan con su ADR (`07_DECISIONES.md`, ADR-019 a ADR-027).
>
> **Regla de lectura.** Las tablas comparativas de la versión 1 se conservan en los documentos a propósito:
> muestran cómo se decidió con la información de entonces. Lo que cambia es la **decisión vigente**.

---

## 1. El sistema tal como es (decisiones vigentes)

| Tema | Versión 1 (plan) | **Vigente (v2)** | Evidencia | ADR |
|---|---|---|---|---|
| Recuperación | Semántica densa (bge-m3 / E5) sobre almacén vectorial | **Léxica híbrida**: coseno sobre TF-IDF de palabras completas y de n-gramas de caracteres 3–5, **promediados**; depuración del fraseo constante; capa de **coincidencia de lema** para entradas lexicográficas | PoC: denso recall@5 0,650 frente a 1,000; similitudes densas comprimidas | ADR-005 (ya aceptado) |
| Almacén | ChromaDB (escritorio) · sqlite-vec (móvil) | **Ninguna base vectorial.** Índice léxico persistente en escritorio; en móvil, **índice exportado** en binario plano por columnas (índice invertido) | No hay vectores densos que almacenar | ADR-019 |
| Umbral τ | 0,41 (PoC) | **0,48** en la implementación (formulación exacta del híbrido): 0 FP, 92,8 % de consultas atendibles. El Documento 6 conserva 0,41 como resultado de la PoC y añade una nota | Barrido sobre 248 consultas | ADR-020 |
| Coincidencia de lema | No existía | Si el término depurado es **exactamente** el lema de una entrada del diccionario, esa entrada cuenta como respaldo documental **aunque el coseno quede bajo τ** | Auditoría: 0 FP en C con la regla activa | ADR-021 (**a formalizar**) |
| Prosa | Responder o abstenerse | Tercer caso (RF-08): ante material de prosa **no se afirma nada**; se entregan los pasajes literales y citados si comparten ≥ 2 palabras de contenido con la consulta depurada. Cuenta como **abstención** | 60 preguntas de prosa + 135 negativas: 0 FP fuera de cobertura (conjunto sintético) | ADR-022 |
| Consulta en inglés | Traducir con el SLM en tiempo de consulta | **Tabla EN→ES** de los 2 257 lemas del corpus, generada con el SLM **en tiempo de compilación**; se muestran **todas** las lecturas | Funciona sin modelo (necesario en el móvil). Límite: hereda errores del modelo que la generó (`boiled corn → huayco`) y D es un **techo** por construcción | ADR-023 |
| OCR | Tesseract en la ingesta | **No se incorpora.** Las páginas sin capa de texto se **señalan**; se añade un **reparador de acentos** separados por la extracción (70,6 % de los fragmentos de prosa) | 88,4 % de páginas con texto; OCR aportaría el 0,45 % del corpus (PoC) | ADR-024 |
| Interfaz | Streamlit | **React + Vite** sobre la API FastAPI («aplicación web sobre servicio de escritorio») | La asignatura evalúa la integración front-end ↔ back-end | ADR-025 |
| Generación en escritorio | Qwen3.5-4B vía Ollama | **Sin cambio.** Qwen3.5-4B vía Ollama, instrucción restrictiva | Correcto en los 5 casos de fidelidad | — |
| Generación en móvil | Qwen3.5-0.8B cuantizado (llama.cpp) | **Ningún modelo en el dispositivo.** Respuesta compuesta con **plantilla determinista** sobre la entrada extraída por un analizador determinista | 0,8B afirmó que *ashuti* significa «uña»; 2B falló 2 de 5 casos; 4B, 5 de 5. El extractor acierta 180/180 en A+B y cubre el 90,2 % de los fragmentos lexicográficos | ADR-026 (**revisión abierta**, §4) |
| Persistencia | No especificada; RF-11 «historial de sesión» | Historial tras un **puerto Repository**; escritorio con gestor relacional, móvil con **SQLite** | Anexo del Doc. 5, tabla E | ADR-027 (**propuesta**, §3) |
| Paquete móvil | ≤ 1,2 GB (con codificador) | ≤ 1,2 GB como techo; **medido 21,5 MB** (índice exportado 11,85 MB) | Artefacto ARM64 | — |
| PMV2 | Analítica + cuantización + exportación del codificador | **Analítica predictiva RF-14–16 (pendiente)** + exportación del índice y **verificación de paridad** (hecha) | Paridad: diferencia máx. 2,5 × 10⁻⁸ en 248 consultas; top-5 idéntico | — |
| PMV3 | App con SLM cuantizado | App Flutter con índice exportado, tabla EN→ES y compositor determinista. **Adelantada; no validada en dispositivo físico** (latencias solo de emulador) | Doc. 5, tabla F | — |
| Riesgo R-06 | Degradación por cuantización | «El modelo que cabe en el dispositivo no lee la entrada con fidelidad» — **materializado** | Tabla B del anexo | — |

---

## 2. Correcciones pendientes en la propia revisión 2 (antes de la entrega)

La revisión 2 es mejor que la versión 1, pero todavía tiene estas inconsistencias. El archivista las anota;
las corrige el equipo en los `.docx`.

| # | Documento | Problema | Corrección propuesta |
|---|---|---|---|
| L-1 | Doc. 0, §RF | Afirma que RF-01 a RF-13 están «implementados y **verificados**». RF-10 (cultural) no tiene conjunto de referencia (RD-05) y RF-04 se midió con consultas derivadas de los mismos lemas que la tabla | «Implementados; verificados sobre el conjunto de evaluación salvo RF-10 (sin conjunto de referencia) y RF-04 (resultado techo)» |
| L-2 | Doc. 0 | Aún dice «cuantización del modelo» en la descripción del PMV2 y del nodo de compilación, y «similitud semántica» en HU-02 | Sustituir por «exportación del índice y verificación de paridad» y «similitud léxica» |
| L-3 | Doc. 4 | Quedan 4 menciones a «recuperación **semántica**» en el PMV1, E-03…E-05 y el plan de sprints | «recuperación léxica híbrida» |
| L-4 | Doc. 1 | Su registro de riesgos mantiene R-06 como «cuantización agresiva» mientras el Doc. 4 lo redefine | Alinear R-06 en ambos o anotar en el Doc. 1 la redefinición |
| L-5 | Doc. 2 | Sigue justificando un modelo «cuantizado a 4 bits» en escritorio y el motor móvil por formato cuantizado; el resumen del equipo dice «no se cuantizó ningún modelo» | El modelo de Ollama **se distribuye cuantizado** (verificar con `ollama show qwen3.5:4b`, campo *quantization*). Precisar: «no se cuantizó ningún modelo **para el móvil**»; retirar la justificación del motor móvil |
| L-6 | Resumen del equipo frente a Doc. 2 | Paridad «2,5 diezmillonésimas» (2,5 × 10⁻⁷) en el resumen; «2,5 × 10⁻⁸» en el Doc. 2 y en el anexo | Unificar con la salida de `scripts/validar_indice_movil.py` |
| L-7 | Anexo Doc. 5 | Generaliza un «techo entre 2 000 y 4 000 millones de parámetros» a partir de **5 casos × 4 modelos** | Mantener la decisión (el fallo de *ashuti* basta para retirar el 0,8B) y declarar el tamaño de la muestra como limitación; ampliar la prueba de fidelidad si se reabre ADR-026 |
| L-8 | Doc. 0, RF-08 | No menciona la **coincidencia de lema** que responde bajo τ (sí figura en el anexo del Doc. 5) | Añadirla a RF-08 como segunda vía de respaldo (ADR-021) |
| L-9 | Doc. 0, RF-11 y RNF-06 | El historial se persiste; RNF-06 prohíbe recolectar datos personales y una consulta libre puede contenerlos | Aviso en la interfaz, sin identificadores, opción de borrar el historial (ADR-013 y ADR-027) |

---

## 3. Persistencia (ADR-027, propuesta)

- **Una sola tecnología en los tres PMV: SQLite**, tras el puerto `RepositorioConsultasPort` (patrón
  Repository).
  - PMV1 (escritorio): historial y registro anónimo de consultas en un archivo SQLite local. No requiere
    instalar un servidor: la demo corre en cualquier PC.
  - PMV2: el mismo archivo es el conjunto de datos de RF-14–16 (sin servidor, sin exportaciones).
  - PMV3 (móvil): SQLite para el historial del dispositivo.
- **El índice no va en SQLite**: en escritorio es el índice léxico; en móvil, los binarios exportados.
- **PostgreSQL** queda como **segundo adaptador** del mismo puerto (el código base ya lo tiene). Sirve de
  evidencia del patrón Repository («dos implementaciones, un puerto») y es opcional en la demo.

## 4. Modelo en el teléfono (ADR-026, revisión abierta)

- **Vigente:** sin modelo; plantilla determinista. Cumple RNF-04 (gama media, 4 GB) y no puede alterar
  formas quechuas.
- **Evidencia disponible:** solo Qwen3.5-4B leyó fielmente los 5 casos; es el mismo modelo del escritorio
  (`ollama ps`: 3,1 GB en memoria).
- **Opción a evaluar en el sprint del PMV3, no ahora:** un «modo enriquecido» **opcional** con un modelo de
  4B en dispositivos que lo soporten (p. ej. el de prueba del equipo, POCO F8 Pro: Snapdragon 8 Elite,
  12 GB), que **solo redacta** a partir de la entrada ya extraída, con el mismo verificador de forma
  literal y caída a la plantilla en gama media. Condiciones para aceptarlo: prueba de fidelidad ampliada
  (≥ 60 casos) sin alteraciones, latencia medida en el dispositivo y descarga separada del modelo (no cabe
  en el límite de 1,2 GB de RNF-05). No aumenta la precisión de la forma quechua —que la da la extracción
  (180/180)—, solo la fluidez.

## 5. Lo que la línea base v2 exige al PMV1 que se entrega

1. Estructura hexagonal en 4 capas con **puertos de entrada** (rúbrica E2) — sin cambios respecto de
   `CONSIDERACIONES.md` §4.
2. Reglas de respuesta explícitas y probadas: τ desde configuración (0,48 hasta nueva calibración),
   **regla de lema** (ADR-021) y **pasajes de prosa** (ADR-022), cada una con prueba `@salvaguarda` y
   0 FP en C.
3. Interfaz React **endurecida** (`CONSIDERACIONES.md` §5, PR 7).
4. Corrección de las entradas lexicográficas truncadas (p. ej. «SOL: Inti. (rayo de sol) Intip shaplan.
   (época de»).
5. Mediciones M1–M15 (`CONSIDERACIONES.md` §8), que además **verifican** las cifras nuevas de la revisión 2.
