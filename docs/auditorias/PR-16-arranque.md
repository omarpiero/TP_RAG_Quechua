# Auditoría PR #16 · feat/arranque-exe (B14, HU-11)

- **PR / rama:** #16 `feat/arranque-exe` (commits propios `182813a` y `74542b9`; el resto es el apilamiento de #13 a #15)
- **Fecha:** 2026-10-29
- **Puerta de calidad:** SonarQube local en OK tras la corrección de #11; no hay análisis posterior a este PR.
- **Pruebas (última rama de la pila, con `POSTGRES_PRUEBAS_URL`, credencial sin imprimir):** 321 pasan, 0 omitidas; cobertura global 90 %, `domain/` ≈ 94 %; `salvaguarda` 49/49; arquitectura 4/4; Vitest 30/30; **E2E 21/21**; `pip-audit` y `npm audit --omit=dev` limpios. Arnés idéntico byte a byte a la línea base 2980a81; RN-06 = `True`; 0 FP en C. Puertos 8000-8002 y 5173-5175 libres antes y después de mis pruebas.

## Hallazgos

| # | Sev. | Archivo | Regla | Descripción | Corrección sugerida |
|---|---|---|---|---|---|
| 1 | Menor | `capturas/B14_estado_inicial_todo_disponible.png` y `frontend/e2e/estado.real.spec.js` | Evidencia | La captura muestra «Corpus 5 965 fragmentos»: la E2E de estado corre después de HU-02, que incorpora la copia del diccionario, y contradice los 3 605 del resto de capturas y del `.exe`. | Ejecutar la prueba de estado antes de HU-02 (o renombrarla para que corra primero). |
| 2 | Menor | `frontend/src/componentes/EstadoInicial.jsx` | Presentación | Con Ollama sin respuesta, «Modelo qwen3.5:4b» se marca con ⚠ aunque el modelo podría estar descargado; solo se sabe que el servicio no contesta. | Rotular «Modelo: sin comprobar» o comprobarlo por separado. |
| 3 | Menor | `backend/ejecutable.py` (`comprobar_ollama`) | Coherencia | La comprobación de arranque acepta cualquier modelo que empiece por `qwen3.5:4b` (`startswith`), a diferencia del verificador del PR #8, que ya exige el modelo exacto. | Reutilizar la comparación exacta. |
| 4 | Menor | `docs/evidencias/cierre_u3/b14_exe/registro.md` | Procedencia | El `.exe` no es reproducible desde Git (está en `backend/dist`, fuera del repositorio); no hay una huella que ligue ese binario a un commit. | Registrar el SHA-256 y el commit con el que se compiló. |

Sin bloqueantes ni mayores.

## Verificación por foco

1. **Sección «Estado del sistema».** `EstadoInicial.jsx` (en la vista Consultar, sin cambiar las pestañas) lee `/api/estado` y muestra Ollama, modelo, corpus y base con ✔/⚠ y texto (no solo color: `aria-hidden` en el símbolo y texto «responde/no responde»), y `<output>` con el aviso cuando falta Ollama; sin conexión con el servicio muestra un mensaje propio. Vitest cubre las variantes (4 pruebas nuevas) y la E2E `estado.real.spec.js` pasa; el axe del PR #15 también pasa con la sección presente.
2. **Modo sin Ollama.** Prueba de backend `test_arranque_sin_ollama.py` (marcada `salvaguarda`): con `ollama_url` hacia un puerto muerto el estado informa `generador_disponible: false`, la consulta devuelve 200, `abstenida: false`, el fragmento literal `ZORRO: Atuq.` con documento y página 37 y `aviso_generacion`. La E2E C-10 (con la captura B14 de aviso) también pasa. **Comprobado con el `.exe` real** (abajo).
3. **`dist` solo con el `.exe`.** `backend/dist` contiene únicamente `QuechuaWankaWeb.exe` (109 152 471 bytes, igual al registro: 104,1 MiB); ni `datos/` ni archivos `.db`.
4. **Arranque del `.exe` (ejecutado por mí).** Copié el `.exe` a una carpeta temporal fuera del repositorio (sin `.env` ni base) y lo lancé con `QW_SIN_NAVEGADOR=1`; la base real no se tocó (hash idéntico antes y después) y la carpeta temporal se eliminó.
   - **Con Ollama disponible:** arranque en frío hasta `GET /api/estado` = 200 en 26,6 s (el registro dice 43,6 s; depende de la máquina); `generador_disponible: true`, base conectada, 3 605 fragmentos, modelo `qwen3.5:4b`; consulta en inglés → 200, `abstenida: false`, diccionario página 37, sin aviso; la SPA responde 200 con CSP `style-src 'self'` y `/docs` 200. Junto al `.exe` solo aparecieron `datos/` y `quechua_wanka.db` (con sus archivos `-wal` y `-shm`).
   - **Sin Ollama** (`OLLAMA_URL=http://127.0.0.1:9`): arranque en 19,2 s; `generador_disponible: false`, base conectada, 3 605 fragmentos; consulta 200, no abstenida, documento y página 37, `aviso_generacion` presente, texto igual al fragmento literal. Coincide con `arranque_sin_ollama.json`.
   - Cierre del proceso: terminé solo el árbol del `.exe` que lancé; el puerto 8000 quedó libre.

## Estado de reglas
RN-01…RN-10 y RS-01…RS-08: cumplen (RS-01: el `.exe` escucha solo en 127.0.0.1; sin telemetría ni red saliente salvo la comprobación local de Ollama). Sin cambios en la salvaguarda.

## Veredicto: **apto** para revisión humana (0 bloqueantes · 0 mayores · 4 menores).
