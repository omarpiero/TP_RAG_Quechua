# Auditoría PR #10 · test/e2e-capturas (B6)

- **PR / rama:** #10 `test/e2e-capturas` (diff `bb2b2b2..1e419ec`; última rama de la pila)
- **Fecha:** 2026-10-29
- **Puerta de calidad:** SonarQube local sin análisis real (solo SQ_UPGRADE); pendiente en B9.
- **Cobertura:** global 89 %, `domain/` ≈ 94 % (sin cambios en `domain/`).
- **Pruebas:** con `POSTGRES_PRUEBAS_URL` (`quechua_wanka_pruebas`, credencial sin imprimir): **232 pasan, 0 omitidas**. `salvaguarda` 18/18. Vitest 21/21 (`e2e/**` excluido de Vitest). **`npm run test:e2e`: 15/15 en dos corridas seguidas** (1,4 y 1,3 min, con Ollama activo). `npm audit --omit=dev`: 0 vulnerabilidades. `pip-audit`: limpio. Lint: solo los avisos ya conocidos.

## Hallazgos

| # | Sev. | Archivo | Regla | Descripción | Corrección sugerida |
|---|---|---|---|---|---|
| 1 | Mayor | `capturas/Swagger_documentacion_de_la_API.png`, `e2e/capturas.real.spec.js:143` | Evidencia | La captura es **solo un indicador «LOADING»** (7,7 KB, idéntica en mis dos corridas): se toma en cuanto existe el contenedor `.swagger-ui`, antes de que cargue la documentación. Además `/docs` de FastAPI carga Swagger UI desde una CDN; sin red no habría captura útil. | Esperar a un elemento de la documentación (p. ej. `.opblock-tag`) antes de capturar; considerar servir Swagger UI en local o anotar la dependencia de red de `/docs`. |
| 2 | Menor | `HU-03_…`, `HU-07_…`, `HU-01_lista…`, `HU-09_insuficiencia…` | Fidelidad de la evidencia | HU-02 incorpora una copia del diccionario como `copia-e2e-hu02.pdf` en la carpeta temporal y las capturas siguientes la muestran como segunda fuente de «ZORRO: Atuq. — página 37» (HU-07), con el contador del pie en 5 965 fragmentos frente a 3 605 en las primeras. Es honesto (lo devuelve el sistema), pero una captura de HU-07 con un documento que no existe en el corpus real confunde. | Ejecutar HU-02 al final, o eliminar la copia y reindexar al terminar esa prueba. |
| 3 | Menor | `HU-04_consulta_de_contenido_cultural.png` | Cobertura de la historia | La consulta «¿Qué relatos hablan del zorro?» termina en «Sin respaldo documental»: la captura no muestra contenido cultural recuperado. | Usar una consulta propia que sí devuelva un pasaje de los relatos, o rotular la captura como abstención. |
| 4 | Menor | `HU-05_…`, `RF-15_pasajes_de_prosa_rotulados.png` | Trazabilidad visible | En la ventana capturada el documento y la página no aparecen (la respuesta en inglés y el primer pasaje se cortan antes). En las demás capturas del mismo flujo sí salen (p. 37, p. 126). | Capturar la tarjeta completa con `locator` de la respuesta. |
| 5 | Menor | `docs/evidencias/cierre_u3/data_masiva/metricas/entrenar_predictores.txt:36`, `pip_audit.txt:4` (PR #7) | Datos personales | Rutas `C:\Users\<usuario>\AppData\…` con el nombre del usuario en evidencia versionada (también hay rutas en `b1_deps/`, de otro PR). Las capturas **no** muestran rutas. | Sustituir por `%TEMP%`/`[ruta]`. |
| 5b | Menor | interfaz (HU-09) | Presentación | Con 0 consultas contadas se ven «Por idioma:» y «Por vía:» sin datos. | Ocultar las filas vacías. |

Sin bloqueantes.

## Verificación por foco

1. **Repetible y sin tocar la base real.** `playwright.config.js` borra y recrea `frontend/e2e/.tmp`, copia `quechua_wanka.db` y `carga.db` allí y levanta tres APIs en 127.0.0.1 (8000-8002) con `RUTA_SQLITE` y `CARPETA_DATOS` temporales; Vite apunta a cada una con `VITE_PROXY`. `reuseExistingServer: false` (falla en vez de reutilizar una API real). Comprobado: tras dos corridas completas, el SHA-256 de `backend/quechua_wanka.db`, `carga.db`, `fragmentos_v3.jsonl` y los dos modelos del repositorio principal es idéntico al de antes; no se creó `backend/data/documentos`. PF-18 borra el historial solo de la copia. La subida de HU-02 usa una copia renombrada de un PDF ya registrado.
2. **Capturas (24 PNG revisados con Read, uno por uno).**
   - **Texto de `evaluacion_prosa.json`:** ninguno. Las preguntas visibles son propias o de conjuntos versionados (comprobado por conteo sin imprimir: 0 coincidencias con las cadenas exclusivas de prosa; incluye los términos y las frases de las prioridades y del historial, que son de `evaluacion_v2.json` y `negativas_prosa.json`).
   - **Rutas con el nombre del usuario o datos personales:** ninguno; solo `127.0.0.1` en Swagger y la fecha del sistema.
   - **Formas quechuas visibles:** `ZORRO: Atuq.` (pág. 37, forma verificada; también «atuq»/«**Atuq**» en las respuestas generadas) y el pasaje literal de la gramática (pág. 126, «no es una respuesta»), todas devueltas por el sistema con documento y página. En HU-05 y en el primer fotograma de RF-15 la página no cabe en la ventana (hallazgo 4). Sin formas inventadas.
3. **Cableado.** `vite.config.js` solo añade `VITE_PROXY` (por defecto el mismo proxy a 127.0.0.1:8000) y excluye `e2e/**` de Vitest. Paquete añadido: `@playwright/test` (devDependency); `npm audit` limpio.

## Observación al orquestador (fuera del PR)
El archivo `backend/quechua_wanka.db` del repositorio principal **cambió durante la sesión de auditoría** (hash `e0603771…` → `1f9b0560…`, modificado a las 05:14:38; mismo tamaño). Contenido intacto: 65 consultas del 2026-10-01, todas `usuario`, pero ahora **tiene la columna `origen`**, es decir, alguna aplicación arrancó contra la base real y aplicó la migración de HU-09. No lo hizo la E2E (copia en `.tmp`; el hash no cambió durante mis corridas) ni mis comprobaciones (usan el worktree). Conviene saber quién la arrancó; el cambio es la migración compatible prevista, no pérdida de datos.

## Estado de reglas
RN-01…RN-10 y RS-01…RS-08: sin cambios; cumplen (RS-01 con Vite y API solo en 127.0.0.1). Sin cambios en `domain/`, τ ni salvaguarda; el arnés no se tocó (idéntico a la línea base en la revisión de #7).

## Veredicto: **apto** para revisión humana, con el mayor 1 (captura de Swagger vacía) a corregir en este PR. 0 bloqueantes · 1 mayor · 6 menores.

## Re-auditoría de la corrección 119078f (2026-10-29)

`fix(e2e): capturas completas y reindexado atomico del indice`. Capturas nuevas abiertas con Read.

- **Hallazgo 1 (mayor): cerrado.** `Swagger_documentacion_de_la_API.png` (56 KB) muestra ahora el título, la descripción y las operaciones (`/api/estado`, `/api/consultas`, `/api/historial`, `/api/corpus/*`); ya no es el indicador «LOADING».
- **Hallazgo 2 (menor): cerrado.** HU-02 se ejecuta al final; HU-07 muestra una sola fuente (`293274822-diccionario-quechua-Wanka-docx.pdf`, página 37), sin `copia-e2e-hu02.pdf`.
- **Hallazgo 4 (menor): cerrado.** `HU-05_documento_y_pagina_de_la_respuesta_en_ingles.png` muestra «In Wanka Quechua, the word for fox is **Atuq**.» con `ZORRO: Atuq.` y el diccionario, página 37. `RF-15_pasaje_con_documento_y_pagina.png` muestra el pasaje literal rotulado «no es una respuesta» con `vbook.pub_cerron-palomino-…pdf`, página 125. Sin texto de `evaluacion_prosa.json`, ni rutas del usuario, ni datos personales; las formas quechuas visibles son las del fragmento citado.
- **Hallazgo 5 (rutas con el nombre del usuario): cerrado** (ver la re-auditoría de #7).
- Sin resolver (menores): HU-04 sigue mostrando una abstención; `RF-15_probabilidad_de_los_pasajes.png` y `RF-15_pasaje_con_documento_y_pagina.png` son idénticas (mismo hash), y `HU-03` y `HU-07` también; las filas vacías «Por idioma» y «Por vía» persisten.
- **Índice atómico:** revisado en `PR-12-carga.md`; la prueba de concurrencia pasa.

**Veredicto: apto** (0 bloqueantes · 0 mayores · 3 menores).
