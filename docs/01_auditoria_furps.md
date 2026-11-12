# 01 · Auditoría FURPS+ — Asistente de consulta del quechua wanka (versión web)

| Dato | Valor |
|---|---|
| Fecha | 2026-11-12 |
| Rama y commit auditados | `s13/furps-owasp`, idéntica a `main` `1d0b129` |
| Alcance | Versión web: backend FastAPI hexagonal (`backend/src`), frontend React + Vite (`frontend/src`), despliegue Render + Neon + Gemini (`render.yaml`), CI (`.github/workflows`), documentación (`docs/`) |
| Rol | Auditor independiente. No se modificó ningún archivo salvo este informe; no se generó código ni plan de implementación |
| Método | Lectura de código con referencia `ruta:línea`, ejecución local de pruebas (solo lectura), consultas `GET` y `curl -sI` contra la nube, y reutilización de las mediciones ya registradas en la U3 (`docs/17_REPORTE_METRICAS_U3.md`, `docs/16_REPORTE_DESPLIEGUE_NUBE.md`, `docs/evidencias/cierre_u3/`) |
| Restricciones respetadas | Ninguna operación de escritura contra la nube; no se enviaron `POST /api/consultas` ni `/api/predicciones`. Lo que escribe se demuestra por código. Ningún secreto se imprimió |
| Fuera de alcance | Arnés de 248 consultas (el corpus `backend/data/fragmentos_v3.jsonl` no está en esta máquina): se citan los resultados de la U3. Aplicación móvil y ejecutable de escritorio |

---

## 1. Resumen ejecutivo

El sistema cumple su función central con evidencia sólida: recupera, cita documento y página, y se
abstiene sin falsos positivos con τ = 0,48 (arnés U3: 0 FP en 28 consultas fuera de cobertura;
paridad local-nube 0 decisiones distintas en 248). La arquitectura hexagonal está bien separada, la
cobertura de pruebas es alta y la degradación del generador (Gemini → fragmento literal citado) está
resuelta por diseño. La salvaguarda (τ, RN-06, verificador de forma literal, ADR-028) no presenta
ninguna brecha en esta auditoría.

Las brechas se concentran en **la frontera pública de la versión en la nube**, que el código no
distingue de la versión local de escritorio para la que se diseñó:

1. **Operaciones de escritura y borrado sin autorización.** Cualquier visitante anónimo puede borrar
   todo el historial de la base compartida —incluidas las consultas `carga` y `humo` que sostienen
   HU-09—, registrar, modificar o eliminar fuentes, subir PDF de hasta 60 MB y forzar un reindexado.
   Contradice la restricción declarada «consulta pública de solo lectura» (R-01, PLUS-01).
2. **Arranque en frío sin aviso.** El plan free de Render duerme el servicio; la U3 midió 62–72 s y
   la interfaz no informa de ello, sino que muestra «Sin conexión con el servicio local» (R-02, U-01).
3. **Historial compartido entre visitantes.** Cada visitante ve las consultas de los demás (U-03).
4. **Sin límite de peticiones** ni control de concurrencia en un servicio de 512 MB con una cuota
   gratuita de Gemini compartida (P-01, R-03).

**Puntaje global: 6,9 / 10.** Funcionalidad y soportabilidad son altas; confiabilidad, rendimiento y
restricciones de despliegue bajan por los riesgos propios de exponer públicamente un diseño local.

---

## 2. Puntaje por categoría

Escala 0–10. El puntaje parte del cumplimiento verificado y descuenta según severidad de los hallazgos
(crítica −1,5 · alta −1 · media −0,5 · baja −0,25, con techo y criterio del auditor).

| Categoría | Puntaje | Fortaleza principal | Brecha principal |
|---|---:|---|---|
| **F** Functionality | **8,0** | RF-03 a RF-08 verificados con arnés y paridad local-nube | HU-09 sin demanda real suficiente; corpus de Neon con 2 PDF de prueba |
| **U** Usability | **6,5** | axe-core 0 infracciones, validación 1–300 coherente cliente/servidor, aviso de privacidad de Gemini | Sin aviso de arranque en frío; mensajes «servicio local» en la nube; historial ajeno visible |
| **R** Reliability | **6,0** | Degradación del generador y de la base sin caída del servicio | Borrado anónimo de toda la tabla `consultas`; arranque en frío; 429 de Gemini |
| **P** Performance | **6,5** | Recuperación 5,2 ms; P50 nube 923–944 ms con Gemini, 192 ms en abstención | Sin límite de peticiones; ingesta y reindexado síncronos en la petición en un plan de 512 MB |
| **S** Supportability | **8,5** | Hexagonal con pruebas de arquitectura; 371 pruebas, 89,9 %; radon CC 2,55; 30 ADR | Pruebas dependientes del corpus fuera de Git; configuración muerta; `main.py` sin cobertura unitaria |
| **+** Restricciones (diseño, implementación, interfaz, físicas/despliegue) | **6,0** | Secretos fuera de Git (`sync: false`), CSP estricta en la API, CI verde como condición de despliegue | Escritura sin autorización; frontend estático sin CSP; límites del plan free sin mitigación |
| **Global** (media simple) | **6,9** | | |

---

## 3. Hallazgos

### 3.1 Tabla de hallazgos

| ID | Sev. | Categoría | Hallazgo (una línea) |
|---|---|---|---|
| R-01 | **Crítica** | R | `DELETE /api/historial` anónimo borra **toda** la tabla `consultas` (usuario, carga, humo, arnés) en Neon |
| PLUS-01 | **Crítica** | + | Endpoints de escritura de corpus y fuentes públicos sin autorización, contra la restricción «solo lectura» |
| R-02 | Alta | R | Arranque en frío de 62–72 s (U3) sin mecanismo de mantenimiento en caliente (REF-01) |
| U-01 | Alta | U | La interfaz no avisa del arranque en frío (REF-02) y muestra «Sin conexión con el servicio local» |
| U-03 | Alta | U | El historial muestra las consultas de todos los visitantes y de las pruebas; el borrado se presenta como local |
| P-01 | Alta | P | Sin límite de peticiones ni de concurrencia en un servicio free de 512 MB con cuota Gemini compartida |
| R-03 | Media | R | Gemini devuelve 429 en 2/20 consultas; la cuota se agota sin control de abuso (la degradación sí es correcta) |
| R-04 | Media | R | `limite` del historial y `top` de la demanda sin validar: un valor negativo produce un error 500 en PostgreSQL |
| R-05 | Media | R | PDF incorporados en la nube se guardan en el disco efímero de Render; sus fragmentos persisten en Neon |
| F-01 | Media | F | HU-09 sin demanda real suficiente: 36 consultas `usuario` frente a 1 273 sintéticas |
| F-02 | Media | F | El corpus público de Neon incluye 2 PDF de prueba (10 documentos, 3 607 fragmentos) |
| U-02 | Media | U | Textos de error y de estado pensados para escritorio («servicio local», «este equipo») en la versión web |
| P-02 | Media | P | Ingesta de PDF (≤ 60 MB) y reindexado completo se ejecutan dentro de la petición HTTP |
| PLUS-02 | Media | + | El frontend estático no envía CSP; la API no envía HSTS |
| PLUS-03 | Media | + | Restricciones físicas del plan free (suspensión a 15 min, 512 MB, cuota Gemini) asumidas sin mitigación |
| S-01 | Media | S | 16 pruebas se omiten sin corpus/PostgreSQL; `infrastructure/main.py` 0 % en la corrida unitaria |
| F-03 | Baja | F | PF-01 a PF-17 no están definidas en el repositorio (solo PF-18) |
| U-04 | Baja | U | Pestañas sin semántica `tablist`/`aria-selected` |
| U-05 | Baja | U | La subida de PDF no usa el cliente común (`pedir`): sin tiempo máximo ni mensajes homogéneos |
| P-03 | Baja | P | `borrar_todo` en SQLite carga y borra fila a fila; recuperación por producto disperso lineal |
| S-02 | Baja | S | Configuración y código muertos: `TRADUCTOR` en `render.yaml` sin efecto; `OllamaTraductor` sin cablear |
| S-03 | Baja | S | `pytest` declarado en `requirements.txt` de producción |
| S-04 | Baja | S | Las propuestas REF-01/REF-02 de la experta no constan en el repositorio |
| PLUS-04 | Baja | + | CORS con `allow_credentials=True` y métodos/cabeceras `*` (mitigado: lista de orígenes cerrada) |

### 3.2 Functionality (F)

**Implementado y verificado** (evidencia de la U3, no repetida):

| Capacidad | Requisito | Evidencia |
|---|---|---|
| Consulta en lenguaje natural, recuperación híbrida léxica | RF-03, RF-05 | `consultas_controller.py:31-63`; arnés A 120/120, B 60/60 (`docs/17` M-06) |
| Consulta en inglés por tabla de traducción | RF-04, HU-05 | D 40/40, declarado techo (`docs/17` §5) |
| Abstención con τ = 0,48 | RF-08, HU-06 | C 0 FP en 28, similitud máx. en C 0,4698 (M-06); nube 0 FP (N-08) |
| Trazabilidad documento y página | RF-07, HU-07 | `esquemas.py:17-28` (`documento`, `pagina` obligatorios) |
| Redacción verificada (forma literal) | ADR-028 | `generador_extractivo.py:36-54`; Qwen extractiva 0/103 (M-23); Gemini contradicción 0/16 (N-04) |
| Historial | RF-11 | `historial_controller.py:14-42` |
| Gestión de corpus y fuentes (CRUD, ingesta, reindexado) | RF-01, RF-02, RF-13 | `corpus_controller.py:34-105`, `fuentes_controller.py:30-84` |
| Predicción de cobertura y pasajes | RF-14, RF-15 | AUC 0,9961 y 0,9804 (M-07, M-08); `prediccion_controller.py:17-33` |
| Demanda insatisfecha | RF-16, HU-09 | `prediccion_controller.py:36-47`; rotulado como demostración |

**Parcial o ausente.**

- **F-01 (media).** HU-09 depende de la demanda real. `GET /api/estado` del 2026-11-12 devuelve
  `"consultas_por_origen":{"carga":1005,"humo":268,"usuario":36}` y `"base_demostracion":true`. La U3
  fijó el mínimo en 100 (`docs/17` M-27, HU-09 «insuficiente: 13 < 100»); hoy son 36. El sistema lo
  rotula correctamente (`App.jsx` aviso `base-demostracion`), pero la funcionalidad no está cubierta
  con datos reales.
- **F-02 (media).** La misma respuesta muestra `"documentos_corpus":10` y `"fragmentos_indexados":3607`
  frente a 8 documentos y 3 605 fragmentos del corpus v3. `docs/17` §1 identifica los dos PDF de
  prueba (`documento_control_guia11.pdf`, `prueba_qa_tp1.pdf`) y su efecto en el IDF (diferencia de
  similitud máx. 0,0035, N-08). El corpus público consultable contiene material que no es fuente
  publicada.
- **F-03 (baja).** `docs/17` §6: «El repositorio solo define PF-18»; PF-01 a PF-17 «por registrar».

### 3.3 Usability (U)

**Fortalezas verificadas.** axe-core 0 infracciones WCAG 2 A/AA en 4 vistas y 0 objetivos < 44 px
(M-22). Validación idéntica en cliente (`validacion.js:1-9`) y servidor (`esquemas.py:6-14`). Errores
con `role="alert"` y botón «Reintentar» (`App.jsx:159-170`). Indicador de carga (`App.jsx:171-175`).
Control de tamaño de texto con `aria-label` (`TamanoTexto.jsx:5-27`). Aviso de envío a Google cuando
redacta Gemini (`App.jsx:135-140`). Medidor de similitud frente a τ con `role="meter"`
(`Respuesta.jsx:19-23`).

- **U-01 (alta) — sin aviso de arranque en frío (REF-02).** Búsqueda:
  `grep -rniE "arranque|despert|fr[ií]o|cold|render|tarda" frontend/src --include=*.js* | grep -v test`
  → solo `api.js:15` (comentario sobre la CPU local) y `main.jsx:6` (`render(`). No existe ningún
  texto que avise al visitante. Durante la espera, `obtenerEstado()` puede tardar hasta
  `TIEMPO_MAXIMO_MS = 180000` (`api.js:16`) y, si falla, la interfaz muestra
  «Sin conexión con el servicio local» (`App.jsx:41`, `EstadoInicial.jsx:20`).
- **U-02 (media) — mensajes de escritorio en la web.** `api.js:44` «No se pudo conectar con el
  servicio local. Comprueba que esté en marcha.»; `EstadoInicial.jsx:20` «Compruebe que la aplicación
  esté en marcha»; `Historial.jsx:15` «¿Borrar todo el historial de consultas de este equipo?». En la
  nube el visitante no puede «poner en marcha» nada y el borrado no es de «este equipo».
- **U-03 (alta) — historial compartido.** `historial()` ordena por fecha toda la tabla sin filtrar por
  origen ni por visitante (`repositorio_consultas_sqlalchemy.py:61-66`; `RepositorioConsultasPostgres`
  hereda ese método, `repositorio_consultas_postgres.py:36`). El texto de `Historial.jsx:36` lo
  reconoce («compartida por todos los visitantes»), pero el visitante ve consultas ajenas y de prueba,
  y el confirm de `Historial.jsx:15` las presenta como propias. Riesgo de privacidad (se profundiza en
  la fase OWASP).
- **U-04 (baja).** `Pestanas` (`App.jsx:23-37`) usa `<nav>` con `<button>` sin `role="tablist"`,
  `role="tab"` ni `aria-selected`; el estado activo solo se expresa por clase CSS. axe-core no lo marca
  como infracción, pero un lector de pantalla no anuncia la pestaña activa.
- **U-05 (baja).** `ingestarDocumento` (`api.js:95-109`) llama a `fetch` directamente: sin
  `AbortController`, sin clasificación del error y con un `Error` genérico, a diferencia del resto de
  llamadas (`api.js:26-68`).

### 3.4 Reliability (R)

**Fortalezas verificadas.** Sin base de datos el servicio sigue respondiendo (`contenedor.py:313-321`);
si no se puede registrar una consulta, se responde igual (`consultar_corpus.py:440-450`); si el
generador falla, se devuelve el fragmento literal citado con aviso (`consultar_corpus.py:308-314`;
`gemini_generador.py:134-146` traduce tiempo agotado, red, 429 y HTTP ≥ 400 a `GeneradorNoDisponible`);
JSON inválido del modelo → fragmento literal (`generador_extractivo.py:36-39`). Pool con
`pool_pre_ping` y `pool_recycle=300` para Neon (`contenedor.py:271-281`). `healthCheckPath: /api/estado`
(`render.yaml`). Ingesta con tope de 60 MB leída por bloques (`corpus_controller.py:14-27`).

- **R-01 (crítica) — borrado anónimo de todo el historial.** Cadena verificada por código:
  `historial_controller.py:35-42` (`DELETE /api/historial`, sin dependencia de autorización) →
  `RepositorioConsultasPostgres.borrar_todo` → `CALL sp_borrar_historial(0)`
  (`repositorio_consultas_postgres.py:76-78`) → `DELETE FROM consultas;`
  (`backend/db/postgres/procedimientos.sql:79-86`). No filtra por origen: borra también las 1 005
  `carga`, 268 `humo` y 36 `usuario` actuales, que son los datos de HU-09, la evidencia N-08/M-27 y el
  rótulo `base_demostracion`. La interfaz pública lo ofrece a cualquier visitante con un único
  `window.confirm` (`Historial.jsx:14-31`). No se ejecutó contra la nube, por regla.
- **R-02 (alta) — arranque en frío.** U3: 72,39 s y 62,37 s tras 16 min de inactividad (`docs/17`
  N-01). Medición de esta auditoría:
  `curl -s -o /dev/null -w "estado http=%{http_code} t=%{time_total}s\n" https://quechua-api.onrender.com/api/estado`
  → `estado http=200 t=21.401064s` (primera petición del día de la auditoría; no se controló el tiempo
  de inactividad previo, de modo que no sustituye a N-01). En el repositorio no existe ningún ping
  programado ni flujo de mantenimiento en caliente (REF-01): `.github/workflows` solo contiene la CI.
  Mientras tanto, `precalentar()` de Gemini es un `return True` (`gemini_generador.py:148-149`).
- **R-03 (media) — cuota de Gemini.** 429 en 2/20 con 5 s de pausa (`docs/17` N-04). El contador
  `errores_429` (`gemini_generador.py:62,139`) no se expone ni limita nada. Sin límite de peticiones
  (P-01) cualquier cliente puede agotar la cuota del servicio para todos; la salvaguarda no se ve
  afectada porque se degrada al literal.
- **R-04 (media) — parámetros sin acotar.** `limite: int = 50` (`historial_controller.py:16`) y
  `top: int = 15` (`prediccion_controller.py:38`) no tienen `ge`/`le`. `limite` llega a
  `.limit(limite)` (`repositorio_consultas_sqlalchemy.py:64`); en PostgreSQL un `LIMIT` negativo es un
  error de la base que FastAPI devuelve como 500. Demostrado por código; no ejecutado contra la nube.
- **R-05 (media) — almacenamiento efímero.** `carpeta_datos` es `backend/data/` fuera del ejecutable
  (`config.py:19-23,98`) y `ruta_documentos` cuelga de ella (`config.py:122-124`); en Render ese disco
  se pierde en cada despliegue o reinicio, mientras los fragmentos van a Neon (`CORPUS_ORIGEN=postgres`).
  El verificador de consistencia solo informa (`contenedor.py:237-245`); hoy reporta `"estado":"ok"`.
  Efecto concreto en la nube: por medir.

### 3.5 Performance (P)

**Fortalezas verificadas.** Recuperación 5,2 ms sobre 3 605 fragmentos (línea base); predicción P50
6,11 ms (M-11). Nube despierta: `consultas` con Gemini P50 923–944 ms, P95 977–1 048 ms; abstención
P50 192 ms (N-02); `/api/predicciones` P50 158 ms (N-03). Carga HTTP local 0 % errores hasta 10
usuarios (M-16, no repetida en el último commit). RAM de la API 215 MiB frente a 512 MB del plan (N-09,
medido en local). `/api/estado` no gasta cuota de Gemini (`gemini_generador.py:151-153`).

- **P-01 (alta) — sin límite de peticiones.** `grep -rn "slowapi|RateLimit|rate_limit|limiter" backend/src backend/requirements*.txt`
  → sin resultados. Uvicorn con un solo proceso (`render.yaml` `startCommand`), pool de 3+2 conexiones
  (`contenedor.py:276-277`). La carga de 500 en la nube dio 2,22 tps (N-10). No hay protección frente a
  ráfagas ni frente a peticiones costosas (P-02).
- **P-02 (media) — trabajo pesado en la petición.** `POST /api/corpus/documentos` lee hasta 60 MB en
  memoria (`corpus_controller.py:18-27,49`), extrae y segmenta y reconstruye el índice en el mismo
  hilo (`ingestar_documento.py:41-83`); `POST /api/corpus/reindexar` reindexa todo el corpus
  (`reindexar_corpus.py:18-22`). En 512 MB y CPU compartida, combinado con PLUS-01, es un vector de
  agotamiento. Consumo real en Render: por medir.
- **P-03 (baja).** `borrar_todo` del adaptador SQLAlchemy materializa todas las filas y las borra una a
  una (`repositorio_consultas_sqlalchemy.py:68-75`); en PostgreSQL se usa el procedimiento, sin ese
  coste. La recuperación es un producto disperso exhaustivo (`indice_hibrido_lexico.py:134-135`),
  adecuado para 3 607 fragmentos; su crecimiento es lineal (RNF-12): por medir con un corpus mayor.

### 3.6 Supportability (S)

**Fortalezas verificadas.**

- Hexagonal real: `domain/` sin dependencias de terceros, puertos de entrada y salida en
  `application/ports/{in,out}`, controladores que solo dependen de puertos (`adapters/in/rest/__init__.py:1-5`,
  `dependencias.py:1-5`) y pruebas de arquitectura (`backend/tests/architecture/`). Adaptadores
  intercambiables por variable de entorno (`config.py:43-93`).
- Pruebas, medición de esta auditoría (sin corpus ni PostgreSQL):
  `backend/.venv/Scripts/python.exe -m pytest -q -p no:cacheprovider --cov=src`
  → `355 passed, 16 skipped, 2 warnings in 151.20s`, `TOTAL 2423 286 88%`.
  `npx vitest run` → `Test Files 6 passed (6) · Tests 34 passed (34)`.
  Coinciden con la U3 una vez descontadas las 16 omitidas (U3 con PostgreSQL: 371 y 89,9 %, M-01/M-02).
- Calidad estática U3: radon CC media 2,55, ninguna función D/E/F (M-17); SonarQube Passed, 0 bugs,
  0 vulnerabilidades, duplicación 0,6 % (M-20); Bandit 0 altos/medios (M-18); pip-audit y npm audit 0
  (M-19). E2E 21/21 (M-04), Newman 39/39 local y nube (M-05, N-05). CI con pytest + pip-audit + vitest +
  build como condición de despliegue (`autoDeployTrigger: checksPass`).
- Documentación: 30 ADR en `docs/07_DECISIONES.md` (408 líneas), `README.md`, `docs/INSTALACION.md`,
  reportes de despliegue y métricas con rutas de evidencia.

**Brechas.**

- **S-01 (media).** 16 pruebas se omiten sin `fragmentos_v3.jsonl` ni PostgreSQL (ADR-015: el corpus no
  está en Git), de modo que un tercero no puede reproducir el arnés. `infrastructure/main.py` aparece
  con 40 sentencias y 0 % en la corrida unitaria (las pruebas montan su propia app): el cableado real de
  middlewares y montaje estático solo lo cubren E2E/Newman. La CI no fija umbral de cobertura ni ejecuta
  `oxlint` aunque exista el script (`frontend/package.json` `"lint": "oxlint"`).
- **S-02 (baja).** `render.yaml` declara `TRADUCTOR: tabla`, pero `Configuracion` no tiene ese campo
  (`extra="ignore"`, `config.py:39-41`) y el contenedor fija `TraductorTabla` (`contenedor.py:112`).
  `adapters/out/traduccion/ollama_traductor.py` solo lo usan dos scripts, no el contenedor.
- **S-03 (baja).** `pytest==9.2.0` en `backend/requirements.txt` (dependencia de producción).
- **S-04 (baja).** `grep -rn "REF-0[0-9]" docs --include=*.md` → sin resultados: las propuestas de la
  experta (REF-01 ping, REF-02 aviso) no constan en el repositorio (`docs/17` §8 lo deja «para personas»).

### 3.7 «+» Restricciones de diseño, implementación, interfaz y despliegue

**Cumplido.** Secretos fuera de Git (`render.yaml` `sync: false`; `TOKEN_PRUEBAS` con
`generateValue`); la clave BYOK viaja solo en cabecera y caduca con la petición
(`seguridad.py:32-55`, `api.js:6-13`); el token de pruebas se compara en tiempo constante
(`seguridad.py:76-81`). Cabeceras de la API verificadas con `curl -sI https://quechua-api.onrender.com/api/estado`:
`content-security-policy: default-src 'self'; …`, `x-frame-options: DENY`, `x-content-type-options: nosniff`,
`referrer-policy: no-referrer`, `Cache-Control: no-store`. Umbral τ como parámetro (`config.py:75`;
`/api/estado` → `"umbral_abstencion":0.48`). Licencias libres; plan sin coste.

- **PLUS-01 (crítica) — restricción «solo lectura» no implementada.** El servicio público registra
  sin ninguna dependencia de autorización: `POST/PUT/DELETE /api/fuentes` (`fuentes_controller.py:30-84`),
  `POST /api/corpus/documentos` (`corpus_controller.py:34-92`), `POST /api/corpus/reindexar`
  (`corpus_controller.py:101-105`) y `DELETE /api/historial` (R-01). Los únicos middlewares son BYOK,
  token de pruebas (que solo rotula el origen) y cabeceras (`main.py:46-55`). La interfaz pública los
  ofrece como pestañas («Fuentes del corpus», «Incorporar documentos», `App.jsx:16-21`). El
  `openapi.json` público los documenta (`curl … /openapi.json` → `http=200`). Un tercero puede alterar
  el corpus que el sistema cita como fuente documentada.
- **PLUS-02 (media).** `curl -sI https://quechua-web.onrender.com/` → solo `x-content-type-options`,
  `x-frame-options` y `strict-transport-security`; **sin `content-security-policy`** (las cabeceras del
  sitio estático vienen de `render.yaml`, que solo declara las dos primeras). La API no envía
  `strict-transport-security` en la misma comprobación. La CSP estricta probada por ZAP (M-21) era la
  del servicio local que sirve la interfaz, no la del sitio estático de la nube.
- **PLUS-03 (media).** Restricciones físicas del plan free asumidas sin mitigación registrada en el
  repositorio: suspensión por inactividad (R-02), 512 MB (P-02), cuota Gemini (R-03), región única
  `virginia`. N-09: memoria en Render «por medir».
- **PLUS-04 (baja).** `CORSMiddleware` con `allow_credentials=True`, `allow_methods=["*"]`,
  `allow_headers=["*"]` (`main.py:49-55`). Mitigado: preflight desde `Origin: https://evil.example`
  → `HTTP/1.1 400 Bad Request` sin `access-control-allow-origin`. La API no usa cookies, de modo que
  `allow_credentials` es innecesario.

---

## 4. Evidencias

### 4.1 Comandos ejecutados en esta auditoría

| # | Comando (resumen) | Salida relevante |
|---|---|---|
| E-01 | `curl -s -w "%{http_code} %{time_total}" https://quechua-api.onrender.com/api/estado` | `http=200 t=21.401064s` |
| E-02 | `curl -s https://quechua-api.onrender.com/api/estado` | `fragmentos_indexados 3607`, `documentos_corpus 10`, `consultas_por_origen {carga 1005, humo 268, usuario 36}`, `base_demostracion true`, `generador gemini`, `umbral 0.48` |
| E-03 | `curl -sI …/api/estado` | `405` en HEAD; CSP, XFO, nosniff, no-referrer, `no-store`; sin HSTS |
| E-04 | `curl -sI https://quechua-web.onrender.com/` | sin CSP; con HSTS, XFO, nosniff |
| E-05 | `curl -sI -X OPTIONS -H "Origin: https://evil.example" …/api/historial` | `400`, sin `access-control-allow-origin` |
| E-06 | `curl -s -o /dev/null -w "%{http_code}" …/openapi.json` | `200` |
| E-07 | `pytest -q --cov=src` (local, sin corpus) | `355 passed, 16 skipped`; cobertura 88 %; `main.py` 0 % |
| E-08 | `npx vitest run` | `34 passed (34)` |
| E-09 | `grep` de aviso de arranque en frío en `frontend/src` | sin coincidencias funcionales |
| E-10 | `grep` de limitador de peticiones en backend | sin coincidencias |

`docs/evidencias/s13_furps_owasp/antes/salidas/` contiene `arranque_estado_antes.txt` y
`pytest_antes.txt`, **ambos vacíos (0 bytes)** al cierre de esta auditoría: conviene volcar en ellos
E-01/E-02 y E-07.

### 4.2 Evidencias de la U3 reutilizadas

`docs/17_REPORTE_METRICAS_U3.md` (M-01 a M-27, N-01 a N-10), `docs/16_REPORTE_DESPLIEGUE_NUBE.md`,
`docs/07_DECISIONES.md`, `docs/evidencias/cierre_u3/99_final_c61f52b/` y
`docs/evidencias/nube/metricas_u3/`.

### 4.3 Capturas «antes» propuestas (hallazgos críticos y altos)

Carpeta: `docs/evidencias/s13_furps_owasp/antes/`.

| Archivo sugerido | Hallazgo | Qué debe verse |
|---|---|---|
| `01_R_borrado_historial_sin_autorizacion_codigo.png` | R-01 | `historial_controller.py:35-42` junto a `procedimientos.sql:79-86` (`DELETE FROM consultas;`) |
| `02_R_boton_borrar_historial_publico.png` | R-01 | La web pública con el botón «Borrar historial» y el confirm «de este equipo» (sin pulsar «Aceptar») |
| `03_PLUS_endpoints_escritura_swagger_nube.png` | PLUS-01 | `https://quechua-api.onrender.com/docs` con `POST/PUT/DELETE /api/fuentes`, `POST /api/corpus/*`, `DELETE /api/historial` sin candado |
| `04_PLUS_pestanas_admin_publicas.png` | PLUS-01 | Pestañas «Fuentes del corpus» e «Incorporar documentos» en la web pública |
| `05_PLUS_middlewares_sin_autorizacion_codigo.png` | PLUS-01 | `main.py:46-55`: solo BYOK, token de pruebas, cabeceras y CORS |
| `06_R_arranque_frio_medicion.png` | R-02 | Terminal con `curl -w time_total` tras ≥ 15 min de inactividad (o `arranque_frio*.json` de la U3) |
| `07_U_sin_aviso_arranque_frio_web.png` | U-01 | Web pública durante el arranque en frío: «Sin conexión con el servicio local» y sin aviso de espera |
| `08_U_sin_aviso_arranque_frio_codigo.png` | U-01 | Salida del `grep` E-09 y `EstadoInicial.jsx:17-24` |
| `09_U_historial_compartido.png` | U-03 | Historial público con consultas ajenas o de prueba, y `repositorio_consultas_sqlalchemy.py:61-66` |
| `10_P_sin_limite_peticiones_grep.png` | P-01 | Salida vacía del `grep` E-10 y `requirements.txt` sin limitador |
| `11_PLUS_cabeceras_web_sin_csp.png` | PLUS-02 (media, opcional) | Salida de E-04 frente a E-03 |

---

## 5. Brechas identificadas

| # | Brecha | Requisito o restricción afectada | Hallazgos |
|---|---|---|---|
| B-01 | El modelo de autorización no existe: la versión pública hereda las capacidades de administración del escritorio | Restricción «consulta pública de solo lectura»; RNF-06; RF-13 | PLUS-01, R-01 |
| B-02 | El historial es global, no por visitante ni por sesión | RF-11; RNF-06 (privacidad) | U-03, R-01 |
| B-03 | Disponibilidad del plan free sin mitigación ni comunicación al usuario | RNF-01 (≤ 8 s); RNF-09 | R-02, U-01, PLUS-03 |
| B-04 | Sin protección de capacidad (límite de peticiones, cuota, tamaño de trabajo) | RNF-10; RNF-12 | P-01, P-02, R-03 |
| B-05 | Validación incompleta de parámetros de consulta en GET | Robustez de la API | R-04 |
| B-06 | Integridad del corpus público (PDF de prueba, almacenamiento efímero) | RF-07, RNF-08 | F-02, R-05 |
| B-07 | Datos reales insuficientes para la analítica de demanda | RF-16, HU-09 | F-01 |
| B-08 | Interfaz con textos de escritorio en la web | RNF-09 | U-01, U-02 |
| B-09 | Trazabilidad del plan de pruebas y de las propuestas de la experta | Documentación | F-03, S-04 |
| B-10 | Endurecimiento de cabeceras del sitio estático | RS-03 | PLUS-02 |

---

## 6. Riesgos detectados

Probabilidad (P) e impacto (I) de 1 a 5; exposición = P × I.

| ID | Riesgo | P | I | Exp. | Origen |
|---|---|---:|---:|---:|---|
| RA-01 | Un visitante borra todo el historial y destruye los datos de HU-09 y las evidencias de carga/humo | 3 | 5 | 15 | R-01 |
| RA-02 | Un tercero incorpora un PDF o modifica fuentes y el sistema lo cita como fuente documentada | 3 | 5 | 15 | PLUS-01 |
| RA-03 | El evaluador o usuario abandona durante el arranque en frío creyendo que el servicio está caído | 4 | 3 | 12 | R-02, U-01 |
| RA-04 | Exposición de consultas de otros visitantes que contengan datos personales | 3 | 3 | 9 | U-03 |
| RA-05 | Agotamiento de la cuota de Gemini o de la memoria por ráfagas o subidas de 60 MB | 3 | 3 | 9 | P-01, P-02, R-03 |
| RA-06 | Pérdida de PDF incorporados tras un redespliegue, con fragmentos huérfanos en Neon | 2 | 3 | 6 | R-05 |
| RA-07 | Analítica de demanda presentada sin base real suficiente | 3 | 2 | 6 | F-01 |
| RA-08 | Error 500 con parámetros anómalos en GET | 2 | 2 | 4 | R-04 |

**Salvaguarda.** Ninguno de estos riesgos permite hoy que el sistema emita una forma quechua no
documentada por la vía del generador: τ, RN-06 y el verificador literal actúan antes de cualquier
salida. La excepción indirecta es RA-02: si se altera el corpus, la salvaguarda citaría fielmente un
material que no es fuente publicada.

---

## 7. Recomendaciones de alto nivel

Sin plan de implementación ni código, por restricción del encargo.

1. **Hacer efectiva la restricción de solo lectura en la nube** (PLUS-01, R-01): que las operaciones
   de escritura y borrado dejen de estar disponibles para visitantes anónimos en el entorno público,
   y que la interfaz pública no las ofrezca.
2. **Separar el historial por visitante o retirarlo de la vista pública** (U-03), y que ningún borrado
   afecte a las consultas de prueba ni a los datos de HU-09.
3. **Atender el arranque en frío en las dos caras**: mantener el servicio despierto (REF-01) y avisar
   en la interfaz de la espera esperada (REF-02), con textos propios de la versión web (U-01, U-02).
4. **Proteger la capacidad**: límite de peticiones por cliente y por operación, con especial atención
   a las costosas (Gemini, ingesta, reindexado) (P-01, P-02, R-03).
5. **Acotar los parámetros de entrada** de los GET con valores mínimos y máximos (R-04).
6. **Sanear el corpus público** (retirar los 2 PDF de prueba) y decidir dónde persisten los PDF en la
   nube (F-02, R-05).
7. **Completar cabeceras del sitio estático** (CSP equivalente a la de la API) y HSTS en la API
   (PLUS-02); retirar `allow_credentials` si no se usa (PLUS-04).
8. **Higiene de mantenimiento**: retirar configuración y dependencias muertas (S-02, S-03), registrar
   PF-01 a PF-17 y REF-01/REF-02 en el repositorio (F-03, S-04), y fijar umbral de cobertura y lint en
   la CI (S-01).
9. **Volver a medir tras cada cambio** con las mismas herramientas de la U3 (arnés, RN-06, Newman,
   E2E, ZAP) y, por primera vez, ZAP contra la nube y memoria real en Render (pendientes de `docs/17`
   §6 y N-09).
