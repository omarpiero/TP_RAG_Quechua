# 17 · Reporte de métricas finales de la Unidad 3

Mediciones del PMV1 y el PMV2, en local y en la nube. Nada se rellenó a mano: lo no medido figura como «por medir».

## 1. Metadatos

| Dato | Valor |
|---|---|
| Fecha | 2026-11-01 (hora de Perú; 2026-11-02 en UTC para la nube) |
| Medición local | `c61f52b` en `docs/evidencias/cierre_u3/99_final_c61f52b/` (`E1`) |
| Medición en la nube | `618714e` en `docs/evidencias/nube/metricas_u3/` |
| Diferencia entre ambos commits | PR #20: refactor de 39 code smells, sin cambio funcional. Sobre él se repitieron pytest, Vitest, arnés, RN-06 y SonarQube |
| E1 | Windows 11 (10.0.26300) · RTX 4060 8 GB, driver 621.01 · Python 3.12.14 · Node 22.16.0 · PostgreSQL 16.15 · Ollama 0.35.0 · `qwen3.5:4b` Q4_K_M |
| Nube | Render plan free · Neon PostgreSQL · `gemini-3.5-flash-lite` · τ 0,48 |
| Corpus local | `fragmentos_v3.jsonl`, SHA-256 `d6200ed9e992e7dc3bfc740ec69195606ffb8f022d044d202d43ce562e47470a` |

**Corpus «reconstruido».** El SHA-256 de `docs/16` coincide con el del v3 original: el corpus reconstruido **es** el v3. Pero Neon ya no es igual: tiene **3 607 fragmentos y 10 documentos**, porque incluye dos PDF de prueba (`documento_control_guia11.pdf` y `prueba_qa_tp1.pdf`). Eso mueve un poco el IDF. Ver N-08.

## 2. Métricas M-01 a M-27

Rutas relativas a `docs/evidencias/cierre_u3/`. Commit `c61f52b` y entorno E1 salvo que se indique otra cosa.

| ID | Métrica | Valor | Unidad | Comando | Evidencia |
|---|---|---|---|---|---|
| M-01 | pytest con PostgreSQL | 371 aprobadas, 0 omitidas, 0 fallidas, 75 s | pruebas | `pytest -q --cov=src` | `99_final_c61f52b/pytest.txt`, `junit.xml` |
| M-02 | Cobertura | total 89,9 · domain 95,2 · application 95,4 · adapters 87,4 · infrastructure 82,8 | % | ídem | `99_final_c61f52b/coverage.json` |
| M-03 | Vitest | 34/34 | pruebas | `npx vitest run` | `99_final_c61f52b/vitest.txt` |
| M-04 | E2E Playwright, incluida PF-18 | 21/21, 1,7 min | pruebas | `npm run test:e2e` | `99_final_c61f52b/e2e.txt` |
| M-05 | Newman local | 15 peticiones, 39/39 | aserciones | `newman run` | `99_final_c61f52b/newman_resumen.json` |
| M-06 | Arnés τ 0,48 | A 120/120 (108 + 12 lema) · B 60/60 (57 + 3) · C 0 FP en 28 · D 40/40 (37 + 3). Sin lema: A+B 165/180 (F1 0,9565). Similitud máxima en C 0,4698. Primer τ sin FP 0,47, no adoptado | consultas | `scripts/arnes_linea_base.py` | `99_final_c61f52b/arnes/` |
| M-07 | Cobertura ML, validación cruzada (n 415) | AUC 0,9961 · F1 0,9635 · P 0,9851 · S 0,9429 · E 0,9704 · VP 264, FP 4, VN 131, FN 16 | — | `entrenar_predictores.py` | `backend/modelos/metricas.json`, `99_final_c61f52b/comparacion_metricas.txt` (reproducido) |
| M-08 | Pasajes ML, validación cruzada (n 167) | AUC 0,9804 · F1 0,8976 · P 0,8507 · S 0,95 · E 0,9065 · VP 57, FP 10, VN 97, FN 3 | — | ídem | ídem |
| M-09 | Puntos de operación | cobertura 0,25 (0 retiradas) · pasajes 0,50 | — | ídem | `backend/modelos/metricas.json` |
| M-10 | No regresión | RN-06 sí · 0 retiradas · 0 FP en C · pasajes en F 49 → 7, en E 50 → 48 | consultas | `evaluar_pmv2.py` | `99_final_c61f52b/pmv2/no_regresion_pmv2.json` |
| M-11 | Predicción por consulta | P50 6,11 · P95 12,66 (caso de uso completo: recuperación, rasgos y 2 modelos) | ms | ver script 06 | `99_final_c61f52b/inferencia_ml.json` |
| M-12 | Qwen en GPU con predictores (30 consultas) | Caliente P50 2 572 · P95 2 767 · máx. 2 793. Primera tras descargar el modelo: 6 224–6 763. Abstención 10–13. VRAM pico del equipo 4 676 MiB (`ollama ps`: modelo 3,1 GB). RAM API 215 MiB | ms | `m5_latencia.py` | `99_final_c61f52b/m5_gpu/`, `m5_frio_real.json`, `vram_gpu.txt`, `ram_pico_api_bytes.txt` |
| M-13 | Qwen en CPU (`num_gpu=0`) | Caliente P50 6 216 · P95 7 836 · máx. 8 201. Carga en frío de CPU: por medir | ms | ídem con modelo `num_gpu 0` | `99_final_c61f52b/m5_cpu/`, `ollama_ps_cpu.txt` |
| M-14 | Data masiva SQLite 800 | 115,2 tps · media 7,81 · P50 5,9 · P95 14,3 · máx. 24,3 ms · 0 FP · 800 filas `carga` | — | `02_carga_sqlite.ps1` | `99_final_c61f52b/data_masiva/sqlite/` |
| M-15 | Data masiva PostgreSQL 1 000 con procedimientos | 104,0 tps · media 8,3 · P50 6,6 · P95 15,2 · máx. 26,5 ms · 0 FP | — | `03_carga_postgres.ps1` | `99_final_c61f52b/data_masiva/postgres/` |
| M-16 | Carga HTTP con Locust (generador literal, commit del B10) | 1 usuario 5 448 sol/min, P50 10, P95 16 · 5 usuarios 8 128, 33/61 · 10 usuarios 8 015, 70/100 · 0 % errores. **No repetido** en `c61f52b` | sol/min, ms | `05_carga_http.ps1` | `b10_carga/` |
| M-17 | radon | CC media 2,55 · 354 A, 33 B, 6 C, ninguno D, E ni F · MI 95/95 en A | — | `radon cc`, `radon mi` | `99_final_c61f52b/radon_*.txt` |
| M-18 | Bandit | 0 altos, 0 medios, 2 bajos (B106 y B107, a revisar como falsos positivos) | — | `bandit -r src` | `99_final_c61f52b/bandit.json` |
| M-19 | Dependencias | `pip-audit` 75 → 0 avisos · `npm audit` 0 | avisos | `pip-audit` | `b1_deps/`, `99_final_c61f52b/pip_audit*.json`, `npm_audit.json` |
| M-20 | SonarQube local | **`c61f52b`: ERROR** por 39 smells nuevos. **`7ed2acd` (fusionado en `618714e`): Passed**. 0 bugs, 0 vulnerabilidades, 0 hotspots · 29 smells · duplicación 0,6 % · cobertura 80,2 % (nueva 87,3 %) · 40 aceptados con justificación | — | `pysonar` | `99_final_c61f52b/sonar.json`, `sonar_tras_fix_7ed2acd.json`, `b9_calidad/excepciones_sonar.md` |
| M-21 | OWASP ZAP, escaneo base pasivo (**reutilizado de B9**, `7389441`, local) | Antes 1 media (CSP) y 1 informativa · después 0 altas, 0 medias, 1 informativa. Sin escaneo activo; no ejecutado contra la nube | alertas | ZAP 2.17 | `b9_calidad/zap_*.json` |
| M-22 | axe-core con datos | 0 infracciones WCAG 2 A/AA en 4 vistas (antes 5) · objetivos < 44 px: 0 (antes 38) | — | E2E | `b13_a11y/` |
| M-23 | Fidelidad con Qwen (120 de A, regla v2) | Libre 13/120 (10,8 %) · extractiva vigente **0/103**, 17 descartadas (14,2 % con fragmento literal) · cortadas 0 · P95 2 681 ms | — | `medir_fidelidad.py` | `b11_fidelidad/despues_v2/`, `registro.md` |
| M-24 | Ejecutable (**no recompilado** en `c61f52b`) | 104,1 MiB · arranque 43,6 s en frío, 2,06 s en caliente · persistencia correcta (3 605 → 5 965 fragmentos tras reabrir) | — | PyInstaller | `b14_exe/` |
| M-25 | Paridad del índice móvil | diferencia máx. 2,533 × 10⁻⁸ · top-5 idéntico · 11,67 MiB | — | `validar_indice_movil.py` | `99_final_c61f52b/paridad/`, `b12_paridad/` |
| M-26 | Ágil | Ver §2.1 | — | `git`, `gh` | `99_final_c61f52b/agil.json` |
| M-27 | HU-09 | Nube: `usuario` 13, `carga` 500, `humo` 264+ → insuficiente. Local demo: `carga` 800 → demostración rotulada | consultas | `/api/analitica/demanda` | `nube/metricas_u3/analitica_real.json`, `b3_origen/` |

### 2.1 Ágil

Commits sin merges en `origin/main`, antes del PR #20:

| Autor en Git | Sprint 1 (21/09–11/10) | Sprint 2 (12/10–05/11) | Total |
|---|---|---|---|
| omarpiero | 14 | 33 | 47 |
| James Saenz Castro | 16 | 3 | 19 |
| jamesSSC | 0 | 4 | 4 |

- PR #1–#19: omarpiero 16, jamesSSC 3, todos fusionados.
- *Lead time* (primer commit → fusión): #1–#2 1,8 h · #3–#16 13,2–13,4 h · #17–#19 0,1–0,2 h. Los #17–#19 miden poco porque los commits nacen justo antes del PR.
- La fusión de #3–#16 fue en bloque, de modo que su *lead time* no mide cada bloque por separado.
- No aparece ningún commit de un tercer integrante. Es un pendiente de personas (rúbrica E2).

## 3. Métricas en la nube N-01 a N-10

Rutas relativas a `docs/evidencias/nube/metricas_u3/`, salvo las indicadas.

| ID | Métrica | Valor | Evidencia |
|---|---|---|---|
| N-01 | Arranque en frío tras 16 min | 72,39 s (`c61f52b`) · 62,37 s (`618714e`). `docs/16` tenía «unos 50 s» sin medir | `arranque_frio*.json` |
| N-02 | Latencia por endpoint (P50/P95 ms, servicio despierto) | `consultas` con Gemini 923/977 y 944/1 048 · abstención 192/207 · pasajes 298/310 · validación 422 125–136/139–178 · historial 136/143 · demanda 162/170 · modelos 126/134 | `humo_2026-11-02_0435.json` |
| N-03 | `/api/predicciones` (248 consultas, cliente) | P50 158,4 · P95 283,0 ms | `paridad_resumen.json` |
| N-04 | Gemini con 5 s de pausa (20 de A) | Servidor P50 765 · P95 859 ms · **429: 2/20** (no desaparecen del todo) · sustituidas 4/20: 2 por cuota, 2 por verificador · contradicción 0/16 | `../gemini_fidelidad_2026-11-02_0437.json` |
| N-05 | Newman contra la nube | 15 peticiones, 39/39 · media 898 ms | `newman_nube_resumen.json` |
| N-06 | CI | Verde en `618714e`, [ejecución 41387235324](https://github.com/omarpiero/TP_RAG_Quechua/actions/runs/41387235324) | GitHub Actions |
| N-07 | Comparación local frente a nube (10 A + 10 C) | Misma decisión 20/20. Nube P50 943 ms (responde) y 179 ms (abstiene) · local con generador literal < 10 ms | `comparacion_local_nube.json` |
| N-08 | Arnés contra la nube (248, `/api/predicciones`) | A 120 (108 + 12) · B 60 (57 + 3) · C 0 FP · D 40 (37 + 3) · **0 decisiones distintas**. Similitud máxima en C 0,4665 (local 0,4698). Diferencia de similitud máx. 0,0035, media 5,8 × 10⁻⁵, causada por los 2 PDF de prueba en Neon | `paridad_decisiones.json`, `paridad_por_consulta.json` |
| N-09 | Memoria | Render free no la muestra en esta medición. Local: API 215 MiB frente a los 512 MB del plan | M-12 |
| N-10 | Carga de 500 (reporte 16, no repetida) | 0 errores · 2,22 tps · P50 484 · P95 624 ms | `../carga_2026-10-29_2210.json` |

La decisión de N-08 se reconstruye con similitud ≥ 0,48 o lema exacto, sin invocar a Gemini.

## 4. Discrepancias frente a las cifras del informe

| ID | Antes | Ahora | Causa |
|---|---|---|---|
| R-01 | 128 (+3) · cobertura 77 % · dominio 93 % · aplicación 90 % | 371 · 89,9 % · 95,2 % · 95,4 % | Pruebas nuevas de los PR #3–#19 |
| R-02 | Vitest 16 | 34 | Ídem |
| R-03 | 39 comprobaciones | 39 | Igual |
| R-04 | Arnés | Igual | Byte a byte frente a `2980a81` |
| R-05, R-06, R-07, R-08 | ML | Igual (matriz de pasajes: VP 57, FP 10, VN 97, FN 3) | Reproducido sin fechas |
| R-09 | P50 2 677 · P95 3 088 · abstención 14 ms | P50 2 572 · P95 2 767 · 10–13 ms | Medición nueva, modo extractivo |
| R-10 | SQLite 52,1 tps, P95 27,7 · PostgreSQL 56,7 tps, P95 27,7 | 115,2 tps, P95 14,3 · 104,0 tps, P95 15,2 | Otra corrida y arreglo de bloqueo. Depende de la carga de la PC |
| R-11 | CC 2,41 · 266/288 en A · 1 en E (32) · MI 84/84 | CC 2,55 · 354/393 en A · ninguno en E · MI 95/95 | Refactor de `_resolver` y código nuevo |
| R-12 | Bandit 1 bajo | 2 bajos | Nuevo B107 en `seguridad.py` |
| R-13 | 5 paquetes con avisos | 0 | PR #3 |
| R-14 | Inferencia 0,26 ms | 6,11 ms | **No comparable**: el informe medía solo los modelos; ahora es el caso de uso completo. **0,26 ms: no reproducida** |
| R-15 | 0 infracciones sin backend | 0 con backend (antes 5) | Medición con datos, PR #15 |
| R-16 | VRAM 3,1 GB | Modelo 3,1 GB · equipo 4 676 MiB | `nvidia-smi` incluye el resto del equipo |
| R-17 | 104 MB | 104,1 MiB | Igual |
| docs/16 | Qwen 0/109, 11/120 | **0/103, 17/120** | Citaba la medición anterior al último endurecimiento |
| docs/16 | «Corpus reconstruido, no v3» | Byte a byte igual al v3; Neon suma 2 PDF de prueba | SHA-256 y `/api/corpus/documentos` |
| docs/16 | Frío «unos 50 s» | 62–72 s | Medido |
| Consultas en Neon | `usuario` 10 | 13 | 3 no proceden de esta medición, que va marcada como `humo` |

## 5. Estado de cada historia

Propuesta; decide el equipo. Capturas en `docs/evidencias/cierre_u3/capturas/`.

| Historia | Local | Nube | Estado propuesto |
|---|---|---|---|
| HU-01 | CRUD; `HU-01_*.png` | Newman y humo | QA: licencias «por registrar» |
| HU-02 | Persistencia en `.exe`; `HU-02_*.png` | Pendiente de confirmar por la interfaz (U8 de `docs/16`) | QA |
| HU-03 | Arnés A y B | C-01 | Done |
| HU-04 | Pasajes; `HU-04_*.png` | Pasajes | QA: sin conjunto de referencia cultural |
| HU-05 | D 40/40 (techo) | C-03 | Done, con D declarado techo |
| HU-06 | 0 FP, salvaguarda | 0 FP en N-08 | Done |
| HU-07 | Documento y página | Cita en respuestas | Done |
| HU-08.1 | M-07 | N-03 | Done |
| HU-08.2 | M-10, RN-06 | N-08 | Done |
| HU-08.3 | M-25 | No aplica | QA: sin validar en dispositivo físico |
| HU-09 | Demostración rotulada | Insuficiente: 13 < 100 | QA: faltan consultas reales |
| RF-15 | M-08 | Ensayo de 4 consultas | Done |

## 6. Plan de pruebas PF-01 a PF-18

El repositorio solo define **PF-18** (E2E consulta → documento y página → historial → borrar: **aprobada**, M-04). Las definiciones de PF-01 a PF-17 están en el informe, fuera de este repositorio: **por registrar** al cruzarlas con las evidencias de §2 y §3.

**Pendiente de la sesión anterior:** retoques menores de capturas, como duplicados RF-15 y `HU-09_demostracion_priorizacion.png`, que no muestra el rótulo (usar `HU-09_demostracion_pagina_completa.png`).

**Otros pendientes técnicos:** ZAP contra la nube · reindexado o limpieza de los 2 PDF de prueba en Neon (no se tocó, por regla) · `humo_nube.py` y `docs/16` citan una pregunta de `evaluacion_prosa.json`, y `docs/11` tiene otra.

## 7. Guion del video

`docs/video/GUION_VIDEO_NUBE.md`, con la lista de pestañas. Capturas para el informe, fuera de Git: `entregables/capturas_informe/`.

## 8. Lo que queda para personas

- Acta del experto y sus 7 propuestas.
- Grabación.
- Tablero.
- NRC y % de participación.
- Enlace del cuaderno de Colab.
- Regenerar `TOKEN_PRUEBAS` y borrar la variable de usuario.
- Commits de los integrantes que faltan.
