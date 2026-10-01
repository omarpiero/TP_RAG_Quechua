# 01 · Contexto general del proyecto

> **Documento de contexto para todos los agentes.** Resume lo que las siete entregas de la serie
> documental (Documentos 0 a 6) establecieron y que condiciona el desarrollo. Si algo de este archivo
> contradice a un documento fuente, manda el documento fuente y el archivista corrige este resumen.
>
> Mantenido por: **archivista** · Última revisión: 2026-09-24 · Versión 1.1

---

## 1. Qué es el sistema, en una frase

Un **asistente de consulta documental** sobre quechua wanka de Junín: la persona pregunta en español o
inglés, el sistema recupera el fragmento pertinente de un corpus de documentos oficiales y responde
mostrando la forma en quechua **tal como aparece en el fragmento**, junto con el fragmento original, el
documento y la página de origen. Cuando el corpus no respalda la consulta, **lo declara y no genera
ninguna forma lingüística**.

**Objetivo general (Documento 4, §4.2.1).** Desarrollar un prototipo de asistente de consulta documental
del quechua wanka basado en un modelo de lenguaje pequeño con generación aumentada por recuperación, que
responda consultas en español o inglés mostrando el término o la expresión en quechua junto con el
fragmento y el documento de origen, que declare explícitamente la ausencia de información cuando el
corpus no la respalde, y que opere en hardware local y, en su fase final, en un dispositivo móvil sin
conexión.

### Lo que el sistema **no** es

| No es | Por qué importa al construir |
|---|---|
| Un traductor | Nunca produce una forma quechua que no esté literalmente en un fragmento recuperado. |
| Una autoridad lingüística | No sustituye la validación por hablantes de la comunidad ni el servicio estatal de interpretación. |
| Un chatbot general | Fuera del corpus se abstiene; no conversa sobre otros temas. |
| Un sistema con voz | La interacción es exclusivamente textual; la voz queda como trabajo futuro. |

**Frase de alcance obligatoria** (debe figurar en la interfaz y en toda documentación de alcance):
*«Herramienta de consulta sobre fuentes ya publicadas y validadas. No sustituye la validación por
hablantes de la comunidad ni se constituye en autoridad lingüística sobre la variedad wanka.»*

---

## 2. El problema (Documentos 1 y 3)

- El quechua wanka está clasificado como **«seriamente en peligro»** por el Ministerio de Cultura (BDPI)
  y como «severamente amenazado» en Glottolog. La transmisión intergeneracional cae en la cohorte de 0 a
  10 años (VIGIL OLIVEROS, 2023).
- La Línea 1812 de interpretación del Ministerio de Cultura cubre tres variedades de quechua (Áncash,
  chanka, Cusco-Collao): **el wanka no está incluido**.
- Existe material publicado (diccionarios, gramáticas, materiales de EIB), pero está **disperso en PDF**
  y no es recuperable con eficacia. El Documento 1 identificó seis puntos de falla en el proceso actual:

| Código | Punto de falla | Qué lo resuelve en el sistema |
|---|---|---|
| F1 | Dispersión documental | Corpus único indexado (RF-01, RF-02) |
| F2 | Búsqueda literal en lugar de semántica | Recuperación por similitud (RF-05) |
| F3 | Documentos sin capa de texto | OCR como higiene de ingesta (RF-01) |
| F4 | Variación ortográfica no normalizada | Normalización + n-gramas de caracteres (RF-05, R-04) |
| F5 | Pérdida de trazabilidad | Documento y página obligatorios (RF-07) |
| F6 | Sustitución por fuentes no específicas | Abstención explícita (RF-08) |

**Riesgo ético central.** En una lengua seriamente en peligro, una respuesta inventada no es un simple
error: **contamina el registro documental** de la lengua que se pretende preservar, porque puede ser
citada y reutilizada sin rastro de su origen. De ahí la salvaguarda (§5).

---

## 3. Personas usuarias e interesados

**Beneficiarios directos:** docentes y estudiantes de Educación Intercultural Bilingüe (EIB) del valle
del Mantaro e investigadores en lingüística andina y PLN. **Beneficiarias indirectas:** las comunidades
quechuahablantes (titulares del patrimonio lingüístico).

| ID | Interesado | Nota para el desarrollo |
|---|---|---|
| I-01 | Comunidades quechuahablantes del valle del Mantaro | Interés muy alto, influencia baja: principal hallazgo ético. Comunicación **pendiente de establecer**. |
| I-02 | Docentes de EIB | Deben aportar las consultas del conjunto externo de evaluación (tarea humana, sprint 1). |
| I-03 | Estudiantes de EIB | Usuarios de HU-03, HU-11. |
| I-04 | Investigadores en lingüística andina y PLN | Usuarios de HU-04. |
| I-05 | Dirección Desconcentrada de Cultura de Junín | Posible fuente de corpus y validación institucional. |
| I-06 | Unidades de gestión educativa local | Canal de acceso a docentes. |
| I-07 | Universidad Continental y docente del curso | Evaluación de los hitos. |
| I-08 | Equipo de proyecto | Humanos que aprueban decisiones y fusiones. |
| I-09 | Ministerio de Cultura | Fuente normativa y documental. |

**Delimitaciones comprometidas que ningún artefacto puede contradecir:** no sustituye al servicio estatal
de interpretación; no constituye autoridad lingüística; no cuenta con validación por hablantes; la
modalidad textual excluye a personas no alfabetizadas y con discapacidad visual total; no existe modelo
de sostenibilidad más allá del periodo académico.

---

## 4. Las tres decisiones de diseño que atraviesan todo

1. **RAG en lugar de ajuste fino.** No hay corpus de entrenamiento suficiente para la variedad wanka y,
   en RAG, el conocimiento lingüístico viene del contexto recuperado, no de los pesos del modelo
   (SOUDANI, KANOULAS y HASIBI, 2024).
2. **Modelo de lenguaje pequeño en lugar de modelo grande cuantizado.** El generador solo interpreta el
   fragmento y redacta; un modelo compacto cumple ese papel con menos memoria de video.
3. **Arquitectura hexagonal (puertos y adaptadores).** Elegida por factores ponderados (4,65 frente a
   2,80 de microservicios y 3,10 orientada a eventos) porque el paso de escritorio a móvil sustituye
   motor de inferencia, base vectorial e interfaz: bajo esta arquitectura eso solo afecta a adaptadores.

---

## 5. La salvaguarda central y las reglas que no se negocian

```
si similitud(mejor_fragmento) >= τ:   responder citando documento y página
si no:                                declarar ausencia de información
                                      y NO generar ninguna forma lingüística
```

1. **Ninguna forma quechua se redacta, se completa ni se corrige.** Todas salen literales del fragmento
   recuperado y con su fuente.
2. **Ninguna respuesta sin documento y página.**
3. **El umbral τ se fija por ausencia de falsos positivos**, nunca por la métrica que da mejor cifra.
   τ es un parámetro versionado en configuración, no una constante del código.
4. **Las particiones de evaluación se reportan por separado**; un promedio global oculta que una falla.
5. **Nunca inventar cifras**: lo que no se midió se declara «por medir».
6. **Un resultado negativo se reporta igual que uno positivo.**
7. **DoD-4 (salvaguarda de abstención) se verifica en todos los incrementos, sin excepción.**

---

## 6. Arquitectura

### 6.1 Núcleo de dominio (no cambia entre plataformas)

Normalización y depuración de la consulta · política de recuperación · regla de abstención · composición
de la respuesta · trazabilidad. **Si un cambio de fase obliga a tocar el núcleo, la separación se rompió.**
El núcleo no importa ninguna biblioteca de terceros.

### 6.2 Puertos y adaptadores (línea base v2)

> Actualizado a la revisión 2 de los Documentos 0–6 (`09_LINEA_BASE_V2.md`). Los nombres de puertos de la
> estructura objetivo están en `CONSIDERACIONES.md` §4.

| Puerto | Responsabilidad | Adaptador escritorio (PMV1) | Adaptador móvil (PMV3) |
|---|---|---|---|
| `ExtraccionDocumentalPort` | PDF → texto por página con procedencia; señala páginas sin texto; repara acentos | pypdf + reparador | no se ejecuta en el móvil |
| `IndiceRecuperacionPort` | Recuperar por similitud léxica (+ coincidencia de lema) | `IndiceHibridoLexico` (scikit-learn) | Motor Dart sobre el **índice exportado** (paridad verificada) |
| `GeneradorTextoPort` | Fragmento → respuesta redactada | Qwen3.5-4B vía Ollama | **Plantilla determinista** (sin modelo, ADR-026) |
| `TraductorPort` | Consulta EN → ES antes de recuperar | Tabla de lemas (tiempo de compilación); Ollama como alternativa | Tabla de lemas |
| `DetectorIdiomaPort` | Español, inglés u otro | Heurístico | Heurístico |
| `Repositorio{Consultas,Fuentes,Corpus}Port` | Historial, fuentes, fragmentos | SQLite (propuesta ADR-027; PostgreSQL alternativo) · manifiesto · JSONL | SQLite (historial) · recursos de la app |
| `PrediccionPort` | RF-14 a RF-16 | scikit-learn (PMV2, pendiente) | — |

**Adaptadores de entrada:** API FastAPI solo en `127.0.0.1`, consumida por la **interfaz React + Vite**
(ADR-025); CLI; servidor MCP de solo lectura para el desarrollo (ADR-017); app Flutter (PMV3).

### 6.3 Fases (PMV) — estado según la revisión 2

| PMV | Semanas | Pregunta que responde | Contenido vigente | Estado |
|---|---|---|---|---|
| PMV1 | S1–S6 | ¿Funciona la consulta con trazabilidad y abstención? | Aplicación web (React) sobre servicio de escritorio (FastAPI), recuperación léxica, Qwen3.5-4B, abstención | Base funcional hecha; se reorganiza y endurece para la entrega (`CONSIDERACIONES.md`) |
| PMV2 | S7–S9 | ¿Genera valor la analítica y se puede llevar el índice al teléfono? | RF-14–16 · exportación del índice · verificación de paridad | Analítica **pendiente**; exportación y paridad hechas |
| PMV3 | S10–S12 | ¿Opera de forma autónoma en un dispositivo de gama media? | App Flutter con índice exportado, tabla EN→ES y compositor determinista | **Adelantada como espiga**; falta validación en dispositivo físico |

---

## 7. Stack tecnológico vigente (Documento 5 + anexo «Corrección por medición»)

| Capa | Escritorio (PMV1–PMV2) | Móvil (PMV3) |
|---|---|---|
| Lenguaje | Python 3.12 | Dart (Flutter) |
| Modelo generador | **Qwen3.5-4B** sobre **Ollama** (corre en GPU; verificado también en CPU: `ollama ps` 100% CPU, 3,1 GB) | **Ninguno** — plantilla determinista (ADR-026) |
| Recuperación | Híbrido léxico TF-IDF + capa de lema | Mismo índice, exportado a binario plano por columnas |
| Almacén | Índice léxico persistente (sin base vectorial) | Recursos de la app (11,85 MB) |
| Persistencia | SQLite (propuesta) / PostgreSQL | SQLite |
| Servicio y UI | FastAPI + **React + Vite** | Flutter |
| Analítica | scikit-learn (pendiente) | — |
| Pruebas | pytest + arnés propio; Vitest para la UI | flutter_test (+ `paridad_test.dart`) |
| Calidad | SonarQube Cloud en CI + Community local · `ruff`, `pytest-cov`, `pip-audit` | SonarQube (Dart) |

Retirados por medición: ChromaDB, sqlite-vec, bge-m3, multilingual-E5, cuantización GGUF para el móvil,
llama.cpp, Qwen3.5-0.8B, Tesseract, Streamlit.

**Hardware de desarrollo:** PC x86-64, 32 GB de RAM, NVIDIA RTX 4060 con 8 GB de VRAM. Dispositivo móvil
de prueba del equipo: POCO F8 Pro (gama alta; no representa el mínimo de RNF-04).

---

## 8. Lo que ya está medido (Documento 6 y cuaderno integral)

Estos valores son **mediciones reales**, no estimaciones. Son el punto de partida del desarrollo y deben
volver a medirse cuando cambie el corpus, la segmentación, el codificador o el tratamiento de la consulta.

### 8.1 Corpus

| Magnitud | Valor |
|---|---|
| Documentos | 8 |
| Páginas / con capa de texto | 679 / 600 (88,4 %) |
| Caracteres extraídos | 687 622 (683 968 en fragmentos) |
| Fragmentos indexados | 3 605 (2 470 lexicográficos · 1 135 de prosa) |
| Aporte de la gramática de Cerrón-Palomino | 63 % del texto |
| Aporte de los tres materiales visuales | 4,1 % del texto |
| Ganancia proyectada del OCR sobre las 79 páginas sin texto | ≈ 3 100 caracteres (0,45 %) |

### 8.2 Conjunto de evaluación (248 consultas)

| Partición | n | Qué mide |
|---|---:|---|
| A · léxico en español | 120 | Recuperación en la condición más favorable |
| B · fraseo independiente | 60 | Sensibilidad al fraseo |
| D · consultas en inglés | 40 | RF-04 |
| C · fuera de cobertura | 28 | RF-08, la abstención |

Derivadas automáticamente de 2 272 entradas del diccionario: **ninguna forma quechua fue redactada por
el equipo**. Las cifras de A, B y D son el **techo** del desempeño, no su valor en uso real.

### 8.3 Resultados que fijan parámetros

| Resultado | Valor | Consecuencia |
|---|---|---|
| Híbrido léxico: recall@5 en A / B / D | 1,000 / 1,000 / 0,175 | Línea base del PMV1 |
| Híbrido léxico: latencia | 5,2 ms sobre 3 605 fragmentos | RNF-02 holgado |
| **Umbral τ sin falsos positivos** | **0,41** → 0 FP · 28/28 abstenciones · recall 0,856 · F1 0,922 | Resultado de la PoC; la implementación recalibró a **0,48** (ADR-020) |
| Punto de mayor F1 (descartado) | τ 0,25 · F1 0,994 · **1 FP** | Prueba de que F1 no elige el umbral |
| Separación de similitudes léxica | 0,517 con respaldo vs. 0,114 sin respaldo | La abstención es implementable |
| E5-small denso: recall@5 A / B / D | 0,650 / 0,650 / 0,275 · separación 0,024 · τ 0,87 retiene 30 % | Complemento, no sustituto |
| E5-base denso: recall@5 A / B / D | 0,600 / 0,600 / **0,275** · separación 0,009 · τ 0,84 retiene 26,7 % | Agrandar el codificador no resuelve |
| Segmentación uniforme 650 car. (ablación) | recall en τ: 48,3 % (ingesta real) · 34,4 % (reconstrucción) | Segmentar por tipo documental es obligatorio |
| Consulta sin depurar | τ utilizable 0,23 · recall 76,7 % | La depuración es obligatoria |
| **Traducción EN→ES previa (subconjunto D)** | recall@5 0,175 → **0,875** · similitud media 0,383 · **solo 20/40 superan τ** | Resuelve la recuperación; falta recalibrar τ |

### 8.4 Decisión de la prueba de concepto: **GO CON CONDICIONES**

| Condición | Qué exige al desarrollo |
|---|---|
| C-1 Multilingüismo | Traducir la consulta EN→ES antes de recuperar y recalibrar τ antes de declarar RF-04 cumplido. |
| C-2 Estrategia | Híbrido léxico como línea base; lo denso solo como complemento medido. |
| C-3 Segmentación | Una entrada por fragmento en material lexicográfico; `tipo` como campo obligatorio. |
| C-4 Umbral | τ por cero FP, versionado, recalibrado con el arnés ante cualquier cambio. |
| C-5 Codificador denso | Si se usa en móvil, abstención por margen primer–segundo resultado o calibración explícita. |
| C-6 Evaluación | Incorporar consultas de docentes de EIB y reportarlas por separado. |

---

### 8.5 Mediciones de la implementación (revisión 2; a verificar con `CONSIDERACIONES.md` §8)

| Medición | Valor declarado | Fuente |
|---|---|---|
| Primer τ sin FP con la formulación exacta | 0,48 · 92,8 % de consultas atendibles | Doc. 6 rev. 2; auditoría |
| Paridad escritorio ↔ móvil | Diferencia máx. 2,5 × 10⁻⁸ en 248 consultas; top-5 idéntico | Anexo Doc. 5, tabla D |
| Extractor determinista | 180/180 en A+B; cubre el 90,2 % de los fragmentos lexicográficos | Anexo Doc. 5 |
| Paquete móvil ARM64 | 21,5 MB (índice exportado 11,85 MB) | Docs. 0 y 3 rev. 2 |
| Prosa legible | 723 de 1 135 fragmentos | Anexo Doc. 5, tabla F |
| Acentos separados en prosa | 70,6 % de los fragmentos | Doc. 0 rev. 2, RF-01 |
| Fidelidad de lectura por modelo | 4B: 5/5 · 2B: 3/5 · 0,8B y Gemma 3 1B: fallos graves | Anexo Doc. 5, tabla B (5 casos) |
| Latencia en móvil | Solo emulador; **no** cuenta como cumplimiento | Anexo Doc. 5, tabla F |

---

## 9. Contrato de datos del índice

Un objeto JSON por fragmento (JSONL). **Campos obligatorios:**

```json
{"id":"35d5d6d6b8a4","documento":"293274822-diccionario-quechua-Wanka-docx.pdf","pagina":37,
 "texto":"ZORRO: Atuq.","tipo":"lexicografico","procedencia":"capa de texto"}
```

- `documento` y `pagina` **nunca nulos** (RF-07, DoD-3).
- `tipo` ∈ {`lexicografico`, `prosa`} y **determina la segmentación**.
- `procedencia` ∈ {`capa de texto`, `reconocimiento óptico`}; el segundo se advierte en la interfaz (R-03).
- El índice se reconstruye **con un único proceso ejecutable** (DoD-1).
- `id = md5("<archivo>|<página>|<índice>")[:12]`, compatible con el conjunto de evaluación de la PoC
  (ADR-018). Por eso los nombres de archivo de `corpus/pdf/` no se cambian.

Ejemplos verificados en el corpus (útiles para pruebas, **no inventar otros**):

| Consulta | Fragmento literal | Documento · página | Nota |
|---|---|---|---|
| zorro | `ZORRO: Atuq.` | diccionario wanka · 37 | S = 0,559 → responde |
| cóncavo | `CÓNCAVO: Puklu.` | diccionario wanka · 9 | subconjunto A |
| confesar | `CONFESAR: Kunfisay.` | diccionario wanka · 9 | subconjunto A |
| agua | `AGUA: Yaku. (agua clara) Chuyaq yaku. …` | diccionario wanka · 2 | entrada con subentradas |
| casa | `CASA: Wasi.CASADO: Walmiyuq.` | diccionario wanka · 7 | **falso negativo conocido**: dos entradas fusionadas por la extracción |
| criptomoneda | — | — | S = 0,055 → se abstiene |

---

## 10. Riesgos que el desarrollo debe vigilar

| ID | Riesgo | Puntaje · estrategia | Estado tras la PoC |
|---|---|---|---|
| R-01 | Corpus insuficiente | 20 · mitigar | No se materializó en su forma severa |
| R-02 | Formas no documentadas | 15 · evitar | Controlado por la abstención |
| R-03 | OCR con errores | 16 · mitigar | Advertencia en interfaz + muestreo |
| R-04 | Variación ortográfica | 12 · mitigar | n-gramas de caracteres |
| R-05 | Evaluación sesgada por el propio corpus | 10 · mitigar | **Vigente**: faltan consultas externas (C-6) |
| R-06 | El modelo que cabe en el dispositivo no lee la entrada con fidelidad (redefinido en v2) | 9 · aceptar | **Materializado**: sin modelo en el móvil (ADR-026) |
| R-07 | Licenciamiento del corpus | 6 · mitigar | Los PDF **no** se versionan en el repositorio |
| R-08 | Dispositivo de prueba insuficiente | 4 · aceptar | Por verificar en PMV3 |
| R-09 a R-16 | Riesgos de impacto (Documento 3): sesgo dialectal, apropiación del patrimonio, sustitución del aprendizaje, exposición de la consulta, discontinuidad, consumo energético, exclusión por modalidad textual, uso en contextos sensibles | — | Guían decisiones de interfaz y datos |

---

## 11. Marco normativo que afecta al código

| Norma | Consecuencia técnica |
|---|---|
| Ley N.º 29733 y D. S. 016-2024-JUS (datos personales) | No recolectar datos personales; ninguna consulta sale del equipo (RNF-06). |
| Ley N.º 31814 y D. S. 115-2025-PCM (IA) | El sistema es de **riesgo aceptable**; queda sujeto a transparencia algorítmica, que se satisface con la trazabilidad. |
| Principios CARE (RDA/GIDA) | Registro de procedencia, fecha y licencia de cada fuente (RNF-11, DoD-7). |
| Ley N.º 29735 y D. S. 012-2021-MC | Marco de lenguas originarias; fundamenta el propósito. |
| WCAG 2.1 | Tipografía ampliable, tres interacciones (RNF-09, HU-11). |

---

## 12. Glosario

| Término | Significado en este proyecto |
|---|---|
| Fragmento | Unidad indexada del corpus, con documento y página. |
| Representación vectorial | Vector que codifica un texto (no usar *embedding* en documentación formal). |
| τ (umbral de abstención) | Similitud mínima del mejor fragmento para responder. Escalar entre 0 y 1; **no es una probabilidad**. |
| Falso positivo (FP) | Consulta sin respaldo que recibe respuesta. **El único error irreversible.** |
| Depuración de la consulta | Eliminar el fraseo constante («cómo se dice», «en quechua wanka», «how do you say»). |
| Arnés de evaluación | Script que ejecuta las cuatro particiones y reporta recall@1, recall@5, MRR@10 y matriz de confusión. |
| Particiones A/B/C/D | Subconjuntos del conjunto de evaluación (ver §8.2). |
| PMV | Producto mínimo viable; hay tres. |
| SDD | Desarrollo guiado por especificaciones: especificar → planificar → tareas → implementar. |

---

## 13. Mapa de documentos fuente

| Documento | Qué aporta al desarrollo | Dónde se refleja aquí |
|---|---|---|
| 0 · Lineamientos | RF-01…16, RNF-01…12, épicas E-01…E-11, HU-01…HU-11 con criterios Given/When/Then, arquitectura | `02_REQUERIMIENTOS`, `03_HISTORIAS_USUARIO` |
| 1 · Análisis del problema | Puntos de falla F1–F6, riesgos R-01…R-08 | §2, §10 |
| 2 · Conocimientos de ingeniería | Fundamento del umbral, tokenización, métricas | §5, §8 |
| 3 · El ingeniero y la sociedad | Interesados I-01…I-09, riesgos R-09…R-16, marco normativo | §3, §10, §11 |
| 4 · Gestión del proyecto | Scrum, 4 sprints, DoD-1…10, hitos, tablero de control | `04_SPRINTS`, `05_KANBAN` |
| 5 · Herramientas modernas | Modelos, motores, almacenes, sustituciones previstas | §7 |
| 6 · Prueba de concepto | Parámetros medidos, condiciones C-1…C-6 | §8, `07_DECISIONES` |

Los `.docx` originales están en `TallerProyectos/docs_idea2/`. Dentro de este proyecto: el corpus en
`corpus/pdf/` (fuera de Git) con su `corpus/MANIFIESTO.yaml`, y los artefactos de la prueba de concepto en
`referencia_poc/`.
