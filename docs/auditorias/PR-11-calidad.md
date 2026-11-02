# Auditoría PR #11 · refactor/resolver-complejidad (B9)

- **PR / rama:** #11 `refactor/resolver-complejidad` (commits propios: `16eeed9` refactor, `6055757` sonar-project.properties, `736f265` cabeceras de seguridad)
- **Fecha:** 2026-10-29
- **Puerta de calidad (SonarQube Community local, Web API, proyecto `omarpiero_rag-quechua-wanka`):** **ERROR**. Condiciones: `new_coverage` 84,9 % (umbral 80, OK) · `new_duplicated_lines_density` 0,0 % (umbral 3, OK) · `new_violations` **44** (umbral 0, ERROR). Medidas globales: 0 bugs, 0 vulnerabilidades, 0 puntos críticos de seguridad, calificaciones de fiabilidad, seguridad y mantenibilidad «A», duplicación 0,7 %, cobertura Python 77,6 % (83 code smells en total). La edición Community guarda un solo análisis (rama `main`); el estado corresponde a la última pasada sobre esta rama.
- **Cobertura propia:** global 89 % (≥ 70), `domain/` ≈ 94 % (≥ 90; sin cambios en `domain/`).
- **Pruebas (última rama de la pila, con `POSTGRES_PRUEBAS_URL`):** 262 pasan, 0 omitidas; `salvaguarda` 28/28; arquitectura 4/4; Vitest 21/21. `pip-audit` y `npm audit --omit=dev`: sin vulnerabilidades.

## Hallazgos

| # | Sev. | Archivo:línea | Regla | Descripción | Corrección sugerida |
|---|---|---|---|---|---|
| 1 | Mayor | (puerta de calidad) | DoD calidad | La puerta está en rojo por 44 *code smells* nuevos (ninguno de seguridad ni fiabilidad). Se clasifican abajo: 4 reales y de arreglo barato, 8 de estilo o diseño discutible y 32 aceptables. | Corregir los 4 reales y los 3 ternarios anidados en este PR y registrar una excepción explícita (o ajustar las reglas de pruebas) para el resto. |
| 2 | Menor | `consultar_corpus.py` · `caracteristicas()` | Duplicación / deriva | Tras el refactor, `caracteristicas()` conserva una copia de la lógica de traducción y de la lectura ganadora que ahora existe en `_traducir` y `_anotar_lectura_ganadora`. El propio docstring exige que entrenar y predecir «hagan exactamente las mismas cuentas»; dos copias pueden divergir. | Que `caracteristicas()` llame a esos dos pasos. |
| 3 | Menor | `infrastructure/seguridad.py` | RS-03 | `/docs`, `/redoc` y `/openapi.json` quedan sin CSP porque Swagger UI se descarga de una CDN: al abrir `/docs` el navegador sale a la red. La interfaz sí cumple. | Documentarlo como excepción de desarrollo o servir Swagger UI en local. |
| 4 | Menor | `sonar-project.properties` y repositorio | CI | No hay `.github/workflows` (CLAUDE.md §10 prevé el análisis desde CI); el archivo ya no trae `sonar.organization` (necesario para SonarQube Cloud) y la cobertura de la interfaz (`frontend/coverage/lcov.info`) no se genera. | Añadir el flujo de CI y `vitest --coverage` cuando se pase a Cloud. |
| 5 | Menor | `docs/evidencias/cierre_u3/b9_calidad/registro.md` | Evidencia | ZAP queda pendiente por una limitación del entorno; el middleware es mitigación, no resultado de escaneo (declarado con honestidad). | Medir antes/después cuando ZAP pueda ejecutarse. |

Sin bloqueantes.

### Clasificación de los 44 smells nuevos (de `/api/issues/search`, `inNewCodePeriod=true`)

| Regla | n | Dónde | Veredicto |
|---|---|---|---|
| `python:S3776` complejidad cognitiva 16 y 17 (límite 15), **críticos** | 2 | `analizar_demanda.py:33`, `verificar_consistencia_datos.py:27` | **Real.** Pasan por uno o dos puntos; extraer un paso en cada función. |
| `python:S8572` usar `logging.exception()` | 2 | `almacen_documentos_disco.py:75,80` | **Real**, trivial. Conserva la traza al fallar un guardado. |
| `python:S3358` / `javascript:S3358` ternarios anidados | 3 | `predecir_consulta.py:45,53`, `App.jsx:143` | **Real de estilo**; arreglo barato. |
| `javascript:S6819` roles `status` y `meter` | 4 | `App.jsx:79`, `PanelPrediccion.jsx:172,220`, `Probabilidad.jsx:14` | **Discutible.** Sonar prefiere `<output>` y `<meter>`; el rol ARIA explícito es válido y conserva el estilo. Aceptable, o cambio de bajo riesgo. |
| `python:S107` 14 parámetros en `__init__` | 1 | `consultar_corpus.py:74` | **Aceptable con justificación**: es inyección de dependencias en un único punto de composición; agrupar los parámetros del PMV2 en un objeto es mejora, no defecto. |
| `python:S9073` aserción compuesta | 29 | pruebas (14 en `test_verificar_entorno_demo.py`, 4 en `test_pasos_de_resolver.py`, el resto en 7 archivos más) | **Aceptable**: preferencia de estilo en pruebas; `a and b` en un `assert` sigue fallando igual. Se puede excluir la regla para `backend/tests/**`. |
| `python:S5778` `pytest.raises` con más de una llamada | 2 | `test_repositorio_consultas_postgres.py:89`, `test_ingesta_guarda_pdf.py:47` | **Aceptable** (menor): acotar el bloque a la llamada que debe fallar. |
| `javascript:S9020` `waitFor` + `getByTestId` | 1 | `PanelPrediccion.test.jsx:103` | **Aceptable** (menor). |

Totales: 4 reales (S3776 ×2, S8572 ×2) + 3 de estilo reales (S3358) = 7 a corregir; 4 discutibles + 1 aceptable-con-justificación (S6819, S107) = 5; 32 aceptables (S9073, S5778, S9020). 7 + 5 + 32 = 44.

## Verificación por foco

1. **El refactor de `_resolver` no cambia el comportamiento.**
   - Lectura línea a línea de los 6 pasos extraídos frente al código anterior: mismas condiciones, mismo orden de trazas y mismas respuestas (incluida la rama léxica sin pasajes, el filtro del predictor de pasajes y la plantilla literal ante `GeneradorNoDisponible`).
   - **Arnés de 248 consultas reejecutado en la rama del PR:** `arnes_por_consulta.csv` y `barrido_umbral.csv` **idénticos byte a byte** a la línea base 2980a81 (τ = 0,48 intacto).
   - **RN-06:** `evaluar_pmv2` en la rama → RN-06 = `True`, falsos positivos en C = 0. Los 12 tests nuevos (`test_pasos_de_resolver.py`, varios marcados `salvaguarda`) cubren que el predictor solo añade abstenciones (incluida la abstención de la regla con p = 0,99), el respaldo por lema y por similitud, y el fallo del generador.
2. **Middleware de cabeceras y CSP.** Probado con la interfaz compilada servida por el propio backend (Chromium de Playwright, base temporal): la SPA carga, consulta y abre «Predicción ML» con **0 violaciones de CSP** (`securitypolicyviolation`) y 0 errores de consola; `index.html` solo trae un `<script type="module" src>` propio y el CSS no usa fuentes ni `url(data:)`. `/docs` responde 200 sin CSP y **Swagger carga las operaciones** (CDN). Las respuestas de `/api` llevan `nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy`, `Cache-Control: no-store`, `Cross-Origin-Resource-Policy: same-origin`. La CSP permite `style-src 'unsafe-inline'` (estilos en línea de React; aceptable en una app local). Pruebas del PR 4/4.
3. **`sonar-project.properties`.** Sin token ni secretos (solo se cita `SONAR_TOKEN`); `sources`/`tests` reflejan `backend/` y `frontend/`; `test.inclusions` separa las pruebas aunque `frontend/src` esté en ambos; exclusiones razonables (datos, modelos, interfaz compilada, `node_modules`). El análisis real lo confirma (cobertura nueva 84,9 %). Ver hallazgo 4.

## Estado de reglas
RN-01…RN-10: cumplen (comportamiento idéntico). RS-01…RS-08: cumplen; RS-03 con la salvedad de `/docs` (hallazgo 3).

## Veredicto: **apto** para revisión humana, con el mayor 1 (puerta roja) a resolver o a aceptar por escrito. 0 bloqueantes · 1 mayor · 4 menores.


## Re-auditoría de #11 (commits 616116f, f4b4fce, 06ab5eb y 72e8781, 2026-10-29)

- **Puerta de calidad (Web API, SonarQube Community local): OK.** `new_coverage` 86,8 %, `new_duplicated_lines_density` 0,0 %, `new_security_hotspots_reviewed` OK, `new_violations` 0. Medidas globales: 0 bugs, 0 vulnerabilidades, 0 hotspots, calificaciones «A», cobertura Python 78,5 %, duplicación 0,7 %, 30 code smells abiertos (todos anteriores a este cambio, en código no nuevo). **Hallazgo 1 (mayor): cerrado.**
- **Issues aceptados:** 40 en estado `ACCEPTED`, **los 40 con un comentario** (python:S9073 ×35, S5778 ×2, S107 ×1, javascript:S9020 ×1, S6819 ×1). Coincide con `excepciones_sonar.md`. Justificación razonable: son estilo en pruebas (aserciones compuestas, `pytest.raises` con construcción y llamada de un único caso), la inyección de 14 colaboradores en el único punto de composición (se revisa en el PMV3) y el `role="meter"` con atributos ARIA, porque el `<meter>` nativo no admite la marca del umbral τ. Las reales se corrigieron (S3776 ×2, S8572 ×2, S3358 ×9, S6819 ×7, S7776, S1192, S5779). Nota menor: el `<meter>` no se justifica con una prueba de accesibilidad; basta con la ya existente de Vitest.
- **CSP sin `'unsafe-inline'`: correcto.** La política es ahora `style-src 'self'`. Probé la interfaz compilada servida por el propio backend con Chromium (Playwright) recorriendo consulta, «Predicción ML», «Fuentes del corpus» e «Incorporar documentos»: **0 eventos `securitypolicyviolation` y 0 errores de consola**; React aplica los estilos por CSSOM, que la CSP permite. `/docs` responde 200 sin CSP y **Swagger sigue cargando las operaciones**. La E2E `csp.real.spec.js` comprueba la cabecera (`style-src 'self';` y ausencia de `unsafe-inline`), recorre la interfaz y exige 0 violaciones. No pude ejecutar la batería E2E completa porque los puertos 8000-8002 y 5173-5175 estaban ocupados por otra ejecución en curso (no la detuve); la prueba equivalente que ejecuté por mi cuenta pasa. Observación menor: `csp.real.spec.js` se **omite** (`test.skip`) si no existe `backend/interfaz`, de modo que en un entorno sin compilar la interfaz pasaría en silencio.
- **ZAP (`zap_antes.json` y `zap_despues.json`):** antes, 1 alerta media (`CSP: style-src unsafe-inline`, 4 instancias) y 1 informativa; después, **0 medias** y solo la informativa «Modern Web Application». Es un escaneo base pasivo (automation framework: OpenAPI, spider, spiderAjax y análisis pasivo), sin escaneo activo; el resumen enumera alertas pero no incluye el informe bruto. Coherente con mi comprobación de CSP. Un escaneo activo sigue pendiente.

**Veredicto de la re-auditoría: apto** (0 bloqueantes · 0 mayores · menores 2 a 5 anteriores, sin cambios, más la omisión silenciosa de la E2E de CSP).
