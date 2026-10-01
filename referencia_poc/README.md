# referencia_poc/

Material de la prueba de concepto (Documento 6) que el PMV1 **promueve a código de producción**.
Es de **solo lectura**: se estudia, se reescribe en `src/` con pruebas y no se importa desde el código.

| Ruta | Qué es | Qué se hace con ello |
|---|---|---|
| `scripts/ingest2.py` | Ingesta con recomposición de la capa OCR y segmentación por tipo (una entrada por fragmento en material lexicográfico) | Base del adaptador de `ExtraccionDocumentalPort` y de la segmentación (HU-01, HU-02) |
| `scripts/ingest.py` | Ingesta con segmentación uniforme de 650 caracteres | Solo para reproducir la ablación; **no** es la configuración adoptada |
| `scripts/build_eval.py`, `scripts/add_D.py` | Construcción automática del conjunto de evaluación a partir del diccionario | Referencia del procedimiento; el conjunto ya está en `datos/` |
| `scripts/experimento.py` | Estrategias E1–E4, métricas por partición y barrido del umbral | Base del arnés de evaluación (HT-01) |
| `scripts/experimento_v1.py` | El mismo experimento sobre la ingesta uniforme | Solo referencia |
| `scripts/demo.py` | Prototipo mínimo: responde con procedencia o se abstiene | Base del caso de uso «consultar» |
| `datos/evaluacion_v2.json` | 248 consultas: A 120 · B 60 · D 40 · C 28, con identificadores de fragmentos de referencia (`oro`) | Se promueve a `evaluacion/conjuntos/` |
| `datos/fragmentos_v2.jsonl` | 3 605 fragmentos indexados en la PoC | Referencia para comprobar que la nueva ingesta reproduce los mismos identificadores. **Fuera de Git** (es el texto del corpus) |
| `resultados/resultados_v2_depurada.json` | Resultados de la configuración de la PoC (τ 0,41, recall@5 1,000 en A y B) | Referencia histórica; la línea base del PMV1 es τ 0,48 (ADR-020) y la congela el PR 0 |
| `resultados/resultados_v2_cruda.json`, `resultados_v1_depurada.json` | Sin depuración de la consulta · con segmentación uniforme | Evidencia de ADR-007 y de la depuración |
| `resultados/resultados_colab.json` | Primera ejecución densa (E5-small) en Colab | Evidencia de ADR-005 |
| `resultados/resultados_cuaderno_e5small.json`, `resultados_cuaderno_e5base.json` | Cuaderno integral con E5-small y con E5-base, incluida la traducción EN→ES | Evidencia de ADR-008 y ADR-012 |
| `resultados/resumen_corpus.json`, `ocr_estimacion.json` | Inventario del corpus y estimación de la ganancia del OCR (0,45 %) | Referencia |
| `PoC_quechua_wanka_recuperacion_densa.ipynb` | Cuaderno de Colab del experimento E5 | Referencia |
| `PoC_quechua_wanka_pruebas_completas.ipynb` | Cuaderno integral de los siete experimentos | Referencia y material de sustentación |

## Diferencias con el contrato de datos del PMV1

- `fragmentos_v2.jsonl` **no** tiene el campo `procedencia`, que el contrato hace obligatorio
  (`docs/02_REQUERIMIENTOS.md`, RD-01). La nueva ingesta debe añadirlo.
- El identificador es `md5("<archivo>|<página>|<índice>")[:12]`. Se conserva para que `evaluacion_v2.json`
  siga siendo válido (ADR-018). La nueva ingesta debe reproducir los mismos identificadores sobre el mismo
  corpus: es una prueba de regresión de HU-02.
- Los scripts leen rutas relativas de la carpeta donde se ejecutaron; no están pensados para ejecutarse
  desde aquí sin adaptar.
