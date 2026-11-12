# 04 · Auditoría de seguridad OWASP Top 10 (2021)

**Agente 4: auditor OWASP Top 10.** El informe evalúa el proyecto solo desde la perspectiva de seguridad.
No corrige, no modifica ni implementa controles. Las líneas «Tratamiento sugerido» indican hacia dónde
iría la remediación de la fase 2, sin contenido de código.

| Campo | Valor |
|---|---|
| Fecha | 2026-11-12 |
| Rama auditada | `s13/furps-owasp` (`dbaa6cc`; incluye la fase 1 FURPS+, PR #23) |
| Desplegado en la nube | `main` en `1d0b129` (Render plan free + Neon PostgreSQL + Gemini Flash-Lite) |
| URL | Web `https://quechua-web.onrender.com` · API `https://quechua-api.onrender.com` |
| Alcance | Frontend React/Vite, backend FastAPI hexagonal, API REST, autenticación, autorización, configuración, dependencias, CI e infraestructura declarada (`render.yaml`, `.github/workflows/ci.yml`) |
| Fuera de alcance | Configuración interna de Render y de Neon (compartida, no se modifica), escaneo activo contra la nube, pruebas de carga reales |

---

## 1. Método

### 1.1 Fuentes de evidencia

1. **Revisión de código** con cita `ruta:línea` sobre `backend/src`, `frontend/src`, `render.yaml` y la CI.
2. **Nube: solo lecturas permitidas.** `GET /api/estado`, `GET /docs`, `GET /openapi.json`, `HEAD` y
   `OPTIONS`. **No** se envió ninguna escritura a la nube, ni `POST /api/consultas` ni `POST /api/predicciones`.
3. **Demostraciones locales.** Instancias efímeras en `127.0.0.1:8120` y `127.0.0.1:8121` con
   `BASE_DATOS=sqlite`, base y carpeta de datos en `%TEMP%` y `GENERADOR=literal`. Se detuvieron al
   terminar y no tocaron `backend/data/` ni la nube. Las salidas están en
   `docs/evidencias/s13_furps_owasp/antes/salidas/04_*.txt`.
4. **Herramientas.** `pip-audit` (venv `backend/.venv`), `npm audit` y `npm audit --omit=dev`, y una
   búsqueda de secretos en todo el historial de Git (`git log --all -p`) con salida enmascarada.
5. **Mediciones ya hechas en U3 que no se repiten y se citan** (`docs/17_REPORTE_METRICAS_U3.md`):
   Bandit con 0 altos, 0 medios y 2 bajos (M-18); `pip-audit` con 0 avisos (M-19); SonarQube Passed
   con 0 vulnerabilidades y 0 hotspots (M-20); ZAP pasivo, **solo local**, con 0 altas y 0 medias (M-21);
   axe-core con 0 infracciones (M-22).
   Hallazgos de la auditoría FURPS+ que aquí se reclasifican: `docs/01_auditoria_furps.md`, PLUS-02 y PLUS-04.

### 1.2 Escalas

- **Impacto (I)** y **Probabilidad (P)** de 1 a 5. El impacto pondera la confidencialidad, la
  integridad y la disponibilidad, más el efecto sobre la salvaguarda central del proyecto (ninguna
  forma quechua sin respaldo documental). La probabilidad pondera la exposición (nube pública o solo
  127.0.0.1), la facilidad (una petición `curl` o una cadena de pasos) y si existe evidencia de que el
  riesgo ya se materializó.
- **Severidad = I × P.** Crítico de 20 a 25 · Alto de 10 a 19 · Medio de 5 a 9 · Bajo de 1 a 4.
- **Estado de cada categoría.** *No cumple* (hay un hallazgo alto o crítico) · *Cumple parcialmente*
  (hallazgos medios o bajos) · *Cumple* (sin hallazgos o solo informativos).

### 1.3 Fórmula del score global

Para cada categoría A01 a A10 se calcula `s_c = 10 − (base de la peor severidad + 0,5 × hallazgos
adicionales, con un máximo de 2 puntos adicionales)` y se acota a [0, 10]. Las bases son: Crítico 8,
Alto 5, Medio 3, Bajo 1 y sin hallazgos 0.
**Score global = Σ s_c** (10 categorías × 10 puntos = 100).
El tope de los puntos adicionales evita que una misma causa raíz, como la ausencia de autenticación,
penalice varias veces una categoría. **Regla de veto:** mientras haya un hallazgo **Crítico** abierto,
el sistema se clasifica como *no apto para exposición pública*, sea cual sea el score.

---

## 2. Resumen ejecutivo

**Score global de seguridad: 61,0 / 100. Un hallazgo crítico abierto: no apto para exposición pública.**

La base técnica es sólida. Las consultas SQL van parametrizadas y la escritura pasa por procedimientos
sin SQL dinámico. Los secretos solo existen como variables de Render, y no aparece ninguno en el
historial de Git. El token de pruebas se compara en tiempo constante. La clave BYOK viaja en cabecera
y no se registra. Hay CSP estricta en la API, TLS con redirección 301 y `sslmode=require` hacia Neon.
El verificador literal (ADR-028) neutraliza la inyección de instrucciones hacia Gemini. No hay
ninguna URL controlada por el usuario, así que no hay SSRF.

El problema es de **control de acceso por diseño**. La API pública no tiene autenticación ni
autorización, y expone funciones de administración: incorporar PDF al corpus, reindexar, alterar o
borrar fuentes y borrar el historial. También expone datos de otros usuarios: el historial y la
demanda insatisfecha. La demostración local (OW-01) prueba que un PDF arbitrario subido sin
credenciales **pasa a ser «respaldo documental» citado con documento y página**. Eso anula la
salvaguarda central del proyecto, y en la nube persistiría en la tabla `fragmentos` de Neon. A ello
se suman la ausencia de límite de peticiones (A04) y una lectura arbitraria de archivos en el modo de
escritorio (OW-05).

| Cat. | Categoría OWASP 2021 | Estado | Peor severidad | Hallazgos | s_c |
|---|---|---|---|---|---:|
| A01 | Broken Access Control | **No cumple** | Crítico | OW-01 a OW-05 | 0,0 |
| A02 | Cryptographic Failures | Cumple parcialmente | Bajo | OW-06 | 9,0 |
| A03 | Injection | Cumple parcialmente | Bajo | OW-07 | 9,0 |
| A04 | Insecure Design | **No cumple** | Alto | OW-08, OW-09 | 4,5 |
| A05 | Security Misconfiguration | Cumple parcialmente | Medio | OW-10 a OW-13 | 5,5 |
| A06 | Vulnerable and Outdated Components | Cumple parcialmente | Medio | OW-14, OW-15 | 6,5 |
| A07 | Identification and Authentication Failures | **No cumple** | Alto | OW-16 | 5,0 |
| A08 | Software and Data Integrity Failures | **No cumple** | Alto | OW-17, OW-18 | 4,5 |
| A09 | Security Logging and Monitoring Failures | Cumple parcialmente | Medio | OW-19 | 7,0 |
| A10 | Server-Side Request Forgery | Cumple | — | — | 10,0 |
| | **Total** | | | **19 hallazgos** | **61,0** |

Distribución: **1 crítico · 7 altos · 5 medios · 6 bajos.**

---

## 3. Hallazgos por categoría

### A01 · Broken Access Control: **No cumple** (s_c = 0,0)

Evidencia común. `GET https://quechua-api.onrender.com/openapi.json` declara
`components.securitySchemes = None` y `security = None` en las 16 operaciones, entre ellas `DELETE
/api/historial`, `POST /api/corpus/documentos`, `POST /api/corpus/reindexar` y `POST/PUT/DELETE
/api/fuentes` (`salidas/04_A05_openapi_estado_nube.txt`). La pila de middlewares
(`backend/src/infrastructure/main.py:46-55`) solo instala BYOK, el token de pruebas, las cabeceras y
CORS: ninguno autoriza. Los proveedores de dependencias (`backend/src/adapters/in/rest/dependencias.py:20-68`)
devuelven el puerto sin comprobar la identidad. CORS no es un control de acceso: el preflight de un
origen ajeno da 400 (`salidas/cors_preflight_ajeno_antes.txt`), pero un cliente sin navegador, como
`curl` o un script, ignora CORS.

#### OW-01 · Escritura del corpus sin autorización: envenenamiento del respaldo documental (**Crítico**, I5 × P4 = 20)
- **Evidencia (código).** `backend/src/adapters/in/rest/corpus_controller.py:34-92`
  (`POST /api/corpus/documentos`) y `:101-105` (`POST /api/corpus/reindexar`), sin dependencia de
  autorización. En la nube el corpus vive en Neon (`contenedor.py:84-92`, `CORPUS_ORIGEN=postgres` en
  `render.yaml:30-31`) y la ingesta inserta en la tabla `fragmentos`
  (`repositorio_corpus_postgres.py:26-27, 72-88`). Ninguna ruta elimina después un documento incorporado.
- **Evidencia (local).** `salidas/04_A08_envenenamiento_local.txt`. Antes de la subida, la consulta
  `auditoriaowasp` → abstención (`similitud_maxima 0.0609`). `POST /api/corpus/documentos` sin
  credenciales con un PDF arbitrario → `HTTP 200`, `fragmentos_nuevos: 1`. La misma consulta →
  `abstenida: false`, `similitud_maxima 0.526` (por encima de τ = 0,48), con `respaldo` citando
  `auditoria_owasp.pdf, p. 1` y `coincidencia_lema: true`. `POST /api/corpus/reindexar` → `HTTP 200`.
  El contenido de prueba es una marca no quechua: no se redactó ninguna forma.
- **Evidencia (nube, solo lectura).** `GET /api/estado` informa `documentos_corpus: 10` y
  `fragmentos_indexados: 3607`, frente a los 8 documentos y 3605 fragmentos del corpus base local.
  `docs/17_REPORTE_METRICAS_U3.md:135` registra «2 PDF de prueba en Neon». La vía de escritura pública
  ya se ha usado.
- **Impacto 5.** Cualquiera puede introducir «formas» no documentadas que el sistema servirá como
  respaldo citado con documento y página. Así se anula RN-06 y la salvaguarda central, y se contamina
  el registro de una lengua seriamente en peligro, justo el daño que el proyecto declara evitar. El
  verificador literal (ADR-028) no protege: comprueba la forma contra el fragmento, y aquí el
  fragmento es el envenenado. El cambio persiste en Neon tras reiniciar.
- **Probabilidad 4.** Basta una petición multipart. La interfaz pública ofrece el formulario
  (captura `04_A01_interfaz_incorporar_documentos_publica_nube.png`) y el endpoint aparece en `/docs`.
- **Tratamiento sugerido (sin implementar).** Exigir un rol de administración en la ingesta y en el
  reindexado, desactivarlos en el despliegue público o separarlos en un servicio no expuesto, y
  disponer de un procedimiento para retirar documentos.

#### OW-02 · Borrado del historial de todos los usuarios sin autorización (**Alto**, I3 × P4 = 12)
- **Evidencia.** `backend/src/adapters/in/rest/historial_controller.py:36-43` (`DELETE /api/historial`
  → `puerto.borrar()`). En PostgreSQL ejecuta `CALL sp_borrar_historial(0)`
  (`repositorio_consultas_postgres.py:76-80`). En local, `salidas/04_A01_historial_local.txt` muestra
  `DELETE /api/historial -> HTTP 204` sin credenciales y un historial vacío (`[]`) justo después.
  Captura: `04_A01_delete_historial_sin_auth_codigo.png`.
- **Impacto 3.** Pérdida irreversible, desde la API, del historial (RF-11) y de los datos que
  alimentan la analítica de demanda (HU-09) y el reentrenamiento de los predictores. No afecta al
  corpus ni a la salvaguarda.
- **Probabilidad 4.** Una sola petición sin cuerpo.
- **Tratamiento sugerido.** Limitar el borrado a un rol de administración o al historial propio de la sesión.

#### OW-03 · Lectura de las consultas de todos los usuarios: privacidad (**Alto**, I3 × P4 = 12)
- **Evidencia.** `historial_controller.py:14-33`: `GET /api/historial?limite=500` devuelve el `consulta`
  (texto literal), la respuesta y el momento de **todas** las consultas, sin filtrar por sesión. Por su
  parte, `prediccion_controller.py:36-47` (`GET /api/analitica/demanda`) expone los términos depurados
  de las consultas sin respaldo. En local (`salidas/04_A01_historial_local.txt`), el «usuario B», sin
  credenciales, lee el texto exacto enviado por el «usuario A». En la nube hay 37 consultas de origen
  `usuario` registradas (`GET /api/estado`). No se leyó su contenido, por la regla de pruebas.
- **Impacto 3.** El texto libre puede contener datos personales que el usuario escriba. Se vulnera el
  principio de finalidad de la Ley N.º 29733 y la privacidad declarada en RNF-06 / R-12 (exposición
  de la consulta).
- **Probabilidad 4.** Una petición GET pública.
- **Tratamiento sugerido.** Historial por sesión, analítica agregada sin texto o tras autorización, y
  retención limitada.

#### OW-04 · Alta, modificación y borrado de fuentes sin autorización (**Alto**, I3 × P4 = 12)
- **Evidencia.** `backend/src/adapters/in/rest/fuentes_controller.py:30-40` (POST), `:61-74` (PUT) y
  `:77-84` (DELETE). En local (`salidas/04_A01_fuentes_local.txt`): `POST /api/fuentes -> 201`, `PUT
  -> 200` (título cambiado a «FUENTE-ALTERADA») y `DELETE -> 204`, todo sin credenciales. Capturas:
  `04_A01_fuentes_crud_sin_auth_codigo.png` y `04_A01_interfaz_fuentes_escritura_publica_nube.png`.
- **Impacto 3.** Se falsea el registro de procedencia y de licenciamiento (RF-07, RNF-08 y principios
  CARE): se pueden borrar fuentes legítimas o declarar licencias falsas. No altera los fragmentos indexados.
- **Probabilidad 4.**
- **Tratamiento sugerido.** El mismo rol de administración que OW-01, y una bitácora de cambios.

#### OW-05 · Recorrido de rutas y lectura arbitraria de archivos al servir la interfaz (**Alto**, I5 × P2 = 10)
- **Evidencia (código).** `backend/src/infrastructure/main.py:76-82`. `archivo =
  configuracion.ruta_interfaz / recurso` se sirve si `is_file()`, sin `resolve()` ni comprobar que
  quede dentro de `ruta_interfaz`. Con pathlib, un segmento absoluto (`C:/…`) **sustituye** la base.
- **Evidencia (local, `salidas/04_A01_traversal_estaticos_local.txt`).** En la instancia con
  `RUTA_INTERFAZ` en `%TEMP%`: `/../secreto_fuera.txt`, `/%2e%2e/secreto_fuera.txt` y
  `/..%2fsecreto_fuera.txt` → **HTTP 200** con el contenido de un archivo situado fuera de la carpeta
  de la interfaz. `/C:/Windows/win.ini` → **HTTP 200** con el contenido de `win.ini`. El montaje
  `/assets` de Starlette sí resiste (`/assets/..%2f..%2f…` → 404).
- **Alcance.** Solo se activa cuando existe `ruta_interfaz/index.html` (`config.py:141-143`), es decir,
  en el ejecutable de escritorio (`QuechuaWankaWeb.spec:4` empaqueta `interfaz`). **No afecta a la
  nube actual**: Render sirve la web como sitio estático y la API responde `GET /` con la raíz JSON,
  según `openapi.json`. El ejecutable escucha en `127.0.0.1` (`backend/ejecutable.py:109`).
- **Impacto 5.** Lectura de cualquier archivo legible por el usuario: el `.env` junto al ejecutable
  (puede contener `DATABASE_URL` o `GEMINI_API_KEY`; se lee de `CARPETA_EJECUTABLE/.env`, `config.py:39-41`), la base SQLite con el
  historial y documentos personales.
- **Probabilidad 2.** Exige alcanzar `127.0.0.1`: otro proceso local, *DNS rebinding* desde una página
  maliciosa (el servicio no valida la cabecera `Host`) o un despliegue futuro que sirva la interfaz en
  `0.0.0.0`. En ese último caso la probabilidad subiría a 5 y la severidad a **Crítico**.
- **Tratamiento sugerido.** Resolver la ruta y exigir que quede contenida en la carpeta de la
  interfaz, o servirla solo con `StaticFiles`.

### A02 · Cryptographic Failures: **Cumple parcialmente** (s_c = 9,0)

**Controles verificados.**
- **TLS de extremo a extremo.** HTTP a HTTPS con 301 en la API y en la web
  (`salidas/04_A05_openapi_estado_nube.txt`).
- **TLS obligatorio hacia Neon.** `sslmode=require` se añade si falta (`config.py:26-36`).
- **Secretos.** `DATABASE_URL` y `GEMINI_API_KEY` con `sync: false` y `TOKEN_PRUEBAS` con
  `generateValue` (`render.yaml:32-37, 47-48`). `.env` está en `.gitignore`.
- **Historial de Git.** El barrido de `git log --all -p` no encuentra ninguna cadena `postgres://…@…neon.tech`
  con contraseña, ninguna clave `AIza…` y ninguna asignación real de `TOKEN_PRUEBAS` (solo marcadores `...`).
- **Clave de Gemini.** Va en la cabecera `x-goog-api-key` y no en la URL (`gemini_generador.py:126`).
- **Token de pruebas.** Se compara con `hmac.compare_digest` (`seguridad.py:76-80`).
- **Integridad de los PDF.** SHA-256 en el almacén (`almacen_documentos_disco.py:71`).

#### OW-06 · La API no envía HSTS (**Bajo**, I2 × P2 = 4)
- **Evidencia.** `salidas/cabeceras_nube_antes.txt` y `04_A05_openapi_estado_nube.txt`: la API no
  devuelve `strict-transport-security`. La web estática sí lo envía (`max-age=315360000; includeSubdomains;
  preload`). Ya registrado como PLUS-02 en `docs/01_auditoria_furps.md:78`.
- **Impacto 2.** La primera petición HTTP de un cliente de la API podría degradarse a HTTP
  (*SSL stripping*) antes del 301 y exponer la cabecera `X-Gemini-Key`. La interfaz usa `https://`
  fijo (`render.yaml:61`), lo que reduce la exposición.
- **Probabilidad 2.** Requiere un atacante en la red y un cliente que use `http://`.

### A03 · Injection: **Cumple parcialmente** (s_c = 9,0)

**Controles verificados.**
- **SQL.** Todas las sentencias usan `text()` con parámetros enlazados
  (`repositorio_consultas_postgres.py:50-74`, `repositorio_corpus_postgres.py:26-27, 54-58`) o el ORM.
  `db/postgres/*.sql` no contiene `EXECUTE`, `format()` ni `quote_*`: no hay SQL dinámico en los procedimientos.
- **Errores de base.** `create_engine(..., hide_parameters=True)` (`contenedor.py:283`) evita que el
  texto de la consulta aparezca en los mensajes de error.
- **XSS.** No hay `dangerouslySetInnerHTML`, `innerHTML` ni `eval` en `frontend/src`. React escapa el
  texto del respaldo, incluido el de un PDF envenenado. La CSP de la API no tiene `unsafe-inline`
  (`seguridad.py:12-16`).
- **Ruta del PDF.** `_nombre_seguro` (`almacen_documentos_disco.py:24-45`) rechaza `..`, `:` (flujos
  NTFS), caracteres de control, nombres reservados de Windows y extensiones que no sean `.pdf`. En
  local, `../../fuera.pdf` → 422 (`salidas/04_A04_pdf_local.txt`).
- **Cabecera BYOK.** Se usa solo como valor de cabecera hacia una URL fija de Google. httpx rechaza
  CR/LF en las cabeceras.

#### OW-07 · Inyección de instrucciones hacia Gemini: mitigada por el verificador literal (**Bajo**, I2 × P2 = 4)
- **Evidencia.** El texto del usuario se concatena en el prompt sin delimitación estructural
  (`gemini_generador.py:82`). La salida del modelo nunca llega al usuario tal cual:
  `GeneradorExtractivo` (`generador_extractivo.py:36-54`) solo compone la plantilla si
  `VerificadorFormaLiteral.comprobar` (`verificador_forma_literal.py:78-90`) encuentra la forma **y** la
  glosa dentro de la **misma** entrada léxica de los fragmentos recuperados. Si no, muestra el
  fragmento literal con su cita. Gemini no se invoca en una abstención.
- **Impacto 2.** Lo peor que puede pasar es una respuesta degradada al fragmento literal o un gasto
  de cuota (ver OW-08). No se puede inyectar una forma que no esté en el corpus, salvo combinando el
  ataque con OW-01.
- **Probabilidad 2.** Por medir con un banco de prompts adversarios. No se ejecutó contra la nube por la regla de pruebas.

### A04 · Insecure Design: **No cumple** (s_c = 4,5)

#### OW-08 · Sin límite de peticiones ni cuotas por cliente (**Alto**, I3 × P4 = 12)
- **Evidencia (código).** Ningún middleware ni dependencia limita la frecuencia (`main.py:46-55`).
  `requirements.txt` no incluye ninguna biblioteca de limitación. `POST /api/consultas`
  (`consultas_controller.py:31-63`) invoca Gemini con la clave del servicio cuando hay respaldo y
  registra cada consulta en Neon. Capturas: `04_A04_consultas_sin_limite_codigo.png` y
  `04_A04_middlewares_sin_rate_limit_codigo.png`.
- **Evidencia (local).** `salidas/04_A04_rate_local.txt`: 60 `POST /api/consultas` seguidos desde un
  mismo cliente en 1,4 s → `{200: 60}`, ningún 429.
- **Impacto 3.** Agota la cuota gratuita de Gemini del servicio. La degradación está diseñada: con un
  429 pasa a fragmento literal (`gemini_generador.py:138-140`), así que **no rompe la salvaguarda**.
  Además hace crecer sin límite la tabla de consultas en Neon y contamina la analítica HU-09 con
  demanda falsa como `usuario`. Combinado con OW-09, expone al agotamiento de CPU y memoria del plan free.
- **Probabilidad 4.** Basta un bucle con `curl`. La API es pública y está documentada en `/docs`.
- **Tratamiento sugerido.** Limitación por IP o sesión en consultas e ingesta, y presupuesto diario
  de llamadas a Gemini.

#### OW-09 · Ingesta de PDF con validación de contenido pero sin límites de recursos (**Medio**, I3 × P2 = 6)
- **Evidencia.** Tamaño: tope de 60 MB por lectura en bloques (`corpus_controller.py:14-27`) y de
  nuevo en el almacén (`almacen_documentos_disco.py:67-70`). Tipo: el controlador solo mira la
  extensión (`corpus_controller.py:46-47`); **no** hay comprobación de *magic bytes* `%PDF-`, pero
  `PdfReader` rechaza lo que no se puede analizar (`extractor_pdf.py:21-24`). En local, un archivo
  `MZ…` llamado `falso.pdf` → 422 «no es un PDF legible» (`salidas/04_A04_pdf_local.txt`). Faltan
  límites de páginas, de tiempo de extracción y de tamaño descomprimido: `extractor_pdf.py:30-35`
  recorre todas las páginas, y `_leer_con_tope` reúne hasta 60 MB en memoria y luego los duplica con
  `b"".join`. El MIME declarado por el cliente no se usa.
- **Impacto 3.** Un PDF válido pero diseñado para ello (miles de páginas o flujos muy comprimidos)
  puede bloquear el proceso único del plan free, que además reconstruye el índice TF-IDF completo
  (`ingestar_documento.py:81-82`). El efecto exacto en memoria es **por medir**: no se probó una bomba
  de descompresión.
- **Probabilidad 2.** Requiere preparar el archivo, aunque el endpoint es público (OW-01).

### A05 · Security Misconfiguration: **Cumple parcialmente** (s_c = 5,5)

**Controles verificados.**
- La API envía CSP estricta, `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy: no-referrer`,
  `Permissions-Policy`, `CORP same-origin` y `Cache-Control: no-store` en `/api`
  (`seguridad.py:20-26, 85-96`; `salidas/cabeceras_nube_antes.txt`).
- FastAPI corre sin `debug`. Los errores no controlados devuelven el 500 genérico y los mensajes 4xx
  no incluyen trazas.
- En local se escucha en `127.0.0.1` y solo en Render en `0.0.0.0` (`render.yaml:20`, `ejecutable.py:109`).

#### OW-10 · El sitio estático no envía CSP (ni Referrer-Policy ni Permissions-Policy) (**Medio**, I2 × P3 = 6)
- **Evidencia.** `render.yaml:67-73` declara solo `X-Content-Type-Options` y `X-Frame-Options` para
  `quechua-web`. `salidas/cabeceras_nube_antes.txt`: la respuesta de `https://quechua-web.onrender.com/`
  no trae `content-security-policy`. Captura: `04_A05_cabeceras_http_nube.png`. Ya figura como PLUS-02
  en FURPS+. El ZAP de U3 (M-21) midió la CSP de la API servida en local, no la de este sitio.
- **Impacto 2.** Sin defensa en profundidad ante un XSS futuro. Hoy no hay vector XSS (A03), y la
  clave BYOK vive en la memoria de la pestaña (`frontend/src/api.js:10-17`), justo lo que una CSP protegería.
- **Probabilidad 3.**

#### OW-11 · CORS con `allow_credentials=True` y métodos y cabeceras `*` (**Bajo**, I2 × P2 = 4)
- **Evidencia.** `main.py:49-55`, con los orígenes de `CORS_ORIGENES` (`render.yaml:44-45`, solo la
  web). Un preflight desde un origen ajeno → 400 sin `access-control-allow-origin`
  (`salidas/cors_preflight_ajeno_antes.txt`). Ya registrado como PLUS-04.
- **Impacto 2.** La API no usa cookies ni credenciales de navegador, así que `allow_credentials` no
  aporta nada y amplía la superficie si algún día se añaden cookies. `*` en métodos admite `DELETE`
  y `PUT` desde la web oficial.
- **Probabilidad 2.** La lista blanca de orígenes funciona.

#### OW-12 · `/docs` y `/openapi.json` públicos en producción, con Swagger cargado de un CDN sin CSP (**Bajo**, I2 × P2 = 4)
- **Evidencia.** `GET https://quechua-api.onrender.com/docs` → 200. `openapi.json` enumera todos los
  endpoints de escritura (`salidas/04_A05_openapi_estado_nube.txt`; captura
  `04_A01_docs_endpoints_escritura_nube.png`). `seguridad.py:18, 91-92` excluye las rutas de
  documentación de la CSP.
- **Impacto 2.** Facilita el reconocimiento de OW-01 a OW-04. La propia web pública también los revela.
- **Probabilidad 2.**

#### OW-13 · Divulgación de detalles internos y rol de base con privilegios de DDL (**Bajo**, I1 × P4 = 4)
- **Evidencia.** `GET /api/estado` (público) revela el motor (`postgres`), el origen del corpus, el
  modelo (`gemini-3.5-flash-lite`), el entorno (`staging`), los conteos por origen (`carga 1005, humo
  268, usuario 37`) y si hay base de demostración. La aplicación instala el esquema y los
  procedimientos al arrancar con la misma cadena de conexión que usa para operar
  (`contenedor.py:301-302`). Por tanto, el rol de la aplicación tiene permisos de DDL sobre Neon y no
  hay mínimo privilegio. Los permisos efectivos del rol en Neon son **por medir**: no se consultaron.
- **Impacto 1** para la divulgación. El rol con DDL agravaría una inyección SQL hipotética, que hoy no existe.
- **Probabilidad 4** para la divulgación.

### A06 · Vulnerable and Outdated Components: **Cumple parcialmente** (s_c = 6,5)

**Controles verificados.**
- `pip-audit -r backend/requirements.txt` → «No known vulnerabilities found»
  (`salidas/04_A06_dependencias.txt`; coincide con M-19).
- `npm audit --omit=dev` → «found 0 vulnerabilities»: React 19 es la única dependencia de
  producción del frontend.
- La CI ejecuta `pip-audit` en cada push (`ci.yml:46-47`).

#### OW-14 · Tres avisos altos en dependencias de desarrollo y compilación del frontend (**Medio**, I3 × P2 = 6)
- **Evidencia.** Según `npm audit` (`salidas/04_A06_dependencias.txt`), hay **3 high**:
  - `vite 8.3.0` (rango afectado 8.3.0-8.3.2): GHSA-9jrq-w75r-8gcw, ejecución de script entre orígenes
    vía middleware; GHSA-rq7h-c2jc-7f22 y GHSA-vfpm-58rq-9qcg, lectura fuera de `server.fs`; y
    `launch-editor`, GHSA-r825-w8mm-5pxw.
  - `undici 7.0.0-7.30.0`: GHSA-2m5v-pch6-74hx (validación TLS omitida), GHSA-4w7w-5xrc-9h26 y varias DoS.
  - `source-map-js ≤ 1.2.1`: GHSA-68fv-2mgg-jv7q.

  Todas tienen corrección vía `npm audit fix`. La CI no ejecuta `npm audit` (`ci.yml:61-68`). Render
  compila con `npm ci`, que instala las devDependencies (`render.yaml:54`).
- **Impacto 3.** Afecta al servidor de desarrollo de Vite en los equipos del equipo, donde una
  página maliciosa podría leer archivos del proyecto, y a la cadena de compilación. **No llega al
  bundle servido**: `--omit=dev` da 0.
- **Probabilidad 2.** Requiere tener `vite` en marcha y visitar una página maliciosa.
- **Discrepancia.** M-19 de U3 reportó `npm audit 0`. Los avisos actuales corresponden a avisos
  publicados después o a otra lectura. Hay que actualizar la cifra en lugar de citarla como vigente.

#### OW-15 · Dependencias transitivas de Python sin fijar ni verificar por hash; sin actualización automatizada (**Bajo**, I2 × P2 = 4)
- **Evidencia.** `backend/requirements.txt` fija con `==` las 13 dependencias directas, pero no hay
  archivo de bloqueo ni `--require-hashes`. Render ejecuta `pip install -r requirements.txt`
  (`render.yaml:18`), de modo que las transitivas se resuelven en cada despliegue. `.github/` no
  contiene `dependabot.yml`.
- **Impacto 2.** Un despliegue podría arrastrar una transitiva comprometida o vulnerable entre dos
  ejecuciones de `pip-audit`.

### A07 · Identification and Authentication Failures: **No cumple** (s_c = 5,0)

**Controles verificados.**
- El token de pruebas se compara en tiempo constante (`seguridad.py:79`). Si está vacío, el
  mecanismo queda desactivado (`seguridad.py:72`), y solo se acepta un origen de la lista cerrada
  `{"carga","humo"}` (`seguridad.py:58, 76-81`). En local, con un token inventado, la consulta queda
  registrada como `usuario` (`salidas/04_A07_token_local.txt`: `consultas_por_origen {"usuario": 63}`).
- La clave BYOK se limita a la petición mediante `ContextVar`, que se restablece en `finally`
  (`seguridad.py:41-55`). No se registra ni se devuelve, y en el cliente solo vive en memoria, sin
  `localStorage` (`frontend/src/api.js:10-17`).

#### OW-16 · No existe ningún mecanismo de autenticación para las funciones de administración (**Alto**, I4 × P4 = 16)
- **Evidencia.** `openapi.json` sin `securitySchemes`. No hay usuarios, sesiones, claves de
  administración ni middleware de identidad (`main.py:46-55`). El contexto de despliegue de S13 describe el servicio como
  consulta pública sin usuarios, pero la API publica operaciones de escritura y
  borrado (OW-01 a OW-04). El token de pruebas existe y está bien construido, pero solo decide el
  **origen** con que se registra una consulta: no autoriza ninguna operación.
- **Impacto 4.** Es la causa raíz común de OW-01 a OW-04. No se cuenta dos veces en el score (§1.3).
- **Probabilidad 4.**
- **Tratamiento sugerido.** Separar el perfil público de solo lectura de un perfil de administración
  autenticado, o retirar del despliegue público las rutas de escritura.

### A08 · Software and Data Integrity Failures: **No cumple** (s_c = 4,5)

**Controles verificados.**
- La CI corre con `permissions: contents: read` (`ci.yml:11-12`), el mínimo para el `GITHUB_TOKEN`.
- Render solo despliega si la CI pasa (`autoDeployTrigger: checksPass`, `render.yaml:22, 56`).
- El frontend se instala con `npm ci` sobre `package-lock.json`.
- El verificador literal (ADR-028) garantiza la integridad de la redacción **respecto del corpus**.

#### OW-17 · El corpus admite contenido no verificado sin cuarentena, revisión ni trazabilidad de quién lo incorporó (**Alto**, I5 × P2 = 10)
- **Evidencia.** `IngestarDocumentoUseCase.ejecutar` (`ingestar_documento.py:41-95`) extrae, segmenta
  e indexa en el acto. El único requisito es que `titulo`, `entidad_publicadora` y `licenciamiento`
  sean texto no vacío (`esquemas.py`, `Fuente`): la licencia es declarativa y no se verifica. No hay
  estado «pendiente de revisión», firma, lista de entidades admitidas ni registro de quién subió el
  documento. La demostración de OW-01 muestra que el fragmento nuevo se usa como respaldo con
  `coincidencia_lema: true` en la consulta siguiente.
- **Impacto 5.** La integridad del corpus es la integridad de todo el sistema: el verificador y τ
  solo garantizan fidelidad al corpus, no la veracidad del corpus.
- **Probabilidad 2.** Hoy la explotación directa ya se cuenta en OW-01. Este hallazgo es el residual
  de diseño que seguiría abierto aunque se añadiera autenticación (error o abuso de un administrador).

#### OW-18 · Acciones de la CI fijadas por etiqueta y Swagger UI desde un CDN con versión flotante y sin SRI (**Bajo**, I2 × P2 = 4)
- **Evidencia.** `ci.yml:34-35, 55-56` usa `actions/checkout@v5`, `actions/setup-python@v6` y
  `actions/setup-node@v5`, fijadas por **etiqueta** y no por SHA. Una etiqueta movida ejecutaría
  código ajeno en la CI. El riesgo queda acotado por `contents: read` y porque la CI no maneja
  secretos de despliegue. `/docs` carga `https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js`
  **sin `integrity`** y con versión mayor flotante (`salidas/04_A05_openapi_estado_nube.txt`).
- **Impacto 2.** El CDN comprometido ejecutaría script en el origen de la API, que no guarda cookies.

### A09 · Security Logging and Monitoring Failures: **Cumple parcialmente** (s_c = 7,0)

**Controles verificados.**
- Los logs no contienen secretos: la clave BYOK y el token no se registran (`seguridad.py:32-36, 61-65`).
- Los logs no contienen el texto de la consulta: el fallo de registro solo anota `consulta_id` y el
  tipo de excepción (`consultar_corpus.py:446-451`), y la base usa `hide_parameters=True`
  (`contenedor.py:283`).
- El log local de la demostración (`%TEMP%/owaspaud/uvicorn.log`) muestra solo rutas, métodos y códigos.

#### OW-19 · Sin bitácora de auditoría de las operaciones de escritura ni alertas de abuso (**Medio**, I3 × P3 = 9)
- **Evidencia.**
  - Las operaciones destructivas solo dejan una línea genérica: `"[REST] DELETE /api/historial"`
    (`historial_controller.py:40`), `"[REST] POST /api/corpus/documentos"`
    (`corpus_controller.py:45`) y `"[REST] DELETE /api/fuentes/{id}"` (`fuentes_controller.py:82`).
    No registran actor ni IP de origen: tras Cloudflare, el access log de uvicorn ve la IP del proxy,
    salvo cabeceras reenviadas que no se procesan, y esto es **por medir** en los logs de Render.
    Tampoco registran el nombre ni el SHA-256 completo del documento, ni la fuente afectada.
  - No hay métricas de 4xx/429, umbrales ni alertas. El contador `errores_429` de Gemini
    (`gemini_generador.py:138-140`) no se expone ni dispara nada.
  - La retención de logs del plan free de Render es limitada: la cifra es por medir.
  - `contenedor.py:317-320` registra la primera línea de la excepción de conexión a la base, que en
    psycopg puede incluir el host y el usuario, aunque nunca la contraseña.
- **Impacto 3.** Ni el envenenamiento ya ocurrido en Neon (2 PDF de prueba, `docs/17:135`) ni un
  borrado del historial se pueden atribuir ni detectar a tiempo.
- **Probabilidad 3.**

### A10 · Server-Side Request Forgery: **Cumple** (s_c = 10,0)

- **Evidencia.** No hay ninguna URL controlada por el usuario.
  - Gemini usa la constante `URL_API` (`gemini_generador.py:29`) y el modelo sale de la configuración
    (`GEMINI_MODELO`, `render.yaml:38-39`).
  - `OLLAMA_URL` sale de la configuración del servidor (`config.py:72`) y no se usa en la nube
    (`GENERADOR=gemini`).
  - La cabecera BYOK solo aporta el valor de `x-goog-api-key`, no el destino.
  - La ingesta recibe bytes (multipart) y no URL. El backend no descarga ningún recurso remoto
    indicado por el cliente.
- **Riesgo residual.** Si en el futuro se aceptan URL de PDF o se permite elegir el modelo de Gemini
  por cabecera, hará falta reevaluar esta categoría.

---

## 4. Lista consolidada de hallazgos

| ID | Cat. | Severidad | I | P | I×P | Hallazgo (una línea) | Nube afectada |
|---|---|---|---:|---:|---:|---|---|
| OW-01 | A01 | **Crítico** | 5 | 4 | 20 | Ingesta y reindexado públicos: un PDF arbitrario se convierte en respaldo citado (rompe RN-06) | Sí (persistente en Neon) |
| OW-02 | A01 | Alto | 3 | 4 | 12 | `DELETE /api/historial` borra el historial de todos sin autorización | Sí |
| OW-03 | A01 | Alto | 3 | 4 | 12 | `GET /api/historial` y `/api/analitica/demanda` exponen las consultas de todos | Sí |
| OW-04 | A01 | Alto | 3 | 4 | 12 | CRUD de `/api/fuentes` sin autorización (procedencia y licencias falsificables) | Sí |
| OW-05 | A01 | Alto | 5 | 2 | 10 | Recorrido de rutas en `interfaz_o_recurso`: lectura de cualquier archivo (`/C:/Windows/win.ini`) | No (escritorio) |
| OW-06 | A02 | Bajo | 2 | 2 | 4 | La API no envía HSTS | Sí |
| OW-07 | A03 | Bajo | 2 | 2 | 4 | Consulta concatenada en el prompt de Gemini, mitigada por el verificador literal | Sí (mitigado) |
| OW-08 | A04 | Alto | 3 | 4 | 12 | Sin límite de peticiones: cuota de Gemini, crecimiento de Neon y analítica contaminada | Sí |
| OW-09 | A04 | Medio | 3 | 2 | 6 | Ingesta de PDF sin límite de páginas, tiempo ni memoria descomprimida | Sí |
| OW-10 | A05 | Medio | 2 | 3 | 6 | El sitio estático no envía CSP, Referrer-Policy ni Permissions-Policy | Sí |
| OW-11 | A05 | Bajo | 2 | 2 | 4 | CORS con `allow_credentials` y `*` en métodos y cabeceras (mitigado por la lista de orígenes) | Sí |
| OW-12 | A05 | Bajo | 2 | 2 | 4 | `/docs` y `/openapi.json` públicos con endpoints de escritura | Sí |
| OW-13 | A05 | Bajo | 1 | 4 | 4 | `/api/estado` detalla los componentes internos; el rol de la base aplica DDL | Sí |
| OW-14 | A06 | Medio | 3 | 2 | 6 | `npm audit`: 3 high en devDeps (vite 8.3.0, undici, source-map-js); la CI no lo ejecuta | Compilación |
| OW-15 | A06 | Bajo | 2 | 2 | 4 | Transitivas de Python sin fijar ni hash; sin Dependabot | Compilación |
| OW-16 | A07 | Alto | 4 | 4 | 16 | Sin mecanismo de autenticación para las funciones de administración (causa raíz) | Sí |
| OW-17 | A08 | Alto | 5 | 2 | 10 | El corpus admite contenido sin cuarentena, revisión ni autoría registrada | Sí |
| OW-18 | A08 | Bajo | 2 | 2 | 4 | Acciones de la CI por etiqueta; Swagger desde un CDN `@5` sin SRI | CI y `/docs` |
| OW-19 | A09 | Medio | 3 | 3 | 9 | Sin bitácora de auditoría de las escrituras ni alertas de abuso | Sí |

Cálculo del score (§1.3):
- A01: 10 − (8 + 2) = 0
- A02: 10 − 1 = 9
- A03: 10 − 1 = 9
- A04: 10 − (5 + 0,5) = 4,5
- A05: 10 − (3 + 1,5) = 5,5
- A06: 10 − (3 + 0,5) = 6,5
- A07: 10 − 5 = 5
- A08: 10 − (5 + 0,5) = 4,5
- A09: 10 − 3 = 7
- A10: 10

**Total: 61,0 / 100.** Si se cerraran solo OW-01 a OW-04 y OW-16 con un perfil de administración
autenticado, A01 quedaría en 10 − (5 + 0) = 5 por OW-05 y A07 en 10, lo que llevaría el score a
≈ 71. Es un cálculo ilustrativo, no una medición.

---

## 5. Evidencias

### 5.1 Salidas de terminal generadas por esta auditoría

Todas están en `docs/evidencias/s13_furps_owasp/antes/salidas/`:

| Archivo | Hallazgos | Contenido |
|---|---|---|
| `04_A08_envenenamiento_local.txt` | OW-01, OW-17 | Abstención → subida sin credenciales → respuesta citando `auditoria_owasp.pdf, p. 1` |
| `04_A01_historial_local.txt` | OW-02, OW-03 | El usuario B lee la consulta del usuario A y borra el historial (204) |
| `04_A01_fuentes_local.txt` | OW-04 | POST 201, PUT 200 y DELETE 204 sin credenciales |
| `04_A01_traversal_estaticos_local.txt` | OW-05 | `/%2e%2e/…` y `/C:/Windows/win.ini` → 200 |
| `04_A04_rate_local.txt` | OW-08 | 60 consultas en 1,4 s, todas 200 |
| `04_A04_pdf_local.txt` | OW-09, A03 | Un no-PDF y un nombre con `..` → 422 |
| `04_A07_token_local.txt` | A07 (control) | Un token inventado no cambia el origen |
| `04_A05_openapi_estado_nube.txt` | OW-06, OW-12, OW-13, OW-18 | Rutas y seguridad de `openapi.json`, recursos de `/docs`, `/api/estado`, 301 y HSTS |
| `04_A06_dependencias.txt` | OW-14 | pip-audit 0 · `npm audit --omit=dev` 0 · `npm audit` 3 high |

### 5.2 Capturas «antes» ya existentes que respaldan los hallazgos

`04_A01_delete_historial_sin_auth_codigo.png` (OW-02) · `04_A01_fuentes_crud_sin_auth_codigo.png` (OW-04) ·
`04_A01_post_documentos_sin_auth_codigo.png` y `04_A01_reindexar_sin_auth_codigo.png` (OW-01) ·
`04_A01_docs_endpoints_escritura_nube.png` (OW-12, OW-16) · `04_A01_interfaz_fuentes_escritura_publica_nube.png` (OW-04) ·
`04_A01_interfaz_incorporar_documentos_publica_nube.png` (OW-01) · `04_A04_consultas_sin_limite_codigo.png` y
`04_A04_middlewares_sin_rate_limit_codigo.png` (OW-08) · `04_A05_cabeceras_http_nube.png` (OW-06, OW-10).

### 5.3 Capturas «antes» que faltan para los hallazgos críticos y altos

| Nombre sugerido | Hallazgo | Qué debe verse |
|---|---|---|
| `04_A01_envenenamiento_respuesta_citada_local.png` | OW-01 | Terminal con `04_A08_envenenamiento_local.txt`: antes `abstenida: true`, después `abstenida: false` con `documento: auditoria_owasp.pdf` |
| `04_A01_estado_documentos_corpus_10_nube.png` | OW-01 | `GET /api/estado` de la nube con `documentos_corpus: 10` y `fragmentos_indexados: 3607` |
| `04_A01_historial_lectura_ajena_local.png` | OW-03 | Respuesta del `GET /api/historial` del usuario B con el texto de la consulta del usuario A |
| `04_A01_historial_codigo.png` | OW-03 | `historial_controller.py:14-33` sin filtro por sesión, y `prediccion_controller.py:36-47` |
| `04_A01_traversal_win_ini_local.png` | OW-05 | `curl --path-as-is …/C:/Windows/win.ini` → 200 con el contenido |
| `04_A01_interfaz_o_recurso_codigo.png` | OW-05 | `main.py:76-82` sin `resolve()` ni contención |
| `04_A04_rafaga_60_consultas_local.png` | OW-08 | Salida `{200: 60}` en 1,4 s |
| `04_A07_openapi_sin_security_schemes_nube.png` | OW-16 | Listado de `openapi.json` con `securitySchemes = None` |
| `04_A08_ingesta_sin_cuarentena_codigo.png` | OW-17 | `ingestar_documento.py:41-95`: extracción, indexado y registro sin estado de revisión |

---

## 6. Limitaciones

- **Sin escrituras contra la nube.** Los efectos de OW-01 a OW-04 y OW-08 en la nube se infieren del
  código, que es idéntico en `main` para esos controladores (`git diff 1d0b129 -- backend/src` solo
  cambia la validación de `limite`/`top` y añade `/api/vivo`), de `openapi.json` y de la
  demostración local. No se midió el consumo real de cuota de Gemini ni el comportamiento de Neon
  bajo carga.
- **Sin escaneo activo** (ZAP activo, fuzzing). El ZAP pasivo de U3 se ejecutó solo en local (M-21).
- **Quedan por medir:**
  - el efecto en memoria de un PDF diseñado para ello (OW-09);
  - la retención y el contenido real de los logs de Render, incluida la IP de origen (OW-19);
  - los privilegios efectivos del rol de Neon (OW-13);
  - la robustez del verificador ante un banco de prompts adversarios (OW-07).
- **Fecha de los avisos.** Los avisos de `npm audit` dependen de la base de GitHub Advisory a fecha
  de 2026-11-12 y discrepan del `npm audit 0` de U3.
- **Auditoría de seguridad, no de corrección funcional.** No se evaluó τ = 0,48, RN-06 ni la calidad
  de recuperación, salvo en lo que afecta a su integridad (OW-01, OW-17). No se escribió, completó ni
  corrigió ninguna forma quechua: el contenido de la demostración fue una marca no quechua.
