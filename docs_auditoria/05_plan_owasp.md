# 05 · Plan de remediación OWASP Top 10 — Asistente de consulta del quechua wanka (versión web)

| Dato | Valor |
|---|---|
| Fecha | 2026-11-12 |
| Entrada | `docs_auditoria/04_auditoria_owasp.md`: score **61,0 / 100**, 19 hallazgos (1 crítico, 7 altos, 5 medios, 6 bajos); dictamen «no apto para exposición pública» |
| Rama | `s13/owasp`, apilada sobre `s13/furps-owasp` (PR #23). Se entrega en un PR propio, el de la fase 2 |
| Rol | Arquitecto de seguridad. Este documento planifica; la aplicación es el paso 7 |
| Restricción principal | No romper la consulta pública (HU-03 a HU-07), la Predicción ML (HU-08, RF-15), la versión de escritorio ni la salvaguarda (τ = 0,48, RN-06, ADR-028). Compatibilidad hacia atrás en rutas y contratos |

## 1. Principio rector: el control depende del modo, no del cliente

El sistema ya distingue el entorno con `ENTORNO` (`render.yaml` fija `staging`; el escritorio y la E2E usan
el valor por defecto, `local`). Todos los controles nuevos se activan **solo cuando `ENTORNO` ≠ `local`**,
que llamaremos «modo nube». Así:

- En local, escritorio y E2E el comportamiento **no cambia**: las mismas pruebas siguen valiendo como prueba
  de no regresión.
- En la nube, la configuración por defecto es la **segura**. Si falta `ADMIN_TOKEN`, las escrituras se
  niegan con 403, y el límite de peticiones está activo aunque no se defina ninguna variable.
- **No se modifica `render.yaml` ni la configuración de Render o de Neon**, que son de otro integrante.
  Lo único que necesita el dueño de Render es definir `ADMIN_TOKEN`, y queda documentado como acción para
  personas. Sin esa variable, el sistema falla de forma segura.

## 2. Remediaciones priorizadas

Riesgo = impacto × probabilidad, tomado de `04`. Los IDs RM-xx son de este plan.

### RM-01 · Token de administración para las escrituras en modo nube — **Crítico**

| Campo | Contenido |
|---|---|
| Hallazgos | OW-01 (crítico, 20), OW-02 (12), OW-04 (12), OW-16 (16): A01 y A07 |
| Riesgo | Cualquiera puede envenenar el corpus citado (rompe RN-06), falsificar fuentes y licencias o borrar el historial de todos |
| Componentes | `backend/src/infrastructure/seguridad.py` (nuevo middleware `EscrituraProtegida`), `infrastructure/config.py` (`admin_token`, `modo_nube`), `infrastructure/main.py` (registro), `frontend/src/api.js` y las pestañas «Fuentes del corpus» e «Incorporar documentos» |
| Mitigación | Middleware ASGI con el mismo patrón que `OrigenDePruebasAutorizado`. En modo nube, toda petición a `/api/*` con un método distinto de GET, HEAD u OPTIONS exige la cabecera `X-Admin-Token`, comparada con `hmac.compare_digest` contra `ADMIN_TOKEN`. Las dos únicas excepciones son las operaciones públicas de lectura que usan POST: `POST /api/consultas` y `POST /api/predicciones`. Sin cabecera → **401**. Con un token incorrecto, o con `ADMIN_TOKEN` vacío → **403**. Al proteger por defecto (lista de excepciones en lugar de lista de rutas), una ruta de escritura futura queda protegida sin acordarse de ella. El token no se registra en los logs. En la interfaz hay un campo «Token de administración» (`type="password"`, en memoria del módulo, **sin `localStorage` ni el *bundle***). Sin token, esas pestañas muestran «solo lectura» y ocultan los formularios. Consultar y Predicción ML no cambian |
| Validación | pytest: en modo nube, 401 sin token, 403 con token incorrecto, 403 sin `ADMIN_TOKEN`, 2xx con el token correcto en cada ruta de escritura; en local, 2xx sin token (comportamiento actual); consultas y predicciones siguen siendo 200 sin token. Vitest: la pestaña en solo lectura y el token enviado en la cabecera. Prueba local en modo nube con `curl` y capturas |
| Rollback | `git revert` del commit. Mientras tanto, como contingencia, el dueño de Render puede poner `ENTORNO=local` para desactivar el control (no recomendado) |
| ADR | ADR-035 |

### RM-02 · Historial por sesión en la nube; el del servidor, solo para el administrador — **Alto**

| Campo | Contenido |
|---|---|
| Hallazgos | OW-03 (12), OW-02 (12); FURPS U-03 |
| Riesgo | Exposición de lo que consultan otros visitantes; borrado de la evidencia de HU-09 |
| Componentes | `seguridad.py` (la lectura de `/api/historial` también exige token en modo nube), `frontend/src/App.jsx` y `componentes/Historial.jsx` |
| Mitigación | Se elige **historial por sesión** para el público y **solo administrador** para el historial del servidor. En modo nube, `GET` y `DELETE /api/historial` exigen el token. La interfaz pública guarda en memoria de la pestaña las consultas de **esa** sesión y las muestra; «Borrar» vacía solo esa lista. El servidor sigue registrando las consultas (HU-09 no pierde datos) y el administrador puede leerlas. En local, el historial sigue siendo el de la base, como hoy (RF-11) |
| Alternativas descartadas | (a) Identificador de sesión en una cookie o cabecera con filtrado en la base: exige migrar el esquema de `consultas` en Neon (base de otro integrante) y añade un dato persistente por visitante. (b) Retirar el historial de la nube: RF-11 dejaría de verse |
| Validación | pytest: `GET /api/historial` en modo nube → 401 sin token y 200 con token. Vitest: en la nube, el historial muestra solo las consultas de la sesión y no llama a `/api/historial` |
| Rollback | `git revert` |
| ADR | ADR-036 |
| Riesgo residual | `GET /api/analitica/demanda` sigue siendo público, porque la consigna exige que Predicción ML no cambie para el público. Expone términos **agregados** de las consultas sin respaldo, no consultas completas ni quién las hizo. Se documenta como riesgo residual bajo |

### RM-03 · Límite de peticiones por IP — **Alto**

| Campo | Contenido |
|---|---|
| Hallazgos | OW-08 (12); FURPS P-01 y R-03 |
| Riesgo | Agotamiento de la cuota de Gemini para todos, crecimiento de la tabla `consultas` en Neon y contaminación de la analítica de HU-09 |
| Componentes | `seguridad.py` (middleware `LimitePeticiones`, sin dependencias nuevas), `config.py`, `main.py`, `frontend/src/api.js` (mensaje del 429) |
| Mitigación | Ventana deslizante en memoria (un solo proceso uvicorn en Render) por IP y por ruta. Valores por defecto en modo nube: `POST /api/consultas` 20/min y `POST /api/predicciones` 60/min, configurables con `LIMITE_CONSULTAS_POR_MINUTO` y `LIMITE_PREDICCIONES_POR_MINUTO` (0 = desactivado; desactivado en local). Al superarlo: **429** con `Retry-After` y un mensaje claro en español. IP del cliente: `CF-Connecting-IP` (Render sirve detrás de Cloudflare: `Server: cloudflare` en `cabeceras_nube_antes.txt`), luego el primer valor de `X-Forwarded-For` y luego el socket. Las peticiones con un token de pruebas válido (origen `humo` o `carga`, que es la medición controlada de HU-09) quedan exentas. Memoria acotada: como máximo 10 000 IP, con purga de las inactivas |
| Validación | pytest: 21.ª consulta en un minuto → 429 con `Retry-After`; otra IP no afectada; con token de pruebas no se limita; en local no se limita. Ráfaga local en modo nube y captura |
| Rollback | `git revert`, o subir el límite por variable sin desplegar código |
| ADR | ADR-037 |

### RM-04 · Contención de rutas al servir la interfaz — **Alto**

| Campo | Contenido |
|---|---|
| Hallazgos | OW-05 (10): solo escritorio |
| Mitigación | En `interfaz_o_recurso` (`main.py`) se resuelve la ruta (`resolve()`) y solo se sirve si queda dentro de `ruta_interfaz.resolve()`. En otro caso se devuelve `index.html`, como cualquier ruta del cliente |
| Validación | pytest con `..`, `%2e%2e`, ruta absoluta y `assets/..`: nunca se sirve un archivo de fuera; un recurso legítimo sigue servido |
| Rollback | `git revert` |

### RM-05 · Endurecimiento de la ingesta de PDF — **Medio**

| Campo | Contenido |
|---|---|
| Hallazgos | OW-09 (6), OW-17 (alto, parcial) |
| Mitigación | Rechazo temprano (422) si el contenido no empieza por la firma `%PDF-`, antes de extraerlo. Con RM-01 la ingesta queda restringida al administrador, lo que reduce la probabilidad de OW-09 y OW-17. La cuarentena con revisión (OW-17) es un cambio de flujo de negocio y queda como riesgo residual documentado |
| Validación | pytest: un archivo `.pdf` que no es PDF → 422 sin llegar al caso de uso |
| Rollback | `git revert` |

### RM-06 · Cabeceras y CORS — **Medio**

| Campo | Contenido |
|---|---|
| Hallazgos | OW-10 (6), OW-06 (4), OW-11 (4), OW-12 (4) |
| Mitigación | (a) CSP del sitio estático **sin tocar `render.yaml`**: un *plugin* de Vite inyecta, solo en `build`, `<meta http-equiv="Content-Security-Policy">` con `default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self' <origen de VITE_API_URL>; object-src 'none'; base-uri 'self'; form-action 'self'` y `<meta name="referrer" content="no-referrer">`. En desarrollo no se inyecta, para no romper el HMR de Vite. (b) HSTS (`max-age=31536000; includeSubDomains`) en la API, solo en modo nube. (c) CORS con métodos y cabeceras explícitos (`Content-Type`, `X-Gemini-Key`, `X-Admin-Token`, `X-Token-Pruebas`, `X-Origen-Consultas`) y `allow_credentials=False`, porque no se usan cookies. (d) `/docs` se mantiene, porque es evidencia de la consigna, pero el esquema OpenAPI declara el esquema de seguridad `X-Admin-Token` en las rutas protegidas, de modo que Swagger muestra el candado |
| Validación | `npm run build` y búsqueda de la meta en `dist/index.html`; la E2E (modo dev) sigue en verde; pytest de cabeceras y preflight CORS |
| Rollback | `git revert` |

### RM-07 · Componentes vulnerables e integridad de la CI — **Medio**

| Campo | Contenido |
|---|---|
| Hallazgos | OW-14 (6), OW-18 (4), OW-15 (4) |
| Mitigación | `npm audit fix` (devDependencies: vite, undici, source-map-js) sin `--force` y comprobando que Vitest, la E2E y el *build* siguen en verde. Paso `npm audit --audit-level=high` en la CI. Acciones fijadas por SHA (`actions/checkout@fbc6f39…` # v5, `setup-python@ece7cb0…` # v6, `setup-node@a0853c2…` # v5). OW-15 (dependencias transitivas sin *hash*) queda documentado: migrar a `pip-tools` con *hashes* es un cambio de cadena de construcción que afecta al *build* de Render |
| Validación | `npm audit` 0, `pip-audit` 0, CI en verde |
| Rollback | `git revert`; el `package-lock.json` anterior queda en Git |

### RM-08 · Bitácora de seguridad — **Medio**

| Campo | Contenido |
|---|---|
| Hallazgos | OW-19 (9) |
| Mitigación | El *logger* `rag.seguridad` registra, sin el token ni el texto de la consulta: `[SEGURIDAD] escritura autorizada|rechazada (401/403) <método> <ruta> cliente=<huella>` y `[SEGURIDAD] 429 <ruta> cliente=<huella>`. La huella es un SHA-256 truncado de la IP, para no guardar el dato personal en claro. Las alertas automáticas dependen del panel de Render (acción para personas) |
| Validación | pytest con `caplog`: aparece la línea y no aparecen ni el token ni la IP en claro |
| Rollback | `git revert` |

### Fuera del alcance de esta fase (riesgo residual documentado)

| Hallazgo | Motivo | Tratamiento |
|---|---|---|
| OW-07 (A03, bajo) | Inyección de instrucciones hacia Gemini: ya la mitiga el verificador literal de ADR-028, que es intocable | Banco de *prompts* adversarios: por medir |
| OW-13 (A05, bajo) | `/api/estado` alimenta la interfaz y el *health check*; los privilegios del rol de Neon son del dueño de la base | Acción para personas: rol sin DDL en Neon |
| OW-15 (A06, bajo) | *Hashes* de dependencias transitivas | Trabajo futuro con `pip-tools` |
| OW-17 (A08, alto → medio tras RM-01) | La cuarentena con revisión cambia el flujo de negocio de HU-02 | Riesgo residual; RM-01 reduce la probabilidad a la del administrador |
| 2 PDF de prueba en Neon | Base de otro integrante | Acción para personas: retirarlos desde la interfaz con el token, una vez desplegado |

## 3. Roadmap y orden recomendado

| Orden | Remediación | Prioridad | Depende de |
|---|---|---|---|
| 1 | RM-04 contención de rutas | Alto | — (aislada, escritorio) |
| 2 | RM-01 token de administración (backend) | Crítico | — |
| 3 | RM-02 historial (backend, mismo middleware) | Alto | RM-01 |
| 4 | RM-03 límite de peticiones | Alto | — |
| 5 | RM-08 bitácora (en los mismos middlewares) | Medio | RM-01, RM-03 |
| 6 | RM-05 firma del PDF | Medio | — |
| 7 | RM-06 cabeceras, CORS y OpenAPI | Medio | RM-01 (cabecera nueva en CORS) |
| 8 | RM-01/RM-02 interfaz (token, solo lectura, historial por sesión) | Crítico/Alto | RM-01, RM-02 en el backend |
| 9 | RM-07 dependencias y CI | Medio | — |
| 10 | Documentación: ADR-035 a 037, README, `humo_nube.py` y Postman con `X-Admin-Token` opcional | — | Todo lo anterior |

Primero se cierra lo crítico en el backend, que es donde está el control real; la interfaz solo refleja el
control y nunca lo sustituye.

## 4. Riesgos de implementación

| ID | Riesgo | P | I | Mitigación |
|---|---|---:|---:|---|
| RI-01 | Tras desplegar sin `ADMIN_TOKEN`, el equipo no puede administrar el corpus en la nube | 4 | 2 | Es el fallo seguro buscado; la acción para personas lo resuelve en un minuto en el panel de Render |
| RI-02 | `humo_nube.py` y Newman contra la nube fallan en el CRUD de fuentes | 4 | 2 | Cabecera `X-Admin-Token` opcional desde la variable de entorno `ADMIN_TOKEN` del operador; documentado |
| RI-03 | El límite de peticiones bloquea a usuarios legítimos detrás de una misma IP (aula con NAT) | 2 | 3 | 20 consultas/min por IP es holgado para uso humano; ajustable por variable sin desplegar |
| RI-04 | La IP de `CF-Connecting-IP` se falsifica si alguien llega al origen sin pasar por Cloudflare | 2 | 2 | En Render, `*.onrender.com` pasa por Cloudflare; riesgo residual documentado en ADR-037 |
| RI-05 | La CSP en `<meta>` bloquea algún recurso del *build* | 2 | 3 | El *build* no usa recursos externos (ya lo comprobó ZAP en la U3); verificación con la vista previa de producción en local |
| RI-06 | `npm audit fix` cambia el comportamiento de Vite o de Vitest | 2 | 2 | Sin `--force`; baterías completas antes de hacer commit |
| RI-07 | Romper la consulta pública o la salvaguarda | 1 | 5 | Los controles no tocan `domain/` ni `application/`; arnés de 248 y E2E antes y después |

## 5. Estrategia para preservar la funcionalidad

- **Modo local idéntico:** pytest, Vitest, E2E (19 de 20 en esta máquina; la que falta exige Ollama) y
  Newman (39/39) deben dar lo mismo que en la fase 1. El arnés de 248 debe seguir idéntico byte a byte.
- **Modo nube probado en local:** API local con `ENTORNO=staging` y `ADMIN_TOKEN` de prueba (generado en la
  sesión, nunca el real), para comprobar 401/403 sin token, 2xx con token, 429 al superar el límite, y que
  HU-03 a HU-07, HU-08 y RF-15 siguen respondiendo sin token.
- **No regresión por historia:** HU-01 y HU-02 (con token), HU-03 a HU-07 (consulta), HU-08.1 y RF-15
  (predicción), HU-09 (demanda pública) y RF-11 (historial por sesión en la nube; de la base en local).
- **Tras la fusión (paso 9):** comprobación en la nube solo con peticiones inocuas: escrituras sin token
  con cuerpo inválido o vacío, que deben dar 401 antes de validar (el middleware actúa antes que el
  controlador, así que nada se escribe), `GET /api/historial` → 401, y consulta pública en la interfaz.
- **Rollback:** un commit por remediación; *Revert* del PR para volver a la fase 1. Sin migraciones de base.
