# 11 · Casos de uso para probar, video E3 y capturas E1

> **Para quién.** El usuario (pruebas a mano y grabación) y el orquestador (rellena el §3 con salidas
> reales al cerrar el PMV1).
>
> **Qué evalúa la lista de cotejo.**
> - **E3:** flujo continuo Usuario → Controller (Adapter IN) → Use Case → Módulo de IA → Adapter OUT →
>   Persistencia / Respuesta, con «respuesta oportuna y manejo de excepciones/validaciones de negocio».
> - **E1:** flujos principales, integración de IA visible («indicadores en tiempo real»), usabilidad,
>   diseño *responsive* y trazabilidad con las HU.

---

## 1. Comportamiento del código base hoy (para elegir bien las consultas)

Ejecutado el **2026-10-01** sobre el código del integrante (commit `8eb172b`, `fragmentos_v3.jsonl`,
τ = 0,48, tabla EN→ES), con un **generador falso** (sin Ollama) para ver solo la recuperación y la
decisión. **Son cifras del código base, no del PMV1 final**: el §3 se rellena con el código cerrado.

| Consulta | Decisión | Similitud | Respaldo mostrado | ¿Invoca generador? | Uso en el video |
|---|---|---:|---|---|---|
| ¿cómo se dice zorro en quechua wanka? | Responde | 0,610 | `ZORRO: Atuq.` · diccionario Wanka, p. 37 | Sí | **Sí** (caso principal) |
| ¿cómo se dice criptomoneda en quechua wanka? | Se abstiene, sin pasajes | 0,05 | — | **No** | **Sí** (salvaguarda) |
| how do you say fox in Wanka Quechua? | Responde; traducción «zorro» | 0,610 | `ZORRO: Atuq.` · p. 37 | Sí | **Sí** (inglés) |
| how do you say water in Wanka Quechua? | Responde con la lectura equivocada | 0,694 | `OCÉANO: Lamar.` p. 25, por delante de `AGUA: Yaku.` p. 2 | Sí | **No** hasta corregir **D-2** |
| ¿cómo se dice sol en quechua wanka? | Responde **por lema** bajo τ | 0,351 | `SOL: Inti. (rayo de sol) Intip shaplan. (época de` (truncada) | Sí | Solo si se acepta ADR-021 y tras corregir **D-4** |
| ¿Qué referencia temporal implica la acción expresada por el verbo nominalizado? (P001) | Se abstiene **con pasajes** de la gramática | 0,339 | 2 pasajes de Cerrón-Palomino | No | **Sí** (prosa), cuando estén rotulados «no es una respuesta» |
| ¿cómo se dice computadora en quechua wanka? | Se abstiene **con un pasaje en quechua** | 0,124 | Saberes y Haceres, p. 55 | No | **No** hasta corregir **D-1** |
| Wie sagt man Fuchs auf Quechua? | Se abstiene (lo toma por español) | 0,176 | — | No | **No** hasta corregir **D-3** |

Latencia de recuperación y decisión: 4–17 ms por consulta en la nube; la de extremo a extremo con Ollama
se mide en M5.

### Defectos encontrados (se corrigen en el PMV1, `PROMPT_CIERRE_PMV1.md` §6)

| ID | Defecto | Riesgo en la demostración |
|---|---|---|
| D-1 | Con una sola palabra de contenido, el filtro de pasajes exige una coincidencia en vez de dos y saca prosa en quechua ante una consulta léxica sin respaldo | Parece una traducción no respaldada justo en la salvaguarda |
| D-2 | En inglés gana la lectura secundaria con mayor similitud (*water* → «océano») | Respuesta incorrecta con respaldo real |
| D-3 | El detector clasifica el alemán como español | No se puede mostrar «idioma no soportado» |
| D-4 | Entrada del diccionario truncada («SOL… (época de») | Fragmento incompleto en pantalla |
| D-5 | Solo «A+», sin reducir ni restablecer; historial solo en estado local | Usabilidad (E1) y persistencia (E3) |

## 2. Pruebas a mano antes de grabar

Hazlas en este orden con el PMV1 cerrado, con el backend y Ollama ya calientes (una consulta previa
cualquiera). Marca cada una y anota lo que veas en el §3.

| Caso | Acción | Resultado esperado | HU / regla | Captura E1 |
|---|---|---|---|---|
| C-01 | «¿cómo se dice zorro en quechua wanka?» | «Atuq» literal; fragmento `ZORRO: Atuq.`; diccionario Wanka, p. 37; similitud ≥ τ; vía «similitud» | HU-03, HU-07 | `E1-1_consulta_zorro.png` |
| C-02 | «¿cómo se dice criptomoneda en quechua wanka?» | Mensaje de ausencia; **ninguna** forma quechua; similitud < τ visible; en el log del backend, el generador **no** se invoca | HU-06 | `E1-2_abstencion.png` |
| C-03 | «how do you say fox in Wanka Quechua?» | Lecturas de la traducción visibles («zorro»); «Atuq» literal, p. 37 | HU-05 | `E1-3_consulta_ingles.png` |
| C-04 | «¿cómo se dice sol en quechua wanka?» | Solo si ADR-021 se acepta: respuesta rotulada «respaldo: entrada exacta del diccionario», con la similitud (< τ) a la vista y la entrada **completa** | ADR-021 | `E1-4_respaldo_lema.png` |
| C-05 | Pregunta de prosa P001 (texto en el §1) | Abstención + pasajes literales y citados, rotulados «no es una respuesta» | ADR-022 | `E1-5_pasajes_prosa.png` |
| C-06 | «¿cómo se dice computadora en quechua wanka?» | Tras corregir D-1: abstención **sin** pasajes | HU-06 | — |
| C-07 | Enviar la consulta vacía; pegar un texto de más de 300 caracteres | Mensaje de validación en español; no se llama a la API o esta responde 422 y la interfaz lo explica | RS-02, E3 «validaciones» | `E1-8_validacion.png` |
| C-08 | Tras corregir D-3: «Wie sagt man Fuchs auf Quechua?» | «Solo se admiten consultas en español o en inglés» | RF-04 | (opcional) |
| C-09 | Hacer 3 consultas → reiniciar el backend → recargar la página | El historial sigue ahí (SQLite); «Borrar historial» lo vacía; aviso de privacidad visible | RF-11, ADR-027, E3 «Persistencia» | `E1-6_historial.png` |
| C-10 | Detener Ollama (`ollama stop qwen3.5:4b` o cerrar Ollama) y repetir C-01 | **Manejo de excepción**: la respuesta muestra el fragmento literal con un aviso de que el servicio de redacción no está disponible; nunca un error 500 ni una pantalla en blanco. *Comportamiento a confirmar por el agente; si no existe, es P0 del PR 3* | E3 «excepciones» | (opcional) |
| C-11 | Detener el backend y consultar | Estado de error con botón «Reintentar» | UI-02 | (opcional) |
| C-12 | A−, A+ y restablecer | Tres tamaños; los extremos deshabilitan el botón; se recuerda al recargar | UI-01 | `E1-9_tamano_texto.png` |
| C-13 | Ventana a 360 px (DevTools, modo dispositivo) | Sin desplazamiento horizontal; todo legible | UI-10 | `E1-10_movil_360px.png` |
| C-14 | Pestaña Fuentes del corpus | Lista del manifiesto con documento, páginas y licencia («por registrar» si falta) | HU-01 | `E1-7_fuentes_ingesta.png` |

Si un caso no da lo esperado, **no lo grabes**. Anótalo y pásaselo a Claude Code como defecto.

## 3. Salidas reales del PMV1 (lo rellena el orquestador)

| Caso | Consulta exacta | Decisión | Vía | Similitud | Documento · página | Latencia total (ms) | ¿Generador? | Procesador (`ollama ps`) | Captura |
|---|---|---|---|---:|---|---:|---|---|---|
| C-01 | | | | por registrar | | por registrar | | | |
| C-02 | | | | por registrar | | por registrar | | | |
| C-03 | | | | por registrar | | por registrar | | | |
| C-04 | | | | por registrar | | por registrar | | | |
| C-05 | | | | por registrar | | por registrar | | | |
| C-07 | | | | — | — | — | | | |
| C-09 | | | | — | — | — | | | |
| C-10 | | | | por registrar | | por registrar | | | |

## 4. Guion del video E3 (1,5–2 min, una sola toma)

**Preparación (10 min antes)**
- [ ] PC con GPU si es posible: comprobar con `ollama ps` que dice GPU. Si es CPU, revisar en M5 que la
      latencia no rompa el ritmo.
- [ ] Backend con log por capas a nivel INFO, en una terminal visible a la derecha; navegador a la izquierda.
- [ ] Una consulta de calentamiento fuera de cámara (la primera carga del modelo es la lenta).
- [ ] Historial vacío; tamaño de letra «grande» para que se lea en el video; notificaciones desactivadas.
- [ ] OBS u otra grabadora a 1080p; micrófono probado. El narrador es el rol Frontend & Integration.

| Tiempo | Pantalla | Qué se dice (idea, no texto literal) | Qué demuestra |
|---|---|---|---|
| 0:00–0:10 | App + árbol `backend/src/` en el editor | «Interfaz React; detrás, cuatro capas: domain, application, adapters, infrastructure» | Arquitectura |
| 0:10–0:40 | C-01 zorro; en el log, la secuencia controller → puerto de entrada → caso de uso → índice → evaluador → generador → verificador → repositorio | «La forma sale literal del diccionario, con documento y página; la IA solo redacta» | Flujo completo + trazabilidad |
| 0:40–1:05 | C-02 criptomoneda; en el log, «generador no invocado» | «Sin respaldo, el sistema lo declara y no inventa: el modelo ni siquiera se ejecuta» | Salvaguarda (núcleo ético) |
| 1:05–1:25 | C-03 fox | «La consulta en inglés se traduce; la forma quechua nunca se traduce» | Multilingüe |
| 1:25–1:40 | C-07 validación + C-09 historial tras recargar | «Reglas de negocio y persistencia en SQLite tras un puerto Repository» | Validaciones + persistencia |
| 1:40–1:55 | `pytest -m salvaguarda` en verde + panel de SonarQube (si existe M9) | «La salvaguarda está probada en cada cambio» | Calidad |

C-04 (lema) y C-05 (prosa) se muestran en las **capturas E1** o en la exposición en vivo, no en el video,
para no pasar de 2 minutos. Si sobra tiempo, C-05 es el siguiente candidato porque muestra la tercera
salida de RF-08.

## 5. Capturas E1 (nombres fijos, en `docs/evidencias/<…>/capturas/`)

Las de la tabla del §2 más: `GH-1_estructura_src.png` (árbol de `backend/src` en GitHub) ·
`GH-2_domain_sin_frameworks.png` (un archivo de `domain/` con solo importaciones de la biblioteca estándar) ·
`QA-1_pytest.png` · `QA-2_sonarqube.png` · `QA-3_newman.png` · `QA-4_vitest.png` ·
`PM-1_projects_roadmap.png` · `PM-2_projects_board.png` · `HW-1_ollama_ps_gpu.png` ·
`HW-2_ollama_ps_cpu.png` · `HW-3_ollama_show.png`. Formato PNG, ventana a 1366 × 768 o mayor, sin datos
personales visibles (barra de marcadores, correo, rutas con el nombre de usuario).
