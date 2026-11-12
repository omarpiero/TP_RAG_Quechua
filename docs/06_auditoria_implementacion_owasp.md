# 06 · Auditoría de implementación OWASP (S13, fase 2)

**Rol.** Auditor independiente de seguridad. **Fecha.** 2026-11-12.
**Entradas.** `04_auditoria_owasp.md` (19 hallazgos OW-01 a OW-19, score 61,0), `05_plan_owasp.md`
(RM-01 a RM-08), rama `s13/owasp` (PR #24, cabeza `ba6a746`), diferencias `git diff 5829ca1..HEAD`.
**Criterio.** Ninguna remediación se da por buena sin evidencia reproducida en esta auditoría. La nube
pública sigue en `main` (`1d0b129`), sin estos cambios: todo lo que sigue describe **la rama**.

---

## 1. Método y evidencia reproducida

| # | Verificación | Resultado obtenido por el auditor |
|---|---|---|
| E1 | `pytest -q tests/unit/infrastructure/test_s13_owasp.py tests/unit/adapters/in/rest/test_ingesta_tope.py` | **41 passed** |
| E2 | `npx vitest run` (frontend) | **45 passed** (8 archivos) |
| E3 | Sonda de caja negra sobre el `app` **real** de `infrastructure/main.py` con `ENTORNO=nube`, `ADMIN_TOKEN` de prueba y `LIMITE_CONSULTAS_POR_MINUTO=2` (TestClient, sin ciclo de vida) | Ver §2; confirma el orden real de los middlewares, no solo el de las pruebas |
| E4 | `cmp` de `antes/salidas/arnes/{arnes_por_consulta.csv, barrido_umbral.csv, resumen_arnes.json}` frente a `despues/salidas/arnes_fase2/` | **Idénticos byte a byte** |
| E5 | Lectura de `despues/salidas/pytest_fase2.txt` (416 passed, 6 skipped, cobertura 90 %), `e2e_fase2.txt` y `e2e_antes.txt` | E2E 19 passed, 1 failed, 1 skipped **en ambas** corridas (mismo test) |
| E6 | Revisión de código: `seguridad_nube.py`, `main.py`, `corpus_controller.py`, `config.py`, `api.js`, `ci.yml`, `render.yaml`, `package-lock.json` | §2 y §3 |
| E7 | `umbral_abstencion: float = 0.48` en `config.py`; verificador literal (ADR-028) no tocado por el diff | Intocables respetados |

Resultado de la sonda E3 (códigos HTTP reales):

| Petición (modo nube) | HTTP | Lectura |
|---|---:|---|
| `POST /api/fuentes` sin token / token incorrecto | 401 / 403 | Correcto, falla segura |
| `DELETE /api/historial` sin token | 401 | Correcto |
| `GET /api/historial` y `GET /api/historial/` sin token | 401 / 401 | Correcto (barra final normalizada) |
| `HEAD /api/historial` · `GET /API/historial` | 405 · 404 | Sin evasión por método ni por mayúsculas |
| `POST /api/corpus/documentos` · `POST /api/corpus/reindexar` sin token | 401 · 401 | Correcto: cierra OW-01 |
| `GET /api/analitica/demanda` sin token | 500 (sin ciclo de vida) | **No pasa por el token**: sigue pública (riesgo aceptado en RM-02) |
| 3.ª `POST /api/consultas` con la misma IP (límite 2) | 429 | Límite operativo |
| Misma ráfaga cambiando `X-Forwarded-For` o `CF-Connecting-IP` | pasa (500 por falta de ciclo de vida, no 429) | **El límite se evade cambiando la cabecera de IP** si la petición no atraviesa un proxy que la sobrescriba |
| Respuestas 401/403/429/200 | `Strict-Transport-Security: max-age=31536000; includeSubDomains` | HSTS presente |
| `GET /docs`, `/openapi.json` | 200; `securitySchemes: []` | `/docs` público y **sin** esquema de seguridad declarado |
| Preflight desde `https://evil.example` | 400 | CORS rechaza orígenes ajenos |

---

## 2. Estado de cada vulnerabilidad

| ID | Sev. original | Estado | Evidencia | Severidad residual |
|---|---|---|---|---|
| OW-01 | Crítico 20 | **Corregida** | E3: ingesta y reindexado → 401 sin token; `requiere_admin` protege por defecto toda escritura en `/api` salvo `/api/consultas` y `/api/predicciones`; `hmac.compare_digest`; `ADMIN_TOKEN` vacío → 403 | — |
| OW-02 | Alto 12 | **Corregida** | E3: `DELETE /api/historial` → 401; `08_controles_modo_nube_local.txt` | — |
| OW-03 | Alto 12 | **Parcialmente corregida** | `GET /api/historial` → 401 y el público ve historial por sesión (Vitest `Nube.s13.test.jsx`); pero `GET /api/analitica/demanda` sigue público (E3), exponiendo términos agregados de consultas sin respaldo | Medio (I2×P3 = 6) |
| OW-04 | Alto 12 | **Corregida** | E3: `POST /api/fuentes` 401/403; PUT/DELETE cubiertos por `requiere_admin` (pruebas unitarias) | — |
| OW-05 | Alto 10 | **Corregida** | `resolver_recurso_interfaz` usa `resolve()` + `is_relative_to`; pruebas con `..`, `%2e%2e`, absoluta y `assets/..` en verde (E1) | — |
| OW-06 | Bajo 4 | **Corregida (en la rama)** | E3: HSTS en todas las respuestas en modo nube | — |
| OW-07 | Bajo 4 | **No corregida (aceptada)** | Sin cambios; mitigada por ADR-028; banco adversario «por medir» | Bajo 4 |
| OW-08 | Alto 12 | **Parcialmente corregida** | E3: 429 con `Retry-After`. Residuales: memoria de proceso (se reinicia con cada despliegue o reposo de Render), evasión rotando IP o, sin proxy, falsificando `X-Forwarded-For`; no verificado en la nube que Render/Cloudflare sobrescriba `CF-Connecting-IP` | Medio (I3×P2 = 6) |
| OW-09 | Medio 6 | **Parcialmente corregida** | Firma `%PDF-` (E1); restringida al administrador. Siguen sin límite de páginas, tiempo ni memoria descomprimida | Bajo (I3×P1 = 3) |
| OW-10 | Medio 6 | **No corregida** | Sin `<meta http-equiv="Content-Security-Policy">` ni `referrer` en `vite.config`/`index.html`; el HTML servido hoy tampoco la lleva. Declarado no implementado | Medio 6 |
| OW-11 | Bajo 4 | **Corregida** | `allow_credentials=False`, métodos y cabeceras explícitos; E3 preflight ajeno → 400 | — |
| OW-12 | Bajo 4 | **No corregida** | E3: `/docs` 200 y `securitySchemes: []`; RM-06(d) preveía declarar `X-Admin-Token` en OpenAPI y no se hizo | Bajo 4 |
| OW-13 | Bajo 4 | **No corregida (aceptada)** | `/api/estado` igual (solo añade el booleano `escritura_protegida`, sin secreto); rol de Neon fuera de alcance | Bajo 4 |
| OW-14 | Medio 6 | **No corregida** | `package-lock.json`: vite 8.3.0; `ci.yml` sin `npm audit`. Declarado no implementado | Medio 6 |
| OW-15 | Bajo 4 | **No corregida (aceptada)** | Sin hashes ni `.github/dependabot.yml` | Bajo 4 |
| OW-16 | Alto 16 | **Corregida** | Existe mecanismo de autenticación para la administración (token compartido, comparación en tiempo constante, solo en memoria de la pestaña según `api.js`). Residual en NV-02 | — |
| OW-17 | Alto 10 | **Parcialmente corregida** | La ingesta solo la ejecuta el administrador (reduce P); sigue sin cuarentena, revisión ni autoría registrada | Medio (I5×P1 = 5) |
| OW-18 | Bajo 4 | **Parcialmente corregida** | `ci.yml`: acciones fijadas por SHA; Swagger por defecto de FastAPI sigue cargándose del CDN sin SRI (`/docs` 200) | Bajo 4 |
| OW-19 | Medio 9 | **Parcialmente corregida** | Logger `rag.seguridad` con 401/403/autorizada/429 sin token (E1, `caplog`); no hay bitácora persistente ni alertas, la retención depende de Render | Bajo (I2×P2 = 4) |

Recuento: **7 corregidas** (OW-01, 02, 04, 05, 06, 11, 16), **6 parciales** (OW-03, 08, 09, 17, 18, 19),
**6 no corregidas** (OW-10, 12, 14 por omisión; OW-07, 13, 15 aceptadas en el plan).

---

## 3. Nuevas vulnerabilidades y controles mal implementados

| ID | Cat. | Sev. | Hallazgo | Evidencia | Recomendación |
|---|---|---|---|---|---|
| NV-01 | A09 | Bajo (2×2 = 4) | El seudónimo de la IP en la bitácora es `sha256(ip)[:10]` **sin sal**: el espacio IPv4 (2³²) se recorre por fuerza bruta en minutos, así que no anonimiza frente a quien lea los registros | `seguridad_nube.py`, `seudonimo()` | HMAC con una sal secreta de entorno (p. ej. derivada de `ADMIN_TOKEN` o propia) |
| NV-02 | A07 | Bajo (2×2 = 4) | Los intentos con token incorrecto (401/403) **no** están limitados: `LimitePeticiones` solo cubre `POST /api/consultas` y `/api/predicciones`. Un token largo lo hace impráctico, pero no hay control que lo exija ni rotación/caducidad (token único compartido, sin identidad) | `main.py` (límites solo para dos rutas); `config.py` (`admin_token` sin longitud mínima) | Exigir ≥ 32 caracteres al arrancar en modo nube y limitar 401/403 por IP |
| NV-03 | A04 | Informativo | `huella_cliente` confía en `CF-Connecting-IP` y luego en el **primer** `X-Forwarded-For`, ambos controlables por el cliente si la petición no pasa por Cloudflare (E3) | Sonda E3 | Verificar en la nube con `curl` que la cabecera se sobrescribe; si no, usar el último salto de `X-Forwarded-For` añadido por Render |
| NV-04 | — | Informativo (operativo) | `render.yaml` define `ENTORNO=staging` (activa los controles) pero **no** declara `ADMIN_TOKEN`; tras desplegar, la administración queda en 403 hasta que el dueño lo defina. Falla de forma segura | `render.yaml` líneas 26-27 | Añadir `ADMIN_TOKEN` con `sync: false` o `generateValue: true` |
| NV-05 | — | Informativo (calidad) | Código inalcanzable tras el `return` en `interfaz_o_recurso` | `main.py` | Eliminar la línea muerta |

No se encontró: evasión del token por método (`HEAD` → 405), por mayúsculas (404), por barra final
(401) ni por codificación (Starlette decodifica `path` antes de enrutar y antes del middleware). El token
no aparece en registros (prueba con `caplog`) ni en `localStorage`/cookies (`grep` del frontend: solo
`tamanoTexto.js` usa `localStorage`, para el tamaño de letra).

---

## 4. Regresiones funcionales

| Aspecto | Evidencia | Veredicto |
|---|---|---|
| Recuperación, abstención y umbral τ = 0,48 | E4: arnés idéntico byte a byte; E7 | Sin regresión |
| Modo local (escritorio) | Pruebas «en local, 2xx sin token / sin límite / sin HSTS» en E1; `modo_nube` = `ENTORNO != local` | Sin regresión |
| Backend completo | `pytest_fase2.txt`: 416 passed, 6 skipped | Sin regresión |
| Frontend | E2: 45 passed | Sin regresión |
| E2E | `estado.real.spec.js` falla (`aviso-sin-ollama` visible) **igual en `e2e_antes.txt`**: depende del Ollama del equipo, no del diff | Fallo preexistente, no regresión |
| Humo en la nube | `humo_nube.py` añade `X-Admin-Token` si `ADMIN_TOKEN` está en el entorno; sin él, el CRUD de fuentes del humo dará 401 tras desplegar | Regresión **operativa** prevista; documentar en el runbook |
| Interfaz pública | Pestañas de administración en solo lectura sin token (capturas `despues/08_*.png`) | Cambio intencional (ADR-035/036), no regresión |

---

## 5. Score de seguridad actualizado (fórmula de 04 §1.3)

`s_c = 10 − (base de la peor severidad + 0,5 × hallazgos adicionales, máx. 2)`; bases Crítico 8, Alto 5,
Medio 3, Bajo 1.

| Cat. | Hallazgos abiertos (residuales) | Antes | Rama |
|---|---|---:|---:|
| A01 | OW-03 Medio | 0 | 10 − 3 = **7** |
| A02 | — (OW-06 corregida) | 9 | **10** |
| A03 | OW-07 Bajo | 9 | **9** |
| A04 | OW-08 Medio, OW-09 Bajo | 4,5 | 10 − (3 + 0,5) = **6,5** |
| A05 | OW-10 Medio, OW-12 Bajo, OW-13 Bajo | 5,5 | 10 − (3 + 1) = **6** |
| A06 | OW-14 Medio, OW-15 Bajo | 6,5 | **6,5** |
| A07 | NV-02 Bajo | 5 | 10 − 1 = **9** |
| A08 | OW-17 Medio, OW-18 Bajo | 4,5 | 10 − (3 + 0,5) = **6,5** |
| A09 | OW-19 Bajo, NV-01 Bajo | 7 | 10 − (1 + 0,5) = **8,5** |
| A10 | — | 10 | **10** |
| **Total** | | **61,0** | **79,0** |

- **Score en la rama / tras desplegar con `ENTORNO=staging` y `ADMIN_TOKEN` definido: 79,0 / 100.**
  Sin hallazgos críticos: se levanta la regla de veto. Si se despliega sin `ADMIN_TOKEN`, el score de
  seguridad es el mismo (las escrituras quedan en 403), pero la administración deja de funcionar.
- **Score de la nube hoy: 61,0 / 100**, con OW-01 crítico abierto: *no apta para exposición pública*
  hasta fusionar y desplegar el PR #24. Ninguna cifra de esta sección se midió contra la nube.
- Las severidades residuales son juicio del auditor con la escala de 04 §1.2; no son mediciones.

---

## 6. Riesgos residuales priorizados

1. **OW-10 y OW-14 (Medio)**: no implementados; son los de mejor relación costo/efecto pendientes
   (meta CSP en *build* y `npm audit fix` + paso en la CI). Juntos suben A05 y A06 a 8 y 9.
2. **OW-08 (Medio)**: el límite en memoria no resiste reinicios ni IP rotativas; verificar NV-03 en la nube.
3. **OW-17 (Medio)**: el corpus sigue sin cuarentena; el riesgo depende ahora de la custodia del token.
4. **OW-03 (Medio, aceptado)**: `/api/analitica/demanda` pública por consigna; documentado en RM-02.
5. **NV-01, NV-02, OW-12, OW-18 (Bajo)**: sal en el seudónimo, longitud mínima y límite de intentos del
   token, `securitySchemes` en OpenAPI y SRI o *self-hosting* de Swagger.

---

## 7. Conclusión

Las remediaciones de alto impacto (RM-01 a RM-04) están aplicadas y verificadas con evidencia propia:
el hallazgo crítico OW-01 y los altos OW-02, OW-04, OW-05 y OW-16 quedan **corregidos en la rama**, y
la sonda sobre el `app` real confirma que el orden de los middlewares produce 401/403/429 con HSTS y CORS
correctos. RM-05, RM-07 y RM-08 están **parcialmente** aplicados y RM-06 tiene la CSP del sitio estático
(OW-10) y el esquema OpenAPI (OW-12) sin implementar; OW-14 tampoco se aplicó. No se detectaron
regresiones funcionales: el arnés de evaluación es idéntico byte a byte, τ = 0,48 y el verificador literal
no cambian, y el único fallo E2E es preexistente. Aparecen dos debilidades nuevas de severidad baja (NV-01
seudónimo sin sal, NV-02 token sin límite de intentos ni longitud mínima). El score pasa de **61,0 a
79,0** en la rama; **la nube sigue en 61,0 y no apta para exposición pública** hasta desplegar el PR #24
con `ADMIN_TOKEN` definido y comprobar en la nube, con `curl -sI`, HSTS y el 401 de una escritura.
