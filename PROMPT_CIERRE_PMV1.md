# Prompt de arranque — unificar y cerrar el PMV1

> **Cómo se usa.** Abre Claude Code en la raíz de `TP_RAG_Quechua`, que crea `crear_repo.ps1` (ver
> `docs/10_REPOSITORIO.md`). Comprueba con `/agents` que aparecen los tres subagentes y pega **todo** el
> bloque de abajo como primer mensaje. En sesiones siguientes basta con: «Retoma el cierre del PMV1 según
> `PROMPT_CIERRE_PMV1.md`; dime dónde quedamos».

---

```text
Eres el orquestador de este repositorio. Objetivo de la sesión (y de las siguientes hasta terminar):
UNIFICAR el código del integrante con la especificación vigente y CERRAR EL PMV1 para la entrega de la
Unidad II, dejando además las mediciones y los casos del video listos.

1. LEE, en este orden, antes de proponer nada:
   CLAUDE.md → docs/09_LINEA_BASE_V2.md → CONSIDERACIONES.md (completo) → docs/08_AUDITORIA_REPO_BASE.md
   → docs/11_CASOS_VIDEO_Y_CAPTURAS.md → docs/12_MEDICIONES_PARA_DIAPOSITIVAS.md.
   El código de partida es el del integrante (etiqueta git `base-integrante`). Su comportamiento ya
   coincide con la línea base v2; lo que falta es la forma que exige la rúbrica (estructura `src/` en 4
   capas, puertos de entrada, Factory y Strategy explícitos), formalizar dos reglas, un verificador de forma
   literal, endurecer la interfaz React, SQLite por defecto, pruebas, CI y mediciones.

2. COMPRUEBA EL ENTORNO y dime qué falta (no instales nada global sin preguntarme):
   python --version · node --version · git log --oneline -3 · git tag
   ollama list · ollama ps · ollama show qwen3.5:4b (anota el campo de cuantización)
   nvidia-smi (si existe) · que backend/data/fragmentos_v3.jsonl y corpus/pdf/*.pdf existen
   Crea backend/.venv, instala requirements y ejecuta las pruebas actuales (deben salir 40/40).

3. CONGELA LA LÍNEA BASE antes de mover un solo archivo (es la red de seguridad de todo el refactor):
   ejecuta sobre el código tal cual las 248 consultas de backend/data/evaluacion_v2.json con un generador
   falso instrumentado y guarda en docs/evidencias/<fecha>_base-integrante_<maquina>/:
   arnes_por_consulta.csv (id, particion, consulta, traduccion, top1_id, similitud_max, decision,
   via_respaldo, pasajes, respaldo_correcto) y barrido_umbral.csv (scripts/calibrar_umbral.py).
   Después de cada PR de refactor (1, 2 y 3) el arnés debe dar EXACTAMENTE lo mismo salvo los cambios que
   el PR declare. Si cambia algo no declarado, paras y me lo explicas.

4. PREGÚNTAME EN UN SOLO BLOQUE (con AskUserQuestion si está disponible) lo que solo yo puedo decidir, y
   no empieces los PR afectados sin respuesta:
   a) Fecha y hora exactas de la exposición y de la entrega → planifica hacia atrás.
   b) ADR-021: ¿la coincidencia exacta de lema responde aunque S < τ? (si NO, se retira y se remide).
   c) ADR-027: ¿SQLite por defecto y PostgreSQL como segundo adaptador? (la consigna solo pide
      «Persistencia»; no exige PostgreSQL).
   d) ADR-013: ¿se guarda el texto de la consulta en el historial? (aviso + borrado en cualquier caso).
   e) La lista de fallos de la interfaz que yo haya visto (se añade a CONSIDERACIONES §5.1).
   f) Nombres y roles de los cinco integrantes, y quién hará los commits de cada PR.

5. PLAN DE PR. Sigue CONSIDERACIONES.md §5 con esta PRIORIDAD (si el tiempo no alcanza, se recorta desde
   abajo y se declara lo no hecho; nunca se recorta P0):
   P0 — imprescindible para la entrega:
     PR 1 estructura hexagonal (git mv, historial conservado) · PR 2 puertos de entrada + CLI ·
     PR 3 reglas de respuesta explícitas (τ de configuración, UmbralConLema, PasajesSinAfirmacion,
     RespuestaFactory) · PR 4 VerificadorFormaLiteral · PR 6 (solo la corrección de entradas truncadas y su
     prueba de regresión) · PR 7 interfaz: UI-01…UI-05, UI-07, UI-08 · PR 8 SQLite por defecto + borrado ·
     PR 9 prueba de arquitectura + Gherkin de HU-03, HU-06, HU-07 · PR 11 mediciones M1–M8 y M13–M15 ·
     docs/11 rellenado con salidas reales.
   P1 — muy recomendable (la rúbrica C5 nombra SonarQube):
     PR 10 CI con ruff, pytest-cov, npm test y SonarQube + M9 · Newman (M10) · PR 5 traductor como
     Strategy y corrección del defecto D-2 · resto de UI-06, UI-09…UI-12 · M11, M12.
   P2 — si sobra tiempo: PostgreSQL probado como segundo adaptador · resto de PR 6 · GitHub Projects ·
     PR 12 README final (el README con la tabla de resultados sí es P0 si existe M1–M8).

6. DEFECTOS YA OBSERVADOS sobre el código base (docs/11 §1, ejecutados el 2026-10-01 con generador falso).
   Cada uno lleva su prueba de regresión:
   D-1 «¿cómo se dice computadora…?» se abstiene pero ofrece como «pasaje» un texto en quechua del libro
       Saberes y Haceres (pág. 55) porque, con una sola palabra de contenido, el filtro exige solo una
       coincidencia (min(2, n)). Con la interfaz actual parece una traducción. Propuesta: las consultas
       LÉXICAS («cómo se dice X», «how do you say X», término suelto) no reciben pasajes de prosa; solo las
       preguntas de prosa. Va en el PR 3 con ADR-022 actualizado.
   D-2 «how do you say water…» responde con «OCÉANO: Lamar.» (sim. 0,694) por delante de «AGUA: Yaku.»
       (0,571), porque la tabla da water → [agua, océano, regar] y gana la lectura con mayor similitud.
       Propuesta: respetar el orden de lecturas de la tabla (la primera es la principal) y mostrar todas
       como alternativas rotuladas. PR 5.
   D-3 «Wie sagt man Fuchs auf Quechua?» se detecta como español y se abstiene, en lugar de responder
       «idioma no soportado». Corregir el detector o, como mínimo, no presentarlo en el video.
   D-4 «sol» responde por la regla de lema con similitud 0,351 y la entrada sale truncada
       («SOL: Inti. (rayo de sol) Intip shaplan. (época de»). PR 6 + rótulo de vía de respaldo (PR 3/7).
   D-5 Interfaz: un único botón «A+» que cicla tamaños, sin reducir ni restablecer; historial solo en
       estado local. PR 7.

7. MODO DE TRABAJO para este cierre (CLAUDE.md §4, aligerado por plazo, sin saltar compuertas):
   - Una spec breve por PR (≤ 1 página, plantilla de docs/specs/). Puedes presentarme varias a la vez
     para que las apruebe juntas.
   - Una historia en desarrollo a la vez; el programador trabaja con TDD en su rama; el auditor revisa
     cada PR; yo fusiono. Nada entra en main sin mi aprobación.
   - Los commits los firma quien esté autenticado en esta máquina. Nunca cambies el autor de un commit
     para atribuírselo a otro integrante. Si un PR corresponde a otro rol, prepárale la rama y la spec y
     dime qué tiene que hacer esa persona.
   - Las pruebas que necesitan el corpus real (índice completo, arnés) llevan el marcador `datos` y se
     omiten en la CI, que no tiene el corpus. Se ejecutan en local y su salida va a docs/evidencias/.
   - Reglas que no se negocian: CLAUDE.md §2. En particular: ninguna forma quechua escrita por un agente;
     ninguna cifra inventada (lo no medido es «por registrar»); τ solo cambia con barrido + ADR + mi visto
     bueno; FastAPI solo en 127.0.0.1; nada de corpus, .env ni .db en Git.

8. AL TERMINAR CADA SESIÓN, el archivista actualiza docs/05_KANBAN.md, docs/04_SPRINTS.md §7,
   docs/07_DECISIONES.md y CLAUDE.md §13. Tú me das un resumen en 5 líneas: qué se fusionó, qué está en
   revisión, qué decisión me toca y qué falta de P0.

9. ENTREGA FINAL DEL PMV1 (cuando P0 esté fusionado):
   - Ejecuta python scripts/medir_pmv1.py en esta PC y, si es posible, en una PC sin GPU (M5/M6 cambian),
     siguiendo docs/12_MEDICIONES_PARA_DIAPOSITIVAS.md.
   - Rellena docs/11 §3 con la salida real de cada caso del video y genera las capturas de nombre fijo
     que se puedan automatizar (el resto me lo indicas).
   - Etiqueta v0.1.0 y dime exactamente qué carpeta debo entregar al asistente documental para regenerar
     figuras, diapositivas e informe.

Empieza por los pasos 1–3 y luego hazme las preguntas del paso 4. No escribas código de producción hasta
que yo haya respondido.
```

---

## Notas para el usuario

- **Tiempo.** Si la exposición es en pocos días, el P0 es el alcance realista. El PR 1 (mover a `src/`) y el
  PR 3 (reglas explícitas) son los que más pesan en la rúbrica E2/C6. El PR 7 es lo que más se ve en E1 y E3.
- **Coste de contexto.** Cada PR es una sesión razonable. Al terminar una, empieza la siguiente con el
  mensaje corto del encabezado: el estado vive en `docs/` y en `CLAUDE.md` §13, no en la memoria del chat.
- **Qué devolverme.** La carpeta `docs/evidencias/<fecha>_<commit>_<máquina>/` completa (JSON, CSV y
  capturas) y `docs/11` con las salidas reales. Con eso se regeneran figuras, diapositivas y guion con datos
  medidos (`docs/12` §3).
