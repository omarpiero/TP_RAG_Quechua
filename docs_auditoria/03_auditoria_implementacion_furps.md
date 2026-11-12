# 03 · Auditoría de implementación FURPS+ — Asistente de consulta del quechua wanka (versión web)

| Dato | Valor |
|---|---|
| Fecha | 2026-11-12 |
| Rama y commit auditados | `s13/furps-owasp`, `HEAD` `dbaa6cc` (PR #23 contra `main` `1d0b129`) |
| Entradas | `docs_auditoria/01_auditoria_furps.md` (línea base, global 6,9 / 10) y `docs_auditoria/02_plan_furps.md` (M-01 a M-08) |
| Diff verificado | `git diff 1d0b129..HEAD` — commits `cc544be`, `0af3322`, `9f767b1`, `c2c06d0`, `2798d6b`, `dbaa6cc` |
| Rol | Auditor independiente. No se modificó ningún archivo salvo este informe; ningún comando git de escritura |
| Método | Lectura del diff con `ruta:línea`; **reejecución propia** de pytest, Vitest, oxlint, `npm run build` y del arnés de 248 consultas; API local en el puerto 8110 (SQLite temporal, generador `literal`) para `/api/vivo` y los 422; lectura de la CI del PR #23 con `gh`; un único `GET` contra la nube (`/api/vivo`). Ninguna escritura contra la nube |
| Límite | La rama **no está desplegada** (Render despliega `main`; la nube sigue en `1d0b129`). Toda la verificación de las mejoras es local o de CI. No se ejecutó la E2E Playwright (sobrescribe evidencias de la U3): se usan las salidas guardadas, marcadas como «no reproducido» |

---

## 1. Resumen ejecutivo

Las ocho mejoras del plan tienen cambios observables en el repositorio. Siete están **implementadas**
(M-01, M-03, M-04, M-05, M-06, M-07, M-08) y una está **parcialmente implementada**
(M-02: la ruta `/api/vivo` existe y está probada, pero el *keep-alive* del PR #22 sigue apuntando a
`/api/estado` 24/7 y la recomendación no se ha dejado en ese PR). Ninguna mejora está desplegada.

**No se encontraron regresiones.** El diff no toca `domain/`, `application/`, `adapters/out/`,
`infrastructure/`, `render.yaml` ni el corpus; el arnés de 248 consultas reejecutado por este auditor
es **idéntico byte a byte** a la línea base (τ = 0,48: VP 180 · FP 0 · VN 28 · FN 0). pytest pasa de
365 a 378 aprobadas (+13 nuevas), Vitest de 34 a 43 (+9 nuevas), la CI del PR #23 está en verde con
cobertura 89,94 %.

Los dos hallazgos **críticos** (R-01, PLUS-01) y tres de los cuatro **altos** (U-03, P-01 y, en la
práctica, R-02) siguen abiertos por diseño del plan (fase 2 OWASP o acción de personas), de modo que
el puntaje global sube de **6,9 a 7,4** y no más.

---

## 2. Comparación antes / después

### 2.1 Baterías de prueba

| Batería | Antes (`1d0b129`) | Después (`dbaa6cc`) | Quién lo midió | Evidencia |
|---|---|---|---|---|
| pytest local (corpus v3, sin PostgreSQL) | 365 aprobadas, 6 omitidas | **378 aprobadas, 6 omitidas**, cobertura 88,21 %, umbral 85 % alcanzado | Agente principal y **reejecutado por el auditor** (155 s) | `…/antes/salidas/pytest_antes.txt`, `…/despues/salidas/pytest_fase1.txt`; reejecución: `cd backend && .venv/Scripts/python -m pytest -q -p no:cacheprovider --cov=src --cov-fail-under=85` → `Required test coverage of 85% reached. Total coverage: 88.21%` · `378 passed, 6 skipped, 2 warnings` |
| pytest CI (PostgreSQL, sin corpus) | — | **374 aprobadas, 10 omitidas, 89,94 %** | CI del PR #23 (run 43315745353, `headSha dbaa6cc`) | `gh run view 43315745353 --log` → `Required test coverage of 85% reached. Total coverage: 89.94%` |
| Vitest | 34/34 (6 ficheros) | **43/43 (7 ficheros)** | Agente y **auditor** | `npx vitest run` → `Test Files 7 passed (7) · Tests 43 passed (43)` |
| oxlint | no estaba en la CI | 0 errores, 3 avisos (preexistentes, `GestionFuentes.jsx:31,67`, `PanelPrediccion.jsx:281`), código de salida 0 | **Auditor** y CI | `npx oxlint; echo $?` → `0`; CI: `Found 3 warnings and 0 errors.` |
| `npm run build` | — | correcto (`index-*.js` 259,78 kB) | **Auditor** | salida de Vite `✓ built` |
| Arnés 248 consultas, τ 0,48 | con lema VP 180 · FP 0 · VN 28 · FN 0; sin lema A+B 165/180, F1 0,9565 | **idéntico** | **Reejecutado por el auditor** en carpeta temporal | `python scripts/arnes_linea_base.py <tmp>` y `cmp` contra `…/antes/salidas/arnes/{arnes_por_consulta.csv,barrido_umbral.csv,resumen_arnes.json}` → los tres idénticos; stdout idéntico a `arnes_antes.txt`; fila `0.48,si,180,0,28,0,1.0000,…` |
| E2E Playwright (generador extractivo, sin Ollama) | 19 aprobadas, 1 fallida, 1 omitida | 19 aprobadas, 1 fallida, 1 omitida | Solo agente (**no reproducido** por regla) | `…/antes/salidas/e2e_antes.txt` y `…/despues/salidas/e2e_fase1.txt` son idénticos (`diff` vacío). La fallida es `estado.real.spec.js:14` (`aviso-sin-ollama` esperado 0, recibido 1): depende de Ollama, no del cambio |
| Newman local | 39/39 aserciones | 39/39 aserciones | Solo agente (**no reproducido**) | `newman_antes.txt` vs `newman_fase1.txt`: solo difieren duración y tiempos medios |
| CI del PR #23 | — | `backend pass 2m4s`, `frontend pass 18s` | `gh pr checks 23` | — |

### 2.2 Comportamiento observable

| Aspecto | Antes | Después | Evidencia del auditor |
|---|---|---|---|
| `GET /api/vivo` | no existía (nube: `404`) | `200 {"vivo":true}` en local, 5 ms | `curl 127.0.0.1:8110/api/vivo`; nube `curl https://quechua-api.onrender.com/api/vivo` → `404` (confirma que no está desplegado) |
| `GET /api/historial?limite=-1` | sin `ge/le` (`historial_controller.py:16` antes) → 500 en PostgreSQL (por código) | `422` | `-1, 0, 501, abc → 422`; `(sin parámetro), 500 → 200` |
| `GET /api/analitica/demanda?top=0` | sin acotar | `422` | `0, 101 → 422`; `(sin parámetro), 100 → 200`; OpenAPI: `limite {minimum 1, maximum 500, default 50}`, `top {minimum 1, maximum 100, default 15}` |
| Interfaz durante el arranque | «Sin conexión con el servicio local» al fallar; nada mientras espera | «Conectando con el servicio…»; a los 4 s aviso `<output>` (rol `status`); «Reintentar conexión» y texto «en la nube» al fallar | Vitest `Arranque.test.jsx` (aprobadas); capturas `despues/03_U_*.png` revisadas |
| Pestaña activa | solo clase CSS | `aria-current="page"` | `App.jsx:38`; prueba «pestañas (M-07)» |
| `pytest` en `requirements.txt` | `pytest==9.2.0` | retirado | `backend/requirements.txt`; `grep -rn pytest backend/src` → sin resultados |

---

## 3. Estado de cada mejora

| Mejora | Hallazgos | Estado | Evidencia principal |
|---|---|---|---|
| M-01 Aviso de arranque en frío (REF-02) | U-01, R-02, U-02 | **Implementada** (local; no desplegada) | `frontend/src/App.jsx:48-72` (`useEsperaLarga`, `AvisoEspera`), `App.jsx:144`, `api.js:8` (`AVISO_ESPERA_MS = 4000`), `EstadoInicial.jsx:17-40`; `Arranque.test.jsx` 3 casos de temporizador + Reintentar |
| M-02 `/api/vivo` sin base | R-02, PLUS-03, S-04 | **Parcialmente implementada** | Ruta: `sistema_controller.py:18-23`; prueba `test_s13_furps.py:47-50` con un contenedor que lanza `AssertionError` ante cualquier acceso. Falta la parte (2): el PR #22 sigue con `cron: "*/10 * * * *"` y `curl …/api/estado` (`gh api …/contents/.github/workflows/keepalive.yml`), y **no tiene comentarios** (`gh pr view 22 --json comments` → `[]`). La recomendación consta en ADR-034 y en el cuerpo del PR #23, no en el PR #22 |
| M-03 Mensajes de la web | U-02 | **Implementada** según su alcance | `api.js:47-51` (mensaje de red remoto/local), `api.js:59-61` (422 con `detail` de texto), `App.jsx:76-81` (pie «en la nube»), `EstadoInicial.jsx:30-35`; 4 pruebas en `Arranque.test.jsx:89-117`. U-02 queda **parcial** (§5) |
| M-04 Parámetros acotados | R-04 | **Implementada** | `historial_controller.py:17`, `prediccion_controller.py:38`; `test_s13_furps.py:53-75` (12 casos); API local, §2.2 |
| M-05 ADR-033/034 y README | S-04, F-03 (parcial) | **Implementada** | `docs/07_DECISIONES.md:398-437` y registro de cambios `:450`; `README.md:62`. `grep REF-0 docs` ya encuentra REF-01/REF-02 (antes, sin resultados). F-03 (PF-01..PF-17) no estaba en el alcance y sigue abierta |
| M-06 `pytest` fuera de producción | S-03 | **Implementada** | `backend/requirements.txt` (−1 línea); `requirements-dev.txt` conserva `pytest>=9.0.3` y `pytest-cov>=5`; `pip-audit` de la CI en verde |
| M-07 `aria-current` | U-04 | **Implementada** (mejora mínima, sin `tablist`, como decidió el plan) | `App.jsx:38`; prueba `Arranque.test.jsx:120-133` |
| M-08 Lint y cobertura en CI | S-01 (parcial) | **Implementada** | `.github/workflows/ci.yml:45` (`--cov=src --cov-fail-under=85`), `ci.yml:62-64` (`npx oxlint`); ejecutados en la CI del PR #23 con éxito |

**Recuento:** 7 implementadas, 1 parcialmente implementada, 0 no implementadas.

### 3.1 Desviaciones de proceso respecto del plan

- **Granularidad de commits.** El plan (§1.2 y §4) prevé un commit por mejora (8). Se hicieron 6 de
  código/documentación: `cc544be` agrupa M-02+M-04 y `c2c06d0` agrupa M-01+M-03+M-07. Un `git revert`
  ya no aísla cada mejora (p. ej. revertir solo M-07). Impacto bajo; se anota.
- **Orden.** Se respetó backend → interfaz → CI → documentación, salvo que M-08 (CI) precede a la
  interfaz. Sin efecto observable: la CI final está en verde.
- **`role="status"`.** El plan lo pedía explícito; se usa `<output>`, cuyo rol implícito es `status`.
  Equivalente para tecnologías de apoyo; la prueba solo comprueba la etiqueta (`aviso.tagName`).

---

## 4. Búsqueda de regresiones, roturas e incompatibilidades

| Comprobación | Resultado |
|---|---|
| Salvaguarda (τ, RN-06, verificador literal ADR-028) | `git diff --stat 1d0b129..HEAD -- backend/src/domain backend/src/application backend/src/adapters/out backend/src/infrastructure render.yaml backend/data` → **vacío**. `config.py:75` sigue en `umbral_abstencion: float = 0.48`. Arnés idéntico byte a byte |
| Compatibilidad de la API | Ninguna ruta cambia de método ni forma. Valores por defecto intactos (50 y 15). El cliente usa `obtenerHistorial()` sin `limite` (`api.js:84`) y `top = 15` por defecto (`api.js:126`): dentro de rango. Newman 39/39 (según evidencia del agente) |
| Pruebas antiguas con texto | `App.test.jsx:179` sigue buscando «servicio local» y pasa, porque en Vitest `VITE_API_URL` no está definido (`API_REMOTA = false`). Sin roturas |
| Cambio del tipo de error en 422 | Un 422 con `detail` de texto pasa de tipo `validacion` a `servicio` (`api.js:59-69`). `grep "\.tipo"` en `frontend/src` (sin pruebas) → ningún consumidor depende de `tipo`. Sin rotura |
| Dependencias | La CI instala `requirements-dev.txt` (incluye `pytest-cov`, necesario para `--cov`). Ningún módulo de `backend/src` importa `pytest` |
| Errores nuevos en la API | `HEAD /api/vivo` → `405 Method Not Allowed` (`allow: GET`). No es regresión (es el mismo comportamiento de `/api/estado`, E-03 de 01), pero un monitor externo que use `HEAD` por defecto fallaría. El *workflow* del PR #22 usa `curl` con GET, compatible |
| Árbol de trabajo | `git status --short` vacío tras build y pruebas (`dist/` y `.coverage` ignorados) |

**Observaciones nuevas de severidad baja (no son regresiones funcionales):**

- **OBS-01 (baja, U).** El aviso de espera también aparece en el escritorio (`API_REMOTA = false`) en
  cualquier consulta que tarde más de 4 s, con el texto «el modelo puede estar cargándose»
  (`App.jsx:65-67`). ADR-033 dice «En local los textos no cambian»: es cierto para los mensajes de
  error, no para este aviso. Con Qwen local (RNF-01 ≤ 8 s) puede mostrarse en consultas normales.
- **OBS-02 (baja, U).** En la web, el aviso dice «se está activando tras un periodo sin uso» para
  cualquier consulta lenta, aunque el servicio esté despierto (p. ej. Gemini lento). Con P95 de
  ~1 s medido en la U3 (N-02) es infrecuente; texto impreciso, no erróneo en la mayoría de casos.

---

## 5. Hallazgos de 01 tras la fase 1

| ID | Sev. | Antes | Después | Comentario |
|---|---|---|---|---|
| R-01 | Crítica | Abierto | **Abierto** | Fase 2 (A01). `Historial.jsx:15` intacto |
| PLUS-01 | Crítica | Abierto | **Abierto** | Fase 2 (A01) |
| R-02 | Alta | Abierto | **Abierto (mitigación preparada)** | `/api/vivo` existe pero nada lo llama; el PR #22 no está fusionado ni ajustado. Sin medición «después» del arranque en frío |
| U-01 | Alta | Abierto | **Resuelto (local)** | M-01; pendiente de despliegue |
| U-03 | Alta | Abierto | **Abierto** | Fase 2 |
| P-01 | Alta | Abierto | **Abierto** | Fase 2 (A04) |
| R-03, P-02, PLUS-02 | Media | Abiertos | **Abiertos** | Fase 2 |
| R-04 | Media | Abierto | **Resuelto (local)** | M-04 |
| R-05, F-01, F-02 | Media | Abiertos | **Abiertos** | Acción de personas |
| U-02 | Media | Abierto | **Parcial** | Resuelto en `api.js`, `EstadoInicial.jsx` y pie. Sigue: `Historial.jsx:15` («de este equipo») y `Historial.jsx:37`, que muestra «se almacenan solo en este equipo» en la web mientras `/api/estado` no responde (`enLaNube` depende de `estado`, `App.jsx:237`). Visible en la captura `despues/03_U_aviso_arranque_frio_local.png` |
| PLUS-03 | Media | Abierto | **Parcial** | Mitigación documentada (ADR-034), no aplicada |
| S-01 | Media | Abierto | **Parcial** | Umbral de cobertura y oxlint en la CI; las omisiones por corpus/PostgreSQL y `main.py` sin cobertura unitaria siguen |
| F-03 | Baja | Abierto | **Abierto** | PF-01..PF-17 no registradas |
| U-04 | Baja | Abierto | **Resuelto en lo esencial** | `aria-current`; sin `tablist` por decisión del plan |
| U-05, P-03, S-02, PLUS-04 | Baja | Abiertos | **Abiertos** | Fuera del alcance de la fase 1 |
| S-03 | Baja | Abierto | **Resuelto** | M-06 |
| S-04 | Baja | Abierto | **Resuelto** | M-05 |

---

## 6. Puntajes FURPS+ antes / después

Mismo criterio que 01: se parte del puntaje de 01 y se reintegra lo descontado por cada hallazgo
resuelto (crítica 1,5 · alta 1 · media 0,5 · baja 0,25; la mitad si queda parcial); los hallazgos
derivados a la fase 2 o a personas siguen descontando. Las observaciones nuevas OBS-01/02 descuentan
como bajas.

| Categoría | Antes | Después | Δ | Justificación |
|---|---:|---:|---:|---|
| **F** | 8,0 | **8,0** | 0 | F-01, F-02, F-03 abiertos; ninguna mejora de la fase los aborda |
| **U** | 6,5 | **7,75** | +1,25 | U-01 resuelto (+1), U-02 parcial (+0,25), U-04 resuelto (+0,25), OBS-01/02 (−0,25). U-03 sigue |
| **R** | 6,0 | **6,75** | +0,75 | R-04 resuelto (+0,5), R-02 solo preparado (+0,25). R-01 crítico, R-03, R-05 siguen |
| **P** | 6,5 | **6,5** | 0 | P-01, P-02, P-03 abiertos (fase 2) |
| **S** | 8,5 | **9,25** | +0,75 | S-03 (+0,25), S-04 (+0,25), S-01 parcial (+0,25). S-02 sigue |
| **+** | 6,0 | **6,25** | +0,25 | PLUS-03 parcial. PLUS-01 crítico, PLUS-02, PLUS-04 siguen |
| **Global** (media simple) | **6,9** | **7,4** | +0,5 | 44,5 / 6 = 7,42 |

El puntaje «después» describe la rama; **en la nube sigue vigente el 6,9** hasta que se fusione el
PR #23 y Render despliegue.

---

## 7. Capturas

| Captura | Respalda | Revisada |
|---|---|---|
| `despues/03_U_conectando_sin_aviso_aun_local.png` | M-01 (antes de 4 s) | Existe |
| `despues/03_U_aviso_arranque_frio_local.png` | M-01 / U-01 | Sí: aviso «en la nube … hasta un minuto», «Conectando…» en estado y pie. Muestra también el residuo de U-02 en el historial |
| `despues/03_U_aviso_desaparece_al_responder_local.png` | M-01 | Existe |
| `despues/03_U_sin_conexion_mensaje_web_reintentar_local.png` | M-03 / U-02 | Sí: «Sin conexión con el servicio en la nube…», botón «Reintentar conexión», pie «en la nube» |
| `despues/03_R_vivo_y_parametros_422_local.png` | M-02, M-04 / R-04 | Sí: `{"vivo":true}`, dos 422 (puerto 8098); coincide con `rutas_fase1.txt` y con la reejecución del auditor |
| `despues/03_pruebas_antes_despues_fase1.png` | Baterías | Existe; las cifras coinciden con `resumen_pruebas_fase1.txt` |
| `antes/01_R_arranque_frio_72s_nube.png`, `antes/01_F_*` | Línea base R-02 / F | Existen |

Las capturas de la interfaz son locales con un proxy que retrasa `/api/estado`
(`herramientas/proxy_lento.mjs`), no del arranque real en Render. **Faltan capturas «después»** para:
R-02 (alta: medición de arranque en frío con el ping activo — imposible sin despliegue y sin el PR
#22 ajustado), y para los críticos R-01/PLUS-01 y los altos U-03/P-01, que corresponden a la fase 2.
La carpeta `nube/salidas/` está vacía: no hay verificación en la nube posterior a la fusión (todavía
no procede).

---

## 8. Riesgos residuales

| ID | Riesgo | P | I | Exp. | Estado |
|---|---|---:|---:|---:|---|
| RA-01 | Borrado anónimo de todo el historial (R-01) | 3 | 5 | 15 | Sin cambio (fase 2) |
| RA-02 | Alteración pública del corpus y fuentes (PLUS-01) | 3 | 5 | 15 | Sin cambio (fase 2) |
| RA-03 | Abandono durante el arranque en frío | 4→3 | 3→2 | 12→6 | Reducido **solo tras desplegar** (el aviso explica la espera, no la acorta) |
| RE-04 | Se fusiona el PR #22 tal cual: ping a `/api/estado` 24/7 despierta Neon (~90 CU-h de 100 según ADR-034) y consume 720–744 h de Render | 2→3 | 3 | 9 | **Aumentado**: la recomendación no está en el PR #22, que sigue abierto sin comentarios |
| RA-04, RA-05 | Historial compartido; agotamiento de cuota/memoria | 3 | 3 | 9 | Sin cambio (fase 2) |
| RA-08 | Error 500 con parámetros anómalos | 2→1 | 2→1 | 4→1 | Mitigado (en la rama) |
| RR-01 | Reversión no aislada por mejora (commits agrupados) | 2 | 1 | 2 | Nuevo, bajo |
| RR-02 | Aviso de espera en escritorio y texto impreciso en la web (OBS-01/02) | 3 | 1 | 3 | Nuevo, bajo |

---

## 9. Conclusión de cumplimiento

**Cumplimiento del plan: alto (7 de 8 implementadas, 1 parcial, 0 no implementadas), sin
regresiones.** Todas las afirmaciones del agente principal que este auditor pudo reproducir
(pytest, Vitest, oxlint, build, arnés, `/api/vivo` y 422, CI) se confirmaron; E2E y Newman se aceptan
solo como evidencia documental, sin reproducción. La salvaguarda queda intacta y demostrada por el
arnés idéntico.

La fase 1 **no cierra** los hallazgos críticos ni la mayoría de los altos, como el propio plan
declaraba; la puntuación sube de 6,9 a 7,4 en la rama. Para dar por cerrada la fase se recomienda:
(1) dejar la recomendación de ADR-034 en el PR #22 (ruta `/api/vivo` y franja horaria) antes de que
alguien lo fusione; (2) tras fusionar el PR #23, verificar en la nube `GET /api/vivo` → 200 y medir de
nuevo el arranque en frío con captura en `nube/`; (3) opcionalmente, condicionar el texto del
historial (`Historial.jsx:15,37`) a `API_REMOTA` además de a `estado`, y limitar el aviso de espera a
la versión web o ajustar ADR-033.
