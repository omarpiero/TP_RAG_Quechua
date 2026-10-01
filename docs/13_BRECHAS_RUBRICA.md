# 13 · Brechas frente a la rúbrica y ajustes al plan de cierre

> **Revisión del 2026-10-01**, hecha por el asistente documental sobre el repositorio en la PC con la RTX 4060.
> Se contrastó contra:
> - la consigna (S6);
> - la trazabilidad integradora (S6), apartado B de cada competencia;
> - la lista de cotejo (S7);
> - la rúbrica de exposición (S8).
>
> **Para quién.** El orquestador de Claude Code, que integra esto en el plan (`PROMPT_CIERRE_PMV1.md` §5), y el
> equipo, en las tareas marcadas «equipo».
>
> **Regla.** Lo que figura aquí **completa** a `CONSIDERACIONES.md` y a `docs/11`–`12`; no los contradice. Donde
> eleva una prioridad, manda este archivo.

---

## 1. Estado verificado del repositorio

| Punto | Estado | Comentario |
|---|---|---|
| Pasos 1–3 del prompt (entorno, pruebas, línea base congelada) | **Hecho y correcto** | `docs/evidencias/2026-10-01_base-integrante_pc-rtx4060/`: 40/40 pruebas, arnés de 248 consultas, barrido con y sin lema, metadatos completos |
| Cuantización del modelo | **Medida: Q4_K_M** | Resuelve L-5 de `docs/09`: el modelo de escritorio **sí** está cuantizado (lo distribuye así Ollama). Corregir la frase «no se cuantizó ningún modelo» en el Doc. 2 |
| Paso 4 (preguntas al usuario) | En curso | ADR-021: ver §3 |
| Código de producción | Sin cambios todavía | Correcto: el prompt pide no programar antes de las respuestas |
| **Historial divergente** | **Atención** | `main` local (13dbafb) y `origin/main` (066ec23) tienen los mismos tres commits de HT-00 con autores distintos (`omarpiero` local, `NeidanShinjou` remoto). La rama `respaldo-antes-reescritura` apunta al remoto. Ver §1.1 |
| Fin de línea | Menor | En una vista sin `autocrlf`, 149 archivos aparecen «modificados» solo por CRLF (`git diff --ignore-cr-at-eol` sale vacío). Añadir `.gitattributes` con `* text=auto` en el PR 1 para que no dependa de la configuración de cada PC |

### 1.1 Historial: decisión del usuario, antes de que el equipo clone

- **Opción A (recomendada, si nadie más ha clonado):** el **usuario**, no el agente, ejecuta una sola vez
  `git push --force-with-lease origin main`. Después borra la rama `respaldo-antes-reescritura`.
  `.claude/settings.json` prohíbe al agente el *push* forzado, y debe seguir así.
- **Opción B:** descartar la reescritura local con `git reset --keep origin/main` y aplicar encima el commit del MCP.
- En ambos casos, comprobar en GitHub (Settings → Emails) que `72682019@continental.edu.pe` está verificado
  en la cuenta `omarpiero`. Si no lo está, los commits no cuentan como del usuario en la gráfica de contribuciones.
- El repositorio es privado. El docente tiene que estar invitado antes de la entrega, porque la carátula del
  informe lleva el enlace (consigna S6 §4).

## 2. Cifras de la línea base que hay que citar con exactitud

Medido en el arnés del 2026-10-01 sobre **`fragmentos_v3.jsonl`**, que es el corpus que usa la aplicación:

| Dato | Valor medido |
|---|---|
| Similitud máxima de una consulta de C (fuera de cobertura) | **0,4698** |
| Primer τ sin falsos positivos | **0,47** (margen 0,0002 sobre esa consulta de C) |
| τ vigente | **0,48** (margen 0,010) |
| A+B respondidas **sin** regla de lema | **165/180** (91,7 %) con τ 0,48 · 167/180 (92,8 %) con τ 0,47 |
| A+B respondidas **con** regla de lema | **180/180**, 0 FP en C |
| Consultas que responde solo la regla de lema | 18: A 12 · B 3 · D 3 |
| Consultas más cercanas al umbral | A038 y B038 «diablo» y D023 «devil»: similitud 0,4799, a 0,0001 de τ (hoy las salva la regla de lema) |

**Inconsistencia que corregir:** la cifra «0,48 → 167/180 (92,8 %)» de la revisión 2 y de la pregunta de
ADR-021 sale de `calibrar_umbral.py`, que trabaja sobre `fragmentos_v2.jsonl`. Sobre v3, con τ = 0,48, son
165/180. El informe y las diapositivas deben citar **un solo corpus** (v3) y decirlo.

**Recomendación:** mantener **τ = 0,48**. Es el primer valor que deja un margen apreciable sobre la consulta
negativa más alta. Bajar a 0,47 gana dos consultas a costa de quedar a 0,0002 de un falso positivo. Se anota
en ADR-020 como «se conserva 0,48 por margen; primer τ sin FP en v3 = 0,47».

## 3. ADR-021 (regla de lema): viable, con condiciones

La propuesta del agente («Aceptar, rotulada») es **viable y es la recomendada**. Una coincidencia exacta con el
lema de una entrada del diccionario es, por definición, respaldo documental. El coseno la penaliza solo porque
las entradas largas diluyen el vector (p. ej. «SOL», con varias acepciones). Condiciones para la spec del PR 3:

1. **Solo para fragmentos lexicográficos** y solo cuando el término depurado es **un único lema**. Las consultas
   de varias palabras no la activan; ejemplo de prueba: «¿cómo se dice banco de peces?» no puede responder por
   el lema «banco».
2. **Normalización declarada**: definir si se ignoran tildes y mayúsculas (p. ej. «cuanto» y «cuánto») y
   probarla, porque cambia qué consultas activan la regla.
3. La entrada se muestra **completa y literal**. Esto depende de corregir D-4 (truncado) en el mismo sprint. El
   generador recibe solo esa entrada y el `VerificadorFormaLiteral` se aplica igual.
4. **Rótulo visible** «respaldo: entrada exacta del diccionario», con la similitud (< τ) a la vista. Nunca se
   presenta como una respuesta por similitud.
5. **Reporte separado** en todas las tablas: respondidas por similitud y respondidas por lema (M4, M15). La
   evidencia «0 FP en C» es débil para esta regla, porque ninguna de las 28 consultas de C es un lema. Añadir a
   C negativas que **sí** sean lemas de palabras funcionales o ambiguas («algo», «cuanto», «banco» usados en
   frases de otro sentido) solo si las formula el equipo; los agentes no fabrican consultas de evaluación.

## 4. Brechas por instrumento

Prioridad: **P0** imprescindible para la entrega; **P1** muy recomendable; **P2** si sobra tiempo. «Agente» =
Claude Code; «equipo» = personas; «documental» = asistente que regenera figuras, diapositivas e informe.

| # | Exigencia (fuente) | Estado | Qué falta | Quién | Prioridad |
|---|---|---|---|---|---|
| G-01 | KPIs del problema **con datos reales**; el ejemplo de la rúbrica es «500 registros, 18 % de error, 36 h de latencia» (S6-C1-B, S8-P1) | Hay KPIs de contexto (vitalidad de la lengua, 88,4 % de páginas con texto, ningún servicio estatal en wanka) | **KPI del proceso AS-IS medido**: tiempo y tasa de fallo de la consulta manual en los PDF. Protocolo **M16** en §5 | Equipo (mide) + agente (prepara la lista y la hoja) | **P0** |
| G-02 | BPMN AS-IS y SIPOC, matriz de restricciones, 5 Porqués (S6-C1-B) | Hay fuentes en `docs/diagramas/` (v_bpmn, v_5porques) de la versión 1 | Regenerarlos con M16 | Documental | P0 |
| G-03 | «Por qué F1/Recall y no *accuracy*» (S6-C2-B) | El argumento existe en el Doc. 2 | Cifra para la diapositiva, calculada sobre los recuentos medidos: con 220 consultas atendibles y 28 negativas, un sistema que **siempre responde** tendría *accuracy* 220/248 = 88,7 % y 28 falsos positivos, es decir, inventaría en todas las consultas sin respaldo. Que el arnés lo calcule y lo guarde como M3-bis | Agente | P0 |
| G-04 | Matriz LPDP y matriz ética de la IA; **mitigación de sesgos** del algoritmo (S6-C3-B) | Hay matrices en el Doc. 3 | **M17** (§5): sesgo medible del sistema real (distribución del respaldo por documento, brecha ES/EN, auditoría manual de una muestra de la tabla EN→ES). D-2 («water → océano») es un sesgo de la tabla ya observado | Agente + equipo (auditoría de la muestra) | P1 |
| G-05 | Trazabilidad Objetivo → Épica → HU → Given/When/Then → PMV1 y **tablero** revisado por el docente (S6-C4-B) | Trazabilidad en `docs/03`; tablero **sin crear** | Crear GitHub Projects (`CONSIDERACIONES.md` §7.4) **ya**, con las tarjetas de los PR, para que el historial de cambios del tablero exista antes de la entrega | Agente (comandos `gh`) + usuario | **P0** (antes P2) |
| G-06 | Métricas ágiles reales: velocidad, *burndown*, *lead/cycle time*, registro CHG (S6-C4 §12–13) | CHG en `CONSIDERACIONES.md` §11 | M12 a partir de Projects y de los PR. Si no hay estimación en puntos, se reporta *lead time* y número de PR por sprint, sin inventar velocidad | Agente | P1 |
| G-07 | **Reportes reales** de cobertura, *code smells* de SonarQube y colección de Postman (S6-C5-B, S7-C5) | Postman existe; SonarQube configurado por JAR | M8, **M9 (SonarQube)** y **M10 (Newman)** pasan a **P0**: la competencia los evalúa explícitamente | Agente | **P0** (antes P1) |
| G-08 | Matriz de limitaciones de herramientas (S6-C5-B) | En el Doc. 5 y su anexo | Añadir las observadas al construir: falsos positivos de SonarQube si los hay, errores de la tabla EN→ES, latencia de Ollama en CPU (M5), Postman sin pruebas de carga | Documental, con datos del agente | P1 |
| G-09 | Pruebas de rendimiento o seguridad (S6-C5 cat. 6) | No hay | Opcional: ráfaga de 50 consultas a `/api/consultar` con 5 clientes concurrentes (script Python o k6) → P50/P95 bajo carga | Agente | P2 |
| G-10 | Estructura física `src/{domain,application,adapters,infrastructure}` y dominio sin *imports* de frameworks (S6-C6-B, S7-E2) | Aún sin mover | PR 1–2 (ya P0) + capturas `GH-1` y `GH-2` | Agente | P0 |
| G-11 | **Pruebas de casos de uso con *fakes* de los puertos de salida, sin BD real** (S6-C6-B) | Existen (`IndiceFalso`, `GeneradorFalso`, `RepositorioFalso`) | Que queden en `tests/unit/application/` con nombre explícito (`test_consultar_corpus_con_fakes.py`) y en la captura `QA-1` se vea que no hay BD ni Ollama | Agente | P0 |
| G-12 | Diagrama de **paquetes o despliegue UML** con las capas y los puertos reales (S8-P3) | Las figuras actuales son de la versión 1 | Al cerrar el PR 2, exportar `arbol_src.txt` y `puertos.md` (lista de puertos IN/OUT, adaptadores y su cableado en el contenedor) para regenerar las figuras | Agente → documental | P0 |
| G-13 | Tabla consolidada de resultados: cobertura, latencia, F1, **criterios de aceptación validados** (S8-P3) | Protocolo M1–M15 | Añadir a M7 el **conteo de escenarios Gherkin aprobados por HU**, por ejemplo «HU-06: 5/5», porque es la fila «criterios validados» | Agente | P0 |
| G-14 | E1: **indicadores en tiempo real** del módulo de IA (S7-E1) | La interfaz muestra la similitud en texto | **UI-13**: indicador visual de similitud frente a τ, latencia de la respuesta en ms, vía de respaldo y número de fragmentos recuperados | Agente (frontend) | **P0** |
| G-15 | E1: diseño *responsive* y trazabilidad con las HU priorizadas (S7-E1) | UI-10 era P1 | UI-10 pasa a **P0**. En el informe, cada captura lleva su HU | Agente + documental | P0 |
| G-16 | E3: **manejo de excepciones** en vivo (S7-E3) | **Defecto D-6** (§4.1) | Corregir en el PR 3 | Agente | **P0** |
| G-17 | E2: «commits constantes **por los integrantes**» (S7-E2) | Solo el usuario y el autor del código base | Cada integrante hace al menos un PR propio desde su cuenta (`docs/10` §6). No se puede delegar en el agente | Equipo | **P0** |
| G-18 | Carátula del informe con roles, enlace al repo y al video; % de participación (S6 §4, S8) | — | Datos del equipo | Equipo | P0 |
| G-19 | Arquitectura «híbrida (base hexagonal)» (S6-C6, S8-P3) | Hexagonal elegida por matriz (Doc. 0) | Ver §6: cómo presentarla con honestidad | Documental | P0 |

### 4.1 Defecto nuevo

| ID | Defecto | Evidencia | Corrección |
|---|---|---|---|
| **D-6** | Si Ollama está detenido, `OllamaGenerador.redactar` deja escapar la excepción de `httpx` (`raise_for_status` sin captura) y `/api/consultar` responde 500 | `backend/infrastructure/adapters/output/ollama_generador.py`: solo `precalentar` y `disponible` capturan `httpx.HTTPError` | El caso de uso captura el fallo del puerto y devuelve la respuesta con el **fragmento literal** (plantilla) y un aviso: «el servicio de redacción no está disponible». Prueba `@salvaguarda` con un generador falso que lanza excepción. Es el caso C-10 del video |

## 5. Mediciones nuevas

### M16 · KPI del proceso AS-IS (consulta manual), lo mide el equipo

Responde a la exigencia de un KPI «extraído de datos reales» del proceso actual. Sin esto, el problema se
cuantifica con indicadores de contexto, pero no con el proceso que el sistema sustituye.

1. El agente genera `docs/evidencias/m16/lista_m16.csv` con **20 consultas de A** y **5 de C**, elegidas al
   azar con semilla fija (2026) de `evaluacion_v2.json`, y una hoja vacía `kpi_asis.csv` con estas columnas:
   `id, consulta, persona, inicio, fin, segundos, resultado (correcto|incorrecto|no_encontrado), documento, pagina`.
2. Dos integrantes que **no** hayan trabajado con el corpus buscan cada término **a mano** en los 8 PDF, con
   un visor y Ctrl+F permitidos. Abandonan a los **5 minutos** («no_encontrado»).
3. El agente calcula:
   - tiempo medio y mediano;
   - tasa de fallo: incorrecto + no encontrado;
   - % de consultas de C en que la persona «encuentra» algo que no corresponde.

   Y lo compara con el sistema sobre **las mismas 25** consultas: latencia de M5 y respaldo correcto de M4.
4. Limitaciones que se declaran: muestra pequeña, personas del propio equipo y Ctrl+F favorable, porque en la
   práctica el usuario no sabe en qué PDF buscar. Es un KPI **conservador**.

Resultado para la diapositiva 3 y el informe C1: «consulta manual: X s de media y Y % de fallo, frente a
Z s con el sistema y 0 respuestas sin respaldo». Las cifras se rellenan con lo medido.

### M17 · Sesgo medible del sistema (C3)

- Distribución del respaldo por documento en A+B+D: qué parte de las respuestas sale de cada diccionario. Una
  concentración alta es un sesgo de fuente y de variedad, ligado al riesgo R-09.
- Brecha por idioma: recall@5 en ES (A) frente a EN (D), con D declarado techo.
- Auditoría de la tabla EN→ES: el agente extrae 50 entradas al azar (semilla fija) y **el equipo** marca cada
  una como correcta, incorrecta o dudosa. Se reporta el % de error. Es la evidencia cuantitativa de la
  mitigación «se muestran todas las lecturas».

## 6. «Arquitectura híbrida» sin inventar componentes

El ejemplo del docente combina un núcleo hexagonal con microservicios, SOA y bus de eventos. Este proyecto
**descartó** microservicios (2,80) y *event-driven* (3,10) frente a hexagonal (4,65) en la matriz del Doc. 0.
Presentarlos ahora contradiría esa decisión. La forma honesta de cumplir «híbrida (base hexagonal)» es mostrar
el **núcleo hexagonal** y, alrededor, los **estilos que sí existen**:

| Estilo | Dónde está en el sistema |
|---|---|
| Hexagonal (núcleo) | `domain` + `application` con puertos IN/OUT; adaptadores IN (REST por recurso, CLI) y OUT (índice, Ollama, traductor, extractor, SQLite) |
| Cliente-servidor local | SPA React ↔ API FastAPI en `127.0.0.1` |
| Servicio de inferencia separado | Ollama como proceso independiente, consumido por HTTP a través de `GeneradorTextoPort` |
| Canal de compilación (*build-time*, por lotes) | Ingesta → índice → exportación binaria → app móvil sin red (PMV2/PMV3), con verificación de paridad |

**Figura a producir** (documental), con la misma lectura de izquierda a derecha que el ejemplo:
- Izquierda: Aplicación web (React) → Controladores REST → Adaptadores de entrada.
- Centro: Núcleo hexagonal, con la capa de aplicación (puertos de entrada → casos de uso → puertos de salida) y,
  dentro, la capa de dominio (entidades, objetos de valor, servicios de regla).
- Derecha: adaptadores de salida hacia Ollama (proceso aparte), SQLite, índice léxico, tabla EN→ES y corpus PDF.
- Abajo: el canal de compilación hacia el artefacto móvil.

Los nombres de clase salen del `puertos.md` de G-12; no se dibuja hasta tener el PR 2 fusionado.

## 7. Prioridades P0 actualizadas (sustituye la lista P0 del prompt §5)

PR 1 · PR 2 · PR 3 (incluye D-1 y **D-6**) · PR 4 · PR 6 (truncado) · PR 7 (UI-01…05, 07, 08, **10, 13**) · PR 8 ·
PR 9 · **PR 10 reducido a SonarQube + cobertura + Newman** (M8, M9, M10) · **GitHub Projects** · PR 11 (M1–M8,
M13–M15, **M3-bis**, **M16**) · `docs/11` §3 · **un PR por integrante** · `arbol_src.txt` + `puertos.md`.

P1: M17 · M11 · M12 · PR 5 (D-2) · UI-06, 09, 11, 12. P2: G-09 (carga) · PostgreSQL como segundo adaptador ·
D-3.

## 8. Mensaje para pegar en Claude Code

```text
Lee docs/13_BRECHAS_RUBRICA.md (revisión contra S6, S7 y S8). Antes de seguir:
1) Respuestas a tus preguntas: ADR-021 aceptada CON las 5 condiciones del §3; τ se mantiene en 0,48 (§2),
   y en ADR-020 anota que el primer τ sin FP en v3 es 0,47 y por qué no se adopta.
2) Corrige las cifras: cita siempre el corpus v3 (165/180 sin lema con τ 0,48), no la cifra de v2.
3) Integra en el plan la lista P0 del §7, que sustituye a la del prompt §5, y añade D-6 a los defectos.
4) Prepara M16 (lista de 25 consultas con semilla 2026 y hoja kpi_asis.csv) y dime cuándo la tenemos que medir.
5) Dame los comandos gh para crear el GitHub Projects (CONSIDERACIONES §7.4) y yo los ejecuto.
6) No hagas push forzado: la decisión sobre el historial divergente (§1.1) la tomo yo.
Después, preséntame las specs del PR 1 y PR 2 para aprobarlas juntas.
```
