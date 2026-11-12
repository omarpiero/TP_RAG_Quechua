# 07 · Auditoría final integral — Asistente de consulta del quechua wanka (versión web)

| Dato | Valor |
|---|---|
| Fecha | 2026-11-12 |
| Rol | Auditor principal de calidad y seguridad, independiente. No se modificó ningún archivo salvo este informe; ningún comando git de escritura; no se ejecutó la E2E |
| Rama auditada | `s13/owasp`, `HEAD` `ba6a746` (PR #24, apilado sobre PR #23 `5829ca1`; ambos contra `main` `1d0b129`) |
| Entradas | `03_auditoria_implementacion_furps.md`, `06_auditoria_implementacion_owasp.md` (leído ya estable, 13 331 bytes), `04_auditoria_owasp.md`, `05_plan_owasp.md`, evidencias de `docs/evidencias/s13_furps_owasp/` y estado actual de GitHub y de la nube |
| Contra la nube | Solo `GET /api/estado`, `GET /api/vivo` y `curl -sI`. Ninguna escritura ni consulta |

## 0. Estado del proyecto comprobado por este auditor

| Comprobación | Resultado |
|---|---|
| `gh pr view 23 --json state` | `OPEN`, sin fusionar (`mergedAt: null`), cabeza `5829ca1` |
| `gh pr view 24 --json state` | `OPEN`, sin fusionar, cabeza `ba6a746`, base `main` |
| `gh pr checks 23` | `backend pass 2m18s` · `frontend pass 14s` |
| `gh pr checks 24` | `backend pass 2m7s` · `frontend pass 20s` (el *backend* estaba `pending` en la primera lectura y terminó en verde) |
| `gh pr view 22` (keep-alive) | `OPEN`; según 03 sigue haciendo ping a `/api/estado` cada 10 min |
| `GET https://quechua-api.onrender.com/api/vivo` | **404**: la ruta de la fase 1 no está desplegada |
| `GET …/api/estado` | 200; `entorno: staging`, `umbral_abstencion: 0.48`, 3 607 fragmentos, PostgreSQL, Gemini. **No** incluye el booleano `escritura_protegida` que añade la fase 2: confirma que la nube sigue en `main` |
| `curl -sI …/api/estado` | `405` a `HEAD` (comportamiento conocido, E-03 de 01). Llevan ya `x-content-type-options`, `x-frame-options` y CSP de la API; no aparece `Strict-Transport-Security` |
| `git log 1d0b129..HEAD` | 14 commits: fase 1 (M-01 a M-08), auditorías 01 a 05, fase 2 (`20303f6`, `51b60da`, `abf7be2`, `ba6a746`) |
| `docs/evidencias/s13_furps_owasp/nube/salidas/` | **Vacía**: no hay ninguna verificación en la nube posterior a la fusión |

**Paso 9 del encargo: PENDIENTE y no cerrado.** No se ha fusionado ninguno de los dos PR, Render no ha
desplegado la rama y, por tanto, no se ha podido comprobar en la nube que las escrituras sin token
devuelvan 401/403 ni que la consulta pública siga funcionando tras el cambio. Todo lo que este informe
afirma de los controles nuevos procede de pruebas locales, de la CI y de las auditorías 03 y 06.

Por eso el dictamen se emite en dos planos que no deben confundirse:

- **Dictamen de la rama** (`s13/owasp`): condicionado a fusionar los PR #23 y #24, a definir `ADMIN_TOKEN`
  en Render y a la verificación en la nube del paso 9.
- **Estado de la nube hoy** (`main` `1d0b129`): lo que está expuesto al público en esta fecha.

---

## 1. Resumen ejecutivo

La fase 1 (FURPS+) implementó 7 de 8 mejoras y dejó una parcial (M-02: `/api/vivo` existe pero el
keep-alive del PR #22 sigue apuntando a `/api/estado`); el puntaje FURPS+ de la rama pasa de 6,9 a 7,4.
La fase 2 (OWASP) corrigió el crítico OW-01 y los altos OW-02, OW-04, OW-05 y OW-16, dejó seis
hallazgos parciales y seis sin corregir (tres de ellos aceptados por el plan); el score OWASP de la rama
pasa de 61,0 a 79,0 y se levanta la regla de veto por crítico. En ambas fases el arnés de 248 consultas
es idéntico byte a byte a la línea base (τ = 0,48: VP 180 · FP 0 · VN 28 · FN 0), el verificador literal
de ADR-028 no se tocó y el único fallo E2E es preexistente (depende de Ollama en el equipo).

La rama es, por tanto, sustancialmente mejor que lo desplegado. Pero **la nube sigue hoy con el corpus,
las fuentes y el historial escribibles sin autenticación** (OW-01 crítico abierto, score 61,0), y la
mejora solo existe para el público cuando alguien fusione, defina el token y lo compruebe.

| Dimensión | Rama (condicionada) | Nube hoy |
|---|---|---|
| Calidad | **Cumple parcialmente FURPS+** | Cumple parcialmente (6,9; críticos R-01 y PLUS-01 abiertos) |
| Seguridad | **Cumple parcialmente OWASP Top 10** (79,0; sin críticos) | **No cumple** (61,0; OW-01 crítico) |
| Funcionalidad | **Se preservó la funcionalidad existente** (con riesgos de regresión operativa en el despliegue, §5) | Sin cambios |
| Riesgo operativo | **Medio** | **Alto** |
| Recomendación | **Apto para producción con observaciones**, condicionado | **No apto para producción** |

---

## 2. Estado de calidad (FURPS+)

Fuente: 03, que reprodujo pytest, Vitest, oxlint, *build*, arnés y las rutas nuevas.

| Categoría | Antes | Rama (03) | Pendiente principal |
|---|---:|---:|---|
| F | 8,0 | 8,0 | F-01, F-02 (acción de personas), F-03 (PF-01..PF-17 sin registrar) |
| U | 6,5 | 7,75 | U-02 parcial (`Historial.jsx:15,37`), OBS-01/02 (texto del aviso de espera) |
| R | 6,0 | 6,75 | R-02 solo preparado (sin ping a `/api/vivo` ni medición del arranque en frío), R-03, R-05 |
| P | 6,5 | 6,5 | P-01, P-02, P-03 |
| S | 8,5 | 9,25 | S-01 parcial, S-02 |
| + | 6,0 | 6,25 | PLUS-02, PLUS-04; PLUS-03 parcial |
| **Global** | **6,9** | **7,4** | |

Lectura del auditor final: el 7,4 de 03 se calculó **antes** de la fase 2. Varias remediaciones OWASP
atacan hallazgos FURPS+ que 03 dejó abiertos: R-01 (borrado anónimo del historial) coincide con OW-02,
corregido; PLUS-01 (alteración pública del corpus) con OW-01, corregido; U-03 (historial compartido)
con OW-03, parcial; P-01 y R-03 (sin límite de carga) con OW-08, parcial. Es razonable esperar que el
puntaje FURPS+ de la rama supere 7,4, pero **nadie lo ha recalculado** y este informe no inventa la
cifra: queda **por medir**. Mientras F-03, R-02 y S-01 sigan abiertos y la rama no esté desplegada, el
veredicto es **Cumple parcialmente FURPS+**.

---

## 3. Estado de seguridad (OWASP Top 10)

Fuente: 06, con sonda de caja negra sobre el `app` real y evidencia `08_controles_modo_nube_local.txt`
(401 sin token, 403 con token incorrecto, 201/204/200 con token, 429 al superar 20 consultas/min,
bitácora `[SEGURIDAD]` sin token ni IP en claro).

| Cat. | Antes | Rama | Estado en la rama |
|---|---:|---:|---|
| A01 Broken Access Control | 0 | 7 | OW-01/02/04/05 corregidas; OW-03 parcial (`/api/analitica/demanda` pública por consigna) |
| A02 Cryptographic Failures | 9 | 10 | HSTS en modo nube |
| A03 Injection | 9 | 9 | OW-07 aceptada (mitigada por ADR-028) |
| A04 Insecure Design | 4,5 | 6,5 | OW-08 parcial (límite en memoria, evadible rotando o falsificando la IP), OW-09 parcial |
| A05 Security Misconfiguration | 5,5 | 6 | **OW-10 (CSP del sitio estático) y OW-12 (OpenAPI) no implementadas** pese a figurar en RM-06 |
| A06 Vulnerable Components | 6,5 | 6,5 | **OW-14 (`npm audit fix` y paso en la CI) no implementada** pese a figurar en RM-07 |
| A07 Authentication Failures | 5 | 9 | OW-16 corregida; NV-02 (token sin longitud mínima ni límite de intentos) |
| A08 Integrity Failures | 4,5 | 6,5 | OW-17 parcial (sin cuarentena), OW-18 parcial (Swagger desde CDN sin SRI) |
| A09 Logging and Monitoring | 7 | 8,5 | OW-19 parcial (sin persistencia ni alertas); NV-01 (seudónimo sin sal) |
| A10 SSRF | 10 | 10 | — |
| **Score** | **61,0** | **79,0** | Sin críticos ni altos abiertos |

Veredicto: **Cumple parcialmente OWASP Top 10** en la rama (no quedan críticos ni altos; quedan medios
en A01, A04, A05, A06 y A08). En la nube hoy: **No cumple** (OW-01 crítico, regla de veto).

Desviación de proceso que se anota: el plan 05 comprometía RM-06 (CSP, OpenAPI) y RM-07 (`npm audit`)
completos; 06 los encontró sin implementar. No es una regresión, pero el informe de la fase 2 debe
declararlo como incumplimiento parcial del plan y no como remediación hecha.

---

## 4. Funcionalidad

| Evidencia | Resultado |
|---|---|
| Arnés de 248 consultas (fase 1 y fase 2) | Idéntico byte a byte a la línea base (03 y 06, `cmp`) |
| pytest | 365 → 378 (fase 1) → **416 aprobadas, 6 omitidas, cobertura 90 %** (`pytest_fase2.txt`) |
| Vitest | 34 → 43 → **45/45** (8 ficheros), reproducido por 06 |
| E2E Playwright | 19 aprobadas, 1 fallida, 1 omitida **antes y después** (misma prueba, `estado.real.spec.js`, depende de Ollama). No reproducida por regla |
| CI | Verde en PR #23 y PR #24 |
| Modo local | Sin token, sin límite y sin HSTS, como antes (pruebas de 06, E1) |
| Consulta y predicción públicas en modo nube (local) | 200 sin token, también desde otra IP |

Veredicto: **Se preservó la funcionalidad existente** en la rama. La interfaz pública de administración
pasa a solo lectura sin token y el historial público pasa a ser por sesión: son cambios intencionales
(ADR-035, ADR-036), no regresiones. Lo que no se puede afirmar es que se preserve **en la nube**,
porque no se ha desplegado: los riesgos de §5 (R-A a R-D) son riesgos de regresión operativa abiertos
hasta el paso 9.

---

## 5. Riesgos pendientes

| ID | Riesgo | Plano | Nivel | Tratamiento |
|---|---|---|---|---|
| R-A | Corpus, fuentes e historial escribibles y borrables por cualquiera (OW-01..04) | **Nube hoy** | **Alto** | Fusionar #23 y #24 y verificar (paso 9) |
| R-B | Se despliega sin `ADMIN_TOKEN`: administración en 403 (falla segura, NV-04) | Despliegue | Medio | Definirlo en Render (`render.yaml` no lo declara) con ≥ 32 caracteres |
| R-C | `humo_nube.py` y Newman fallan en el CRUD de fuentes sin `X-Admin-Token` | Despliegue | Bajo | Exportar `ADMIN_TOKEN` del operador; anotarlo en el runbook |
| R-D | Límite de peticiones evadible si Render/Cloudflare no sobrescribe `CF-Connecting-IP`/`X-Forwarded-For` (NV-03); se reinicia con cada reposo | Rama | Medio | Verificar en la nube; usar el último salto de `X-Forwarded-For` |
| R-E | PR #22 fusionado tal cual: ping 24/7 a `/api/estado` despierta Neon (RE-04 de 03) | Operación | Medio | Cambiar el ping a `/api/vivo` y a una franja horaria antes de fusionarlo |
| R-F | OW-10 y OW-14 sin implementar (CSP del sitio estático; avisos altos de dependencias de desarrollo) | Rama | Medio | Meta CSP en *build* y `npm audit fix` + paso en la CI |
| R-G | OW-17: el corpus sigue sin cuarentena; la integridad depende de la custodia de un token único compartido, sin identidad ni rotación | Rama | Medio | Custodia y rotación del token; cuarentena como trabajo futuro |
| R-H | NV-01 seudónimo sin sal; NV-02 sin límite de intentos del token; OW-12; OW-18 | Rama | Bajo | Ver 06 §6 |
| R-I | Puntaje FURPS+ posterior a la fase 2 y arranque en frío tras `/api/vivo`: sin medir | Calidad | Bajo | Recalcular y capturar en `nube/` tras desplegar |

**Riesgo operativo.** Rama desplegada con token y verificada: **Medio** (sin críticos ni altos, pero con
R-D, R-F y R-G abiertos y un único secreto compartido como control de toda la administración).
Nube hoy: **Alto**.

---

## 6. Observaciones

1. **El paso 9 no está cerrado.** `nube/salidas/` está vacía y `/api/vivo` da 404. Ningún documento de la
   serie debe presentar los controles como desplegados.
2. **06 se leyó cuando ya era estable** (tres lecturas de igual tamaño con 20 s de intervalo). Sus cifras
   de la sonda E3 se aceptan; este auditor no repitió la sonda.
3. **Los documentos 03 a 07 y parte de las evidencias no están necesariamente en los PR.** 03 y 04/05 sí
   están en commits; 06 y este 07 están en el árbol de trabajo sin commit (por regla de este auditor).
4. **La cabecera CSP observada en `curl -sI` de la API desplegada** pertenece a la API; OW-10 se refiere
   al sitio estático, y 06 confirma que el HTML servido no la lleva. No hay contradicción.
5. **La ráfaga de `08_controles_modo_nube_local.txt`** muestra 19 respuestas 200 y 2 429 en vez de
   20 + 1: la consulta previa con acentos mal codificados también contó contra el límite. Es coherente
   con 20/min; conviene aclararlo en la evidencia.
6. **La salvaguarda central está intacta**: τ = 0,48 en `config.py`, verificador literal sin cambios,
   0 falsos positivos en C. Ninguna remediación tocó `domain/` ni `application/`.

---

## 7. Recomendación final

- **Rama `s13/owasp` (PR #23 + PR #24): Apto para producción con observaciones**, condicionado a:
  (1) fusionar el PR #23 y luego el #24; (2) definir `ADMIN_TOKEN` en Render; (3) completar el paso 9 en
  la nube solo con peticiones inocuas (escrituras sin token con cuerpo vacío → 401, `GET /api/historial`
  → 401, `GET /api/vivo` → 200, `curl -sI` con HSTS, una consulta pública desde la interfaz) y guardar
  las salidas en `docs/evidencias/s13_furps_owasp/nube/salidas/`. Si alguna comprobación falla, el
  dictamen pasa a **No apto** y se revierte el PR #24.
- **Nube hoy (`main` `1d0b129`): No apto para producción** como servicio público, por OW-01 crítico
  abierto.

### Pendientes para personas

1. Revisar y fusionar el PR #23 y después el PR #24 (CI verde en ambos).
2. Dueño de Render: crear `ADMIN_TOKEN` (aleatorio, ≥ 32 caracteres), sin registrarlo en el repositorio.
3. Ejecutar el paso 9 en la nube y guardar las evidencias en `nube/salidas/`.
4. Ajustar el PR #22 (ping a `/api/vivo`, franja horaria) antes de fusionarlo; medir de nuevo el arranque en frío.
5. Con el token, retirar los dos PDF de prueba de Neon; dueño de Neon: rol sin DDL (OW-13).
6. Programar OW-10 (CSP del sitio estático) y OW-14 (`npm audit fix` + paso en la CI), comprometidos en el plan.
7. Recalcular el puntaje FURPS+ tras la fase 2 y registrar F-03 (PF-01..PF-17).
8. Hacer commit de `06_auditoria_implementacion_owasp.md` y de este informe en el PR #24.

---

## Adenda · Verificación del paso 9 en la nube (2026-11-12, 22:45–22:50 UTC)

Añadida por el agente principal tras fusionar #23 y #24 (`main` `eba7ce7`). La CI de `main` está en verde en los dos *merges* y Render desplegó: `GET /api/vivo` → 200 y `/api/estado` → `escritura_protegida: true`. Solo se enviaron peticiones inocuas: cuerpos inválidos o IDs inexistentes, que no escribirían aunque el control fallara, y consultas como origen `humo` con el token de pruebas. Los tokens no aparecen en ninguna evidencia.

| Comprobación | Resultado en la nube | Evidencia |
|---|---|---|
| `GET /api/historial` sin token | **401** | `nube/salidas/09_verificacion_nube.txt` · `nube/09_A01_escrituras_sin_token_401_403_nube.png` |
| `POST`/`PUT`/`DELETE /api/fuentes`, `POST /api/corpus/documentos` sin token | **401** en todos | ídem |
| `POST /api/fuentes` con token incorrecto | **403** | ídem |
| Con `ADMIN_TOKEN` (ya definido en Render) | historial **200**; `POST /api/fuentes {}` → **422** (token aceptado, no escribe) | `nube/salidas/09_verificacion_nube_con_tokens.txt` · `nube/09_A01_con_admin_token_y_consulta_publica_nube.png` |
| Consulta pública sin token de administración | **200**, redactada por Gemini, documento y página (p. 37), similitud 0,607 ≥ 0,48 | ídem |
| Abstención pública | `abstenida=true`, 0 respaldos, similitud 0,050 < 0,48 | ídem |
| Predicción pública y consulta vacía | 200 y 422 (no 401) | ambas salidas |
| HSTS en la API · CORS desde un origen ajeno | `max-age=31536000; includeSubDomains` · 400 | `09_verificacion_nube.txt` |
| Interfaz pública | Consultar y Predicción ML operativas; Fuentes e Incorporar en «Modo solo lectura» | `nube/09_F_*.png`, `nube/09_A01_*_solo_lectura_nube.png` |
| CI | `main` en verde tras #23 y #24 | `nube/09_CI_main_verde_github_actions.png` |

**Paso 9: cerrado.** Se cumplen las tres condiciones del dictamen condicionado: los PR están fusionados,
`ADMIN_TOKEN` está definido y la verificación en la nube se superó. El dictamen pasa a **apto para producción
con observaciones** también para la nube, que ahora puntúa **79,0 / 100** en OWASP. Las observaciones son las
de los riesgos pendientes: OW-03 (demanda agregada pública), OW-08 y NV-03 (límite en memoria), OW-10, OW-12,
OW-14, OW-17, NV-01, NV-02 y R-02, que depende del PR #22. El agente principal no evaluó si el despliegue
cambia los puntajes FURPS+ de R y P más allá de lo medido.
