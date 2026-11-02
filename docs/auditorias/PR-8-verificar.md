# Auditoría PR #8 · chore/verificar-entorno-demo (B7)

- **PR / rama:** #8 `chore/verificar-entorno-demo` (diff `78382ad..a6ca42e`)
- **Fecha:** 2026-10-29
- **Puerta de calidad:** SonarQube local sin análisis real; pendiente en B9.
- **Pruebas (última rama de la pila, con `POSTGRES_PRUEBAS_URL`):** 232 pasan, 0 omitidas; cobertura global 89 %, `domain/` ≈ 94 %; `salvaguarda` 18/18; pruebas del verificador 20/20 (con arquitectura). Ruff limpio en los archivos nuevos. pip-audit sin vulnerabilidades.

## Hallazgos

| # | Sev. | Archivo:línea | Regla | Descripción | Corrección sugerida |
|---|---|---|---|---|---|
| 1 | Mayor | `backend/scripts/verificar_entorno_demo.py` · `comprobar_ollama` | Falso ✔ | Acepta cualquier etiqueta `qwen3.5:*` como si fuera `qwen3.5:4b` (`n.startswith("qwen3.5:")`). Comprobado con un doble: solo `qwen3.5:0.8b` instalado → ✔ «responde», cuando la aplicación pide `qwen3.5:4b` y la generación fallaría. Un modelo ajeno (`llama3:8b`) sí se rechaza. | Comparar el nombre exacto (`n == modelo`, o `n == modelo + ":latest"` si procede). |
| 2 | Menor | `comprobar_archivo` | Falso ✔ | Solo comprueba `is_file()`: un `cobertura.joblib` o `fragmentos_v3.jsonl` vacío o corrupto da ✔ (comprobado con 0 bytes y con texto basura). | Exigir tamaño > 0 y, para los modelos, cargarlos con `joblib.load`. |
| 3 | Menor | `docs/evidencias/cierre_u3/b7_verificar/salida_con_postgres.txt` | Evidencia | La salida está recortada a mano (`14 comprobaciones en N s`, 3 líneas); no es salida literal. | Adjuntar la salida íntegra. |

Sin bloqueantes.

## Verificación por foco

- **¿Detecta fallos críticos de verdad?** Ejecuté el verificador en un worktree sin `carga.db` ni interfaz compilada: marca ✖ en ambos y termina con código 1 (comprobado fuera de `tail`). La evidencia `salida_fallo_simulado_app_caida.txt` muestra ✖ por API caída con código 1 y la interfaz como aviso ⚠ (no crítico, coherente). Con Ollama detenido, Python < 3.12, dependencias o datos ausentes y puertos ocupados, las funciones devuelven ✖ (pruebas del PR 20/20 y doble propio). Los avisos no cambian el código de salida; los críticos sí. Falsos ✔: hallazgos 1 y 2.
- **Credenciales en la salida.** PostgreSQL: la contraseña solo se usa para construir la URL; el mensaje de fallo imprime el tipo de excepción (probado con una excepción que contenía `password=…`: no aparece) y el de éxito, versión, host y puerto. Búsqueda de password/token/secret en `b7_verificar/`: nada. No lee `.env` por su cuenta (lo hace pydantic).
- **Efectos.** Solo lectura, salvo el precalentamiento de Ollama (opcional con `--sin-precalentar`). No toca la base real.

## Estado de reglas
RN-01…RN-10 y RS-01…RS-08: sin cambios; cumplen. Sin cambios en `domain/` ni salvaguarda.

## Veredicto: **apto** para revisión humana, con el mayor 1 a corregir en este PR (cambio de una línea). 0 bloqueantes · 1 mayor · 2 menores.

## Re-auditoría de la corrección 957c073 (2026-10-29)

`fix(demo): el verificador exige el modelo exacto y modelos que cargan`.

- **Hallazgo 1 (mayor): cerrado.** Con un doble de Ollama: solo `qwen3.5:0.8b` da ✖; `qwen3.5:4b-q8_0` da ✖; `qwen3.5:4b` da ✔; un modelo sin etiqueta acepta `:latest`. El modelo se lee de `c.ollama_modelo` (la configuración), no de una constante.
- **Hallazgo 2 (menor): cerrado.** `comprobar_modelo` exige archivo, tamaño de al menos 256 bytes y que `joblib.load` lo cargue: un archivo vacío o de 1 000 bytes de basura da ✖; los dos modelos reales dan ✔ («se carga bien»). Nota: `joblib.load` deserializa con pickle; es aceptable porque solo carga los modelos versionados del propio repositorio. Los archivos de datos siguen comprobándose solo por existencia.
- Hallazgo 3 (salida con PostgreSQL recortada a mano): sigue abierto como menor.

**Veredicto: apto** (0 bloqueantes · 0 mayores · 1 menor).
