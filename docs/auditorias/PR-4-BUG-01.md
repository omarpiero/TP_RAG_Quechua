# Auditoría PR #4 · BUG-01 (datos escribibles)

- **PR / rama:** #4 `fix/BUG-01-datos-escribibles` (apilado sobre #3; diff `chore/deps-seguridad..fix/BUG-01-datos-escribibles`, 20 archivos)
- **Fecha:** 2026-10-29
- **Puerta de calidad (SonarQube):** no verificada. El MCP `sonarqube-local` / `sonarqube` no está disponible para este auditor; análisis local con `ruff` en lugar de Sonar.
- **Pruebas:** `pytest -m "not lento"` 156 passed, 3 skipped. `-m salvaguarda` 18 passed. Arquitectura (7 passed). PostgreSQL: `POSTGRES_PRUEBAS_URL` no definida, **omitidas**.
- **Cobertura:** global 86 % (mín. 70 %), `domain/` 94 % (mín. 90 %).
- **ruff** sobre archivos tocados: limpio (22 avisos en el resto del repo, preexistentes). **pip-audit:** sin vulnerabilidades conocidas. `npm audit`: no aplica (no se toca `frontend/`).
- Sin PDF, `.env`, `.jsonl`, `.db` ni pesos en el diff. `.gitignore` añade `backend/data/documentos/` y `backend/datos/`.

## Hallazgos

| # | Sev. | Archivo:línea | Regla | Descripción | Corrección sugerida |
|---|---|---|---|---|---|
| 1 | Mayor | `adapters/out/documentos/almacen_documentos_disco.py` (`guardar`) | RS-04 / robustez | **Traversal contenido**: `../../x.pdf`, `..\..\x.pdf` y `/abs/x.pdf` quedan como `x.pdf` dentro de la carpeta (comprobado con prueba propia). Pero el adaptador no valida la extensión ni nombres reservados: `manifiesto.json` se guarda como PDF y se autorreferencia en el manifiesto (el filtro de `.pdf` solo existe en el controlador REST); `a.pdf:s` crea un flujo alterno NTFS y `CON.pdf` es nombre reservado de Windows; `..` lanza `PermissionError` sin mensaje controlado. Por REST solo es alcanzable el caso de flujo alterno (`x.pdf:s.pdf`). | Rechazar en el adaptador: sufijo distinto de `.pdf`, `MANIFIESTO`, caracteres `:*?"<>|`, nombres reservados y `.`/`..`; lanzar un error de dominio mapeado a 422. |
| 2 | Mayor | mismo, `guardar` | Integridad | **Sobrescritura silenciosa**: si existe en disco un archivo con ese nombre que no figura en el manifiesto (huérfano, p. ej. copiado a mano), `write_bytes` lo pisa sin aviso (comprobado: `ORIGINAL` → `nuevo`). La desambiguación con `-sha8` solo mira el manifiesto. | Comprobar `(carpeta/limpio).exists()` y usar `open(..., "xb")` o el sufijo `-sha8`. Escribir el manifiesto de forma atómica. |
| 3 | Mayor | mismo + `corpus_controller.py:14,37` | RS-02 (entrada acotada) | **Tamaño máximo solo en el controlador** (60 MB, tras `await archivo.read()` completo en memoria). El adaptador no tiene tope (comprobado con 70 MB). El 413 es posterior a leer todo el cuerpo. | Aceptable para uso local, pero mover el límite al caso de uso/puerto o leer por bloques; registrar la decisión. |
| 4 | Menor | `ingestar_documento.py` (llamada a `guardar`) | Consistencia | `Fuente.nombre_archivo` usa el nombre bruto, mientras el almacén puede devolver otro (limpio, `-sha8` o duplicado con otro nombre). `VerificarConsistenciaDatos` emitirá avisos espurios en esos casos. Usar `guardado.nombre` en la fuente. |
| 5 | Menor | `infrastructure/datos.py:14` | Mantenimiento | La copia de datos nunca se actualiza: si un paquete nuevo trae un corpus base distinto, el usuario conserva el antiguo sin aviso. Documentar o comparar huella. |
| 6 | Menor | `contenedor.py` `_verificar_consistencia` | Calidad | `except Exception` amplio con `noqa: BLE001`; aceptable porque solo informa. |
| 7 | Menor | `QuechuaWankaWeb.spec` | Empaquetado | `datas` incluye `('interfaz','interfaz')`, carpeta no versionada (se genera con `npm run build`); el spec falla en un clon limpio sin ese paso. Preexistente, documentar. |

Ningún hallazgo bloqueante.

## Puntos pedidos

1. **AlmacenDocumentosDisco**: traversal por separadores contenido (`Path(...).name`); sin ejecución de rutas externas. Fallos 1-3 arriba. Dedupe por SHA-256 correcto. Sin lectura de `.env`.
2. **No pisa el corpus base**: en empaquetado la copia va a `datos/` junto al `.exe` y el base vive en `_MEIPASS` (solo lectura); en desarrollo `ruta_corpus == ruta_corpus_base` y `preparar_carpeta_datos` sale antes de copiar (comprobado por `resolve()`); nunca sobrescribe una copia existente. Cubierto por `test_rutas_datos.py`/`test_persistencia_datos.py`. OK.
3. **`/api/estado`**: solo expone `consistencia.estado` y `avisos` con nombres de archivo/fuente; ninguna ruta absoluta (rutas solo en el registro del servidor). OK. Nota: los nombres de archivo subidos por el usuario sí aparecen en los avisos (dato local, aceptable).
4. **Salvaguarda**: `domain/` y servicios de abstención intactos (0 cambios); τ no aparece como literal nuevo (sigue en `config.py`, 0,48); arnés `arnes_linea_base.py` a τ = 0,48: FP = 0 en la partición C (28 VN), recall 0,9167 sin regla de lema, igual que la línea base; el generador no se invoca sin respaldo. RN-06: sin cambios en predictores. OK.
5. **Arquitectura**: puerto `AlmacenDocumentosPort` en `application/ports/out`; `application/` no importa adaptadores; `domain/` sin terceros; pruebas de arquitectura en verde. OK.
6. **`.spec`**: añade los hiddenimports del PMV2 (`prediccion_controller`, `predecir_consulta_port`, `analizar_demanda_port`); correcto y coherente con el hallazgo del `.exe` documentado. Los nuevos módulos (`almacen_documentos_disco`, `infrastructure.datos`) se importan estáticamente, no requieren entrada. OK.
7. **SonarQube**: MCP no disponible; no se pudo consultar la puerta de calidad.

## RN-01…RN-10 y RS-01…RS-08

RN-01…RN-10: sin cambios en el flujo de respuesta; cumplen (arnés y pruebas de salvaguarda verdes). RS-01, RS-03, RS-05, RS-06, RS-07: sin cambios, cumplen. RS-02/RS-04 (validación de entradas y nombres): cumplen parcialmente, ver hallazgos 1-3. RS-08: no aplica.

## Veredicto: **APTO** para revisión humana (0 bloqueantes, 3 mayores, 4 menores). Los mayores 1-3 deberían resolverse en este PR o aceptarse por escrito como excepción (uso local, un solo usuario).

## Re-auditoría 3273c4b (2026-10-29)

Commit «endurecer el almacén de PDF tras la auditoría». Se repitieron las pruebas propias en un worktree temporal.

| Hallazgo | Resultado |
|---|---|
| M1 (nombres) | **Cerrado.** El adaptador rechaza con `ErrorAlmacenDocumentos` (mapeado a 4xx): `manifiesto.json` en cualquier capitalización, extensiones distintas de `.pdf`, `a.pdf:s`, `a.pdf::$DATA`, `CON/con/NUL.x/LPT1.pdf`, `..`, `../..`, `a/../b.pdf`, vacío, `.pdf` sin nombre, punto o espacio final y caracteres de control. `/abs/z.pdf` se reduce a `z.pdf` dentro de la carpeta. |
| M2 (huérfanos) | **Cerrado.** Un huérfano `h.pdf` con otro contenido no se pisa: el nuevo se guarda como `h-<sha8>.pdf` y el original queda intacto. Si el nombre con sufijo también existe, se rechaza sin sobrescribir (probado). Un huérfano idéntico se adopta en el manifiesto con aviso. |
| M3 (tope) | **Cerrado.** El adaptador rechaza más de 60 MB (probado con 60 MB + 1 byte) y acepta 60 MB exactos; el controlador lee por bloques de 1 MB y responde 413 en cuanto supera el tope (prueba `test_ingesta_tope.py`). |
| Menor 4 (`Fuente.nombre_archivo`) | **Cerrado.** `ingestar_documento` sustituye el nombre del documento, de la fuente y de los fragmentos por el devuelto por el almacén. |

Observación (sin impacto): el manifiesto se sigue escribiendo con `write_text` no atómico (sugerencia secundaria del M2); se deja como deuda menor.

**Verificación:** 191 pruebas pasan (3 omitidas por PostgreSQL), cobertura global 87 %; `salvaguarda` 18/18; arquitectura 6/6; pip-audit sin vulnerabilidades. El commit no toca `domain/`, τ ni la recuperación.

**Veredicto de la re-auditoría: apto** (0 bloqueantes, 0 mayores; menores 5-7 y la escritura no atómica siguen como deuda).
