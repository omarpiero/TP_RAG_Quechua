# 02 · Plan de mejora FURPS+ — Asistente de consulta del quechua wanka (versión web)

| Dato | Valor |
|---|---|
| Fecha | 2026-11-12 |
| Entrada | `docs_auditoria/01_auditoria_furps.md` (global 6,9 / 10; 2 críticos, 4 altos, 10 medios, 8 bajos) |
| Rama | `s13/furps-owasp`, sobre `main` `1d0b129` |
| Rol | Arquitecto de software (planificador). Este documento planifica; la aplicación es el paso 3 |
| Restricción principal | **El sistema ya funciona y está desplegado** (Render + Neon + Gemini). Ninguna mejora puede poner en riesgo la consulta pública, la salvaguarda (τ = 0,48, RN-06, verificador literal de ADR-028) ni la versión de escritorio |

## 1. Principios de ejecución

1. **Compatibilidad hacia atrás.** Ningún endpoint cambia de ruta, método ni forma de respuesta. Solo se
   **añade** una ruta (`GET /api/vivo`) y se acotan parámetros que hoy producen un 500.
2. **Cambios incrementales.** Un commit por mejora, cada uno revertible con `git revert <sha>` sin
   arrastrar a los demás.
3. **Riesgo mínimo.** No se toca el dominio, la recuperación, el umbral, los modelos ni el generador.
4. **Validación obligatoria antes y después de cada cambio:** pytest, Vitest, E2E Playwright, arnés de 248
   consultas (el corpus `fragmentos_v3.jsonl` se reconstruyó en local y su SHA-256 coincide con el de la U3:
   `d6200ed9…70a`) y Newman local. Si una batería falla, el commit se revierte antes de seguir.
5. **Rollback.** Por commit (`git revert`) y, tras la fusión, por PR (botón *Revert* de GitHub). Render
   redespliega el estado anterior en cuanto la CI del revert queda en verde (`autoDeployTrigger: checksPass`).

### 1.1 Línea base medida para este plan (2026-11-12, antes de cualquier cambio)

| Batería | Resultado | Evidencia |
|---|---|---|
| pytest (con corpus, sin PostgreSQL) | 365 aprobadas, 6 omitidas (requieren PostgreSQL) | `docs_auditoria/evidencias/antes/salidas/pytest_antes.txt` |
| Vitest | 34/34 | `…/antes/salidas/vitest_antes.txt` |
| Arnés 248 (τ 0,48) | con lema: VP 180 · FP 0 · VN 28 · FN 0 · sin lema: A+B 165/180, F1 0,9565 | `…/antes/salidas/arnes/`, `arnes_antes.txt` |
| E2E Playwright | ver `e2e_antes.txt` (generador `extractivo`, sin Ollama en esta máquina) | `…/antes/salidas/e2e_antes.txt` |
| Arranque en frío en la nube | `GET /api/estado` → 200 en **72,65 s** | `…/antes/salidas/arranque_estado_antes.txt` |

## 2. Reparto de hallazgos entre fases

Varios hallazgos FURPS+ son, en su raíz, controles de seguridad. Para no aplicar dos veces el mismo control
ni dividir un cambio de autorización en dos PR, **se remedian en la fase 2 (OWASP)**, donde tienen su ADR:

| Hallazgo FURPS+ | Severidad | Dónde se resuelve | Motivo |
|---|---|---|---|
| R-01 borrado anónimo del historial | Crítica | Fase 2 · A01 | Es un control de autorización |
| PLUS-01 escritura pública de corpus y fuentes | Crítica | Fase 2 · A01 | Ídem; requiere `ADMIN_TOKEN` y ADR |
| U-03 historial compartido | Alta | Fase 2 · A01/privacidad | Decisión de diseño con ADR |
| P-01 sin límite de peticiones | Alta | Fase 2 · A04 | Control anti-abuso |
| R-03 cuota de Gemini | Media | Fase 2 · A04 | Lo cubre el límite de peticiones |
| PLUS-02 CSP del sitio estático, HSTS | Media | Fase 2 · A05 | Configuración de seguridad |
| PLUS-04 CORS con credenciales | Baja | Fase 2 · A05 | Ídem |
| P-02 ingesta y reindexado en la petición | Media | Fase 2 (mitigación indirecta) | Al exigir token, solo el administrador puede lanzarlos |

**Fuera del alcance de un agente (acción para personas):** F-01 (demanda real de HU-09: hacen falta
consultas reales, no se fabrican), F-02 (retirar los 2 PDF de prueba de Neon: la base es de otro integrante),
R-05 (almacenamiento persistente de PDF en Render: requiere un disco de pago o un almacén externo) y PLUS-03
(límites del plan free: decisión de presupuesto).

## 3. Mejoras priorizadas (fase 1)

### M-01 · Aviso de arranque en frío en la interfaz (REF-02) — **Alta**

| Campo | Contenido |
|---|---|
| Hallazgos | U-01 (alta), R-02 (alta, cara visible), U-02 (media, parcial) |
| Objetivo | Que el visitante sepa que el servicio se está activando y cuánto puede tardar, en lugar de ver «Sin conexión con el servicio local» |
| Justificación | La U3 midió 62–72 s y hoy se midieron 72,65 s; la interfaz no dice nada durante ese tiempo (`App.jsx:86-91`, `EstadoInicial.jsx:17-23`) y un evaluador puede abandonar creyendo que el sistema está caído (RA-03, exposición 12) |
| Cambio | Si `/api/estado` o una consulta tardan más de 4 s, se muestra un aviso `role="status"` («el servicio se está activando; la primera respuesta puede tardar hasta un minuto»). Si `/api/estado` falla, se ofrece «Reintentar» y un mensaje propio de la web. Solo interfaz; no cambia la API |
| Riesgo | Bajo: componente nuevo, sin lógica de negocio. Riesgo de romper aserciones de texto en Vitest/E2E (`App.test.jsx:179`, `EstadoInicial.test.jsx:41`): se conserva el `data-testid` y se actualizan las pruebas |
| Dependencias | Ninguna |
| Validación | Vitest nuevo con temporizador simulado (aviso a los 4 s, desaparece al responder) · E2E existentes en verde · captura local con la API retrasada |
| Rollback | `git revert` del commit; la interfaz vuelve al texto anterior. Sin efecto en datos |

### M-02 · Mantener el servicio despierto (REF-01) sin despertar la base — **Alta**

| Campo | Contenido |
|---|---|
| Hallazgos | R-02 (alta), PLUS-03 (media), S-04 (baja) |
| Objetivo | Reducir el arranque en frío sin agotar las horas gratuitas de Render ni las de Neon |
| Situación encontrada | Ya existe el PR abierto [#22](https://github.com/omarpiero/TP_RAG_Quechua/pull/22) (otro integrante) con `.github/workflows/keepalive.yml`: `GET /api/estado` cada 10 min, 24/7. **No se duplica**: se complementa |
| Análisis de horas | **Render free:** 750 h de instancia al mes por *workspace*; si se agotan, Render suspende **todos** los servicios free del *workspace* hasta el mes siguiente; un servicio dormido no consume horas ([Render, *Deploy for Free*](https://render.com/docs/free)). 24/7 = 720–744 h: deja 6–30 h de margen para cualquier otro servicio free de ese *workspace*, que no es nuestro. **Neon free:** 100 CU-h al mes y suspensión a los 5 min ([Neon, *Free plan limits*](https://neon.com/faqs/free-plan-limits-and-quotas)). `/api/estado` consulta la base (`consultas_por_origen`, `documentos_corpus`), de modo que un ping cada 10 min despierta Neon ~5 de cada 10 min: ~360 h × 0,25 CU ≈ **90 CU-h**, casi toda la cuota mensual. **GitHub Actions:** el repositorio es público, así que los minutos no se facturan |
| Decisión | (1) Añadir `GET /api/vivo`: responde `{"vivo": true}` **sin tocar la base ni Gemini**, para que el ping mantenga despierto a Render y deje que Neon se suspenda. (2) Recomendar en el PR #22 que el ping apunte a `/api/vivo` y que se limite a una franja (p. ej. `*/10 11-23,0-4 * * *` UTC = 06:00–23:59 de Perú, ~18 h/día ≈ 560 h/mes), lo que deja ~190 h de margen. La decisión de fusión es del equipo (acción para personas) |
| Riesgo | Muy bajo: ruta nueva, de solo lectura y sin estado |
| Dependencias | PR #22 para el efecto completo |
| Validación | Prueba unitaria: `/api/vivo` responde 200 aunque la base no esté disponible y no llama al contenedor · Newman/E2E sin cambios |
| Rollback | `git revert`; el PR #22 sigue funcionando con `/api/estado` |

### M-03 · Mensajes propios de la versión web — **Media**

| Campo | Contenido |
|---|---|
| Hallazgos | U-02 (media) |
| Objetivo | Que los errores de red y de validación digan algo cierto en la nube |
| Cambio | `api.js`: si la API es remota (`VITE_API_URL` definido), el error de red dice «No se pudo conectar con el servicio en la nube. Si estuvo sin uso, puede tardar hasta un minuto en activarse: vuelva a intentarlo». En local se conserva el texto actual. Un 422 con `detail` de texto (p. ej. validación de una fuente) muestra ese texto en lugar del mensaje fijo de la consulta. Pie: «Sin conexión con el servicio» sin «local» cuando la API es remota |
| Riesgo | Bajo. El texto del confirm del historial («de este equipo») cambia con la fase 2 (historial), no aquí |
| Validación | Vitest: mensaje local y remoto; 422 con detalle de texto |
| Rollback | `git revert` |

### M-04 · Acotar parámetros de los GET — **Media**

| Campo | Contenido |
|---|---|
| Hallazgos | R-04 (media) |
| Objetivo | Que `limite` (historial) y `top` (demanda) fuera de rango devuelvan 422 en lugar de un 500 de la base |
| Cambio | `Query(ge=1, le=500)` en `limite` y `Query(ge=1, le=100)` en `top`. Los valores por defecto (50 y 15) y los que usa la interfaz no cambian |
| Riesgo | Bajo. Ningún cliente conocido usa valores fuera de esos rangos (`api.js`, colección Postman) |
| Validación | pytest: `limite=-1`, `limite=0`, `limite=501` y `top=0` → 422; valores por defecto → 200 |
| Rollback | `git revert` |

### M-05 · Documentación de REF-01/REF-02 y de la decisión de horas — **Media**

| Campo | Contenido |
|---|---|
| Hallazgos | S-04 (baja), F-03 (baja, parcial) |
| Cambio | ADR-033 (aviso de arranque en frío) y ADR-034 (`/api/vivo` y presupuesto de horas del ping) en `docs/07_DECISIONES.md`; `/api/vivo` en la tabla de endpoints del `README.md` |
| Riesgo | Nulo |
| Rollback | `git revert` |

### M-06 · Retirar `pytest` de las dependencias de producción — **Baja**

| Campo | Contenido |
|---|---|
| Hallazgos | S-03 |
| Cambio | Quitar `pytest==9.2.0` de `backend/requirements.txt` (`requirements-dev.txt` ya declara `pytest>=9.0.3`). Ningún módulo de `backend/src` importa `pytest` (comprobado con `grep`) |
| Riesgo | Bajo: el *build* de Render instala menos; la CI instala `requirements-dev.txt` |
| Validación | CI en verde; `pip-audit -r requirements.txt` sigue en 0 |
| Rollback | `git revert` |

### M-07 · Estado activo de las pestañas para lectores de pantalla — **Baja**

| Campo | Contenido |
|---|---|
| Hallazgos | U-04 |
| Cambio | `aria-current="page"` en la pestaña activa. Se conserva el rol `button` para no romper los selectores existentes (`getByRole("button", {name})` en E2E y capturas) |
| Riesgo | Muy bajo |
| Validación | Vitest: la pestaña activa expone `aria-current` |
| Rollback | `git revert` |

### M-08 · Calidad en la CI: lint y umbral de cobertura — **Baja**

| Campo | Contenido |
|---|---|
| Hallazgos | S-01 (parcial) |
| Cambio | `--cov=src --cov-fail-under=85` en el paso pytest de la CI y paso `npx oxlint` en el *job* del frontend (hoy da 3 avisos y ningún error, de modo que no bloquea) |
| Riesgo | Bajo-medio: si la cobertura de la CI quedara por debajo del 85 %, la CI fallaría. Medido en local sin corpus: 88 %; con corpus, mayor |
| Validación | CI del PR en verde |
| Rollback | `git revert` del commit de la CI |

**Descartado en esta fase:** cambiar las pestañas a `role="tab"` (rompería selectores E2E sin ganancia
funcional) y mover la ingesta a una tarea en segundo plano (P-02: cambio arquitectónico que la guía pide
evitar; se mitiga con la autorización de la fase 2).

## 4. Roadmap y orden recomendado

| Orden | Mejora | Prioridad | Commit previsto | Depende de |
|---|---|---|---|---|
| 1 | M-04 parámetros acotados | Media | `fix(api): acota limite y top` | — |
| 2 | M-02 `/api/vivo` | Alta | `feat(api): ruta de vida sin base (REF-01)` | — |
| 3 | M-01 aviso de arranque en frío | Alta | `feat(web): aviso de arranque en frío (REF-02)` | — |
| 4 | M-03 mensajes de la web | Media | `fix(web): mensajes propios de la versión web` | M-01 (mismos archivos) |
| 5 | M-07 `aria-current` | Baja | `fix(a11y): pestaña activa anunciada` | — |
| 6 | M-06 dependencias | Baja | `chore(deps): pytest fuera de producción` | — |
| 7 | M-08 CI | Baja | `ci: lint y umbral de cobertura` | — |
| 8 | M-05 documentación | Media | `docs: ADR-033 y ADR-034` | M-01, M-02 |

Primero el backend (cambios aditivos, cubiertos por pytest), después la interfaz y al final la CI y la
documentación, para que un fallo de la CI no se confunda con un fallo funcional.

## 5. Riesgos de ejecución

| ID | Riesgo | P | I | Mitigación |
|---|---|---:|---:|---|
| RE-01 | Una prueba E2E o Vitest depende del texto antiguo | 3 | 2 | Conservar `data-testid`; actualizar solo aserciones de texto, en el mismo commit |
| RE-02 | El umbral de cobertura falla en la CI | 2 | 2 | 85 % frente a 88 % medido; si falla, se baja o se revierte el commit M-08 sin tocar el resto |
| RE-03 | La E2E local no reproduce la de la U3 (sin Ollama) | 3 | 2 | Generador `extractivo` en local; se comparan antes y después en las mismas condiciones |
| RE-04 | Se fusiona el PR #22 sin el ajuste y Neon agota su cuota | 2 | 3 | Recomendación documentada en el PR de la fase 1 y en ADR-034 |
| RE-05 | Un cambio toca la salvaguarda por accidente | 1 | 5 | Ningún archivo de `domain/`, `application/` ni de generación está en el alcance; el arnés se repite después |

## 6. Estrategia de preservación de funcionalidad

- **Alcance cerrado:** solo `adapters/in/rest/` (rutas), `frontend/src/` (interfaz), CI, dependencias y
  documentación. `domain/`, `application/`, la recuperación, el umbral, los modelos y los generadores no se tocan.
- **Mismas baterías antes y después, en las mismas condiciones:** pytest, Vitest, E2E, arnés 248 y Newman
  local. Se compara contra la tabla de §1.1. Cualquier diferencia en el arnés (VP, FP, VN, FN) bloquea la fusión.
- **Historias de no regresión:** HU-01 a HU-09 y RF-15 deben seguir pasando sus pruebas existentes.
- **Despliegue:** Render solo despliega si la CI del merge está en verde. Tras la fusión se verifica
  `/api/estado` y `/api/vivo` en la nube con peticiones `GET`.
- **Rollback:** `git revert` por commit o *Revert* del PR; no hay migraciones de base ni cambios de esquema,
  así que el retorno es inmediato y sin pérdida de datos.
