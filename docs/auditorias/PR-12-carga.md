# Auditoría PR #12 · test/carga-http (B10)

- **PR / rama:** #12 `test/carga-http` (commit propio `d2a7d28`; incluye, por apilamiento, el índice atómico de `119078f` de #10)
- **Fecha:** 2026-10-29
- **Puerta de calidad:** ver `PR-11-calidad.md` (ERROR por 44 smells nuevos, sin seguridad ni fiabilidad); no hay un análisis posterior.
- **Cobertura:** global 89 %, `domain/` ≈ 94 % (sin cambios en `domain/`).
- **Pruebas (con `POSTGRES_PRUEBAS_URL`, `quechua_wanka_pruebas`, credencial sin imprimir):** 262 pasan, 0 omitidas; `salvaguarda` 28/28; arquitectura 4/4; Vitest 21/21; `pip-audit` y `npm audit --omit=dev` limpios. Ruff limpio en los archivos del PR.

## Hallazgos

| # | Sev. | Archivo:línea | Regla | Descripción | Corrección sugerida |
|---|---|---|---|---|---|
| 1 | Mayor | `application/use_cases/consultar_corpus.py` (`_registrar`, ~l. 424) | Pérdida silenciosa del historial | Un fallo al registrar se traga (`except Exception`) y solo deja `[REPOSITORIO] no se pudo registrar la consulta: OperationalError`. Se registra en el log, pero sin `consulta_id`, sin texto y sin la causa: no se puede saber qué consulta se perdió ni distinguir «database is locked» de un error de programación o del rechazo RNF-08 del procedimiento de PostgreSQL, y no hay traza (`exc_info`). No hay contador visible en `/api/estado`. | `log.warning("... id=%s: %s", consulta.id, str(exc).splitlines()[0], exc_info=True)` y, mejor, un contador de registros perdidos en `/api/estado`. |
| 2 | Menor | `infrastructure/contenedor.py` (`_wal`) | WAL / durabilidad | Con `synchronous=NORMAL` en WAL, un corte de energía puede perder las últimas transacciones confirmadas (no corrompe). El modo WAL es persistente y crea `*.db-wal` y `*.db-shm`: copiar solo el `.db` (como hace `frontend/playwright.config.js`) puede dejar fuera escrituras recientes. | Aceptable para el historial; documentarlo y copiar los tres archivos (o `PRAGMA wal_checkpoint`) al hacer copias. |
| 3 | Menor | `scripts/carga/locustfile.py` | Dependencias | `locust` no figura en `requirements-dev.txt`; el script y `05_carga_http.ps1` lo exigen. | Declararlo en `requirements-dev.txt`. |
| 4 | Menor | `docs/evidencias/cierre_u3/b10_carga/analitica_tras_la_carga.json` | Evidencia | Tras la corrida hay 21 771 filas `carga` frente a 21 591 respuestas 200 de Locust (+180). Un exceso no indica pérdida, pero el informe no lo explica. | Anotar la causa (p. ej. peticiones en vuelo al detener Locust) o contarlas. |

Sin bloqueantes.

## Verificación por foco

1. **`database is locked`: WAL, espera y registro que no tumba la respuesta.**
   - Correcto en lo esencial: `timeout=30` en la conexión, `PRAGMA journal_mode=WAL` y `synchronous=NORMAL` al conectar (probado: el motor devuelve `wal`); la respuesta sigue citando documento y página aunque falle el historial (prueba `salvaguarda` nueva).
   - **¿Puede perder registros en silencio?** Puede perderlos (solo si el bloqueo supera 30 s o falla la escritura), pero no sin rastro: deja un aviso en el log. Ese aviso es insuficiente (hallazgo 1).
   - Comprobación propia: 20 hilos concurrentes durante 20 s sobre una base temporal con el generador literal y origen `carga`: **2 891 respuestas 200 = 2 891 filas guardadas, 0 avisos de registro, 0 «locked»**. La evidencia de Locust (1, 5 y 10 usuarios, 0 % de errores) es coherente; la corrida previa a la corrección (0,1 % y 0,9 % de HTTP 500) se conserva en `antes_de_la_correccion/`.
   - `05_carga_http.ps1` aísla la corrida (base, carpeta de datos y origen por variables de entorno; puerto 8003; detiene la API y borra la carpeta temporal).
2. **`NotFittedError`: publicación atómica del índice (commit `119078f`).** El estado se agrupa en una `NamedTuple` (`_Estado`) que se asigna de una vez; `recuperar`, `recuperar_prosa` y `puntuar` capturan `e = self._estado` una sola vez e `indexar` construye vectorizadores nuevos sin tocar los del índice en uso. El diseño es correcto: los lectores ven el índice anterior completo o el nuevo completo. La prueba `test_indice_concurrente.py` lanza 4 hilos de consulta mientras se reindexa 25 veces, comprueba que ningún resultado carezca de documento y página y que no haya excepciones (marcada `salvaguarda`); pasa. Los scripts que leen `_fragmentos` y `_matriz_*` por separado son de un solo hilo. El arnés no se altera (idéntico byte a byte a la línea base, comprobado en #11 y de nuevo en esta rama).
3. **Generador `literal` por configuración.** `GENERADOR` es `Literal["ollama","literal","auto"]` (valida el valor); `literal` devuelve el fragmento citado sin invocar al modelo y no relaja ninguna regla de salvaguarda.

## Riesgo de pruebas contra la base real (`backend/quechua_wanka.db`, ruta SQLite por defecto)

**Ninguna prueba unitaria abre la base real.** Los archivos que construyen un `Contenedor` (`tests/unit/infrastructure/test_origen_en_contenedor.py:14-26`, `test_persistencia_datos.py:36-46`, `test_seleccion_repositorio.py:25-36`) sustituyen `modulo.configuracion` con `ruta_sqlite=tmp_path/"q.db"` antes de cada `Contenedor(...)` (líneas 32, 39, 59, 69, 50, 42, 63 y 96); los `TestClient` usan contenedores falsos o `FastAPI()` propios. Tras ejecutar la suite completa en un worktree limpio no apareció ningún `quechua_wanka.db`. La protección depende de que cada prueba nueva repita ese `monkeypatch`: no hay red de seguridad (por ejemplo, un `conftest.py` con fixture `autouse`).

Lo que sí puede escribir en la base real si se ejecuta sin aislar:

| Archivo:línea | Qué hace | Riesgo |
|---|---|---|
| `backend/scripts/generar_transacciones.py:98` | `Contenedor(generador="literal", origen=CARGA)` con la configuración por defecto: escribe 800 filas `carga` en `quechua_wanka.db` (o en la base PostgreSQL real si `.env` trae `BASE_DATOS=postgres`) | Alto si se invoca directamente: el aislamiento lo hacen solo `scripts/demo/02` y `03`; el docstring (l. 19) solo lo «recomienda». |
| `scripts/demo/04_metricas.ps1:101-117` | Solo arranca una API temporal si el puerto 8000 no responde; si ya hay una (por ejemplo, la de uso real), Newman envía sus 15 solicitudes contra ella | Medio: añade consultas `usuario` a la base real. |
| `backend/scripts/humo_bloque7.py:18` | `BASE = "http://127.0.0.1:8000/api"`: consulta lo que esté en el 8000 | Medio: depende de `ORIGEN_CONSULTAS=humo`, que solo está en el docstring. |
| `backend/src/adapters/in/cli/__main__.py:37` | `Contenedor(...)` con la configuración por defecto | Bajo: es la CLI del producto y se espera que use la base real. |
| `backend/src/infrastructure/config.py:48` | Valor por defecto `CARPETA_EJECUTABLE / "quechua_wanka.db"` | Origen de lo anterior. |

El archivo `backend/quechua_wanka.db` del repositorio principal cambió durante la sesión de auditoría (05:14:38; mantiene sus 65 consultas pero ahora tiene la columna `origen`), lo que indica que alguna aplicación se arrancó contra él; no fue ninguna prueba analizada aquí. **Sugerencias:** un `conftest.py` con fixture `autouse` que fije `RUTA_SQLITE` y `CARPETA_DATOS` a `tmp_path`; que `generar_transacciones.py` exija un `RUTA_SQLITE` distinto del valor por defecto (o rechace la base real); y que `04_metricas.ps1` aborte si el 8000 ya responde.

## Estado de reglas
RN-01…RN-10 y RS-01…RS-08: cumplen. RN-02 se mantiene aunque falle el historial. Sin cambios en τ ni en `domain/`.

## Veredicto: **apto** para revisión humana, con el mayor 1 (registrar el fallo con identificador y causa) a corregir en este PR. 0 bloqueantes · 1 mayor · 3 menores.


## Re-auditoría de #12 (commits 4e06779 y 20d684e, 2026-10-29)

- **Hallazgo 1 (mayor): cerrado.** El aviso de registro fallido es ahora `[REPOSITORIO] no se pudo registrar consulta_id=<id>: <TipoDeExcepción>` con **traza** (`exc_info=True`) y **sin el texto de la consulta**; el motor SQLAlchemy se crea con `hide_parameters=True` para que los mensajes de error tampoco filtren los valores. Prueba nueva: el aviso lleva `consulta_id=`, la excepción y la traza («database is locked»), y no contiene el texto. Sigue sin haber un contador visible en `/api/estado` (sugerencia, no exigencia).
- **Red de seguridad para la base real: cerrada.**
  - `backend/conftest.py` (raíz de pruebas) define una fixture `autouse` que fija `RUTA_SQLITE` a `tmp_path` y parchea cada copia del singleton `configuracion` ya importada; la prueba nueva `test_base_segura.py` lo verifica. La suite completa (296 pruebas) no creó ni modificó ningún archivo de base real: el hash de `quechua_wanka.db` del repositorio principal permaneció igual.
  - `generar_transacciones.py` llama a `_base_segura.fijar_base_por_defecto()` (usa `carga.db` si nadie fija `RUTA_SQLITE`) y a `verificar(configuracion)` antes de escribir. **Comprobado:** con `RUTA_SQLITE` apuntando a la base real → `ABORTADO: … es la base real` y el hash no cambia; sin variable → escribe en `carga.db`; con `BASE_DATOS=postgres` y `POSTGRES_DB=quechua_wanka` → `ABORTADO: la base PostgreSQL resuelta es la real`.
  - `humo_bloque7.py` arranca su propia API en el puerto 8004 con una base temporal y origen `humo`; `--url` exige `--confirmo-base-aparte`.
  - `04_metricas.ps1` ya no corre Newman contra una API ajena: si el puerto 8000 responde o está ocupado, registra el fallo y no lanza Newman; solo usa una API que él mismo arranca con una base temporal.
- Menores que quedan: la lista de bases reales de `_base_segura.verificar` es fija (`quechua_wanka` y `quechua_wanka.db`); una base real con otro nombre no se detectaría. Los menores 2 a 4 de este informe (WAL/durabilidad, `locust` sin declarar, +180 filas sin explicar) siguen abiertos.

**Veredicto de la re-auditoría: apto** (0 bloqueantes · 0 mayores · 3 menores).
