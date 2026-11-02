# Guion del video sobre la nube (semana 12)

> Todo se graba sobre **<https://quechua-web.onrender.com>**. Los valores vienen del ensayo del 2026-11-01 contra
> la nube (commit `618714e`): `docs/evidencias/nube/metricas_u3/ensayo_predicciones.json`. Las formas quechuas que
> aparezcan en pantalla las devuelve el sistema; no se escriben ni se corrigen en este guion.

## Antes de grabar

| Paso | Qué hacer | Tiempo |
|---|---|---|
| 1 | Abrir <https://quechua-api.onrender.com/api/estado> **2 minutos antes**. El arranque en frío medido fue de 62 s y 72 s | 2 min |
| 2 | Comprobar en `/api/estado`: `umbral_abstencion` 0.48, `generador` gemini, `motor_base_datos` postgres | 10 s |
| 3 | Dejar abiertas las pestañas de abajo | 2 min |
| 4 | Si Gemini responde con cuota agotada, esperar 1 minuto. El sistema muestra el fragmento literal, que también es válido | 1 min |

**Pestañas abiertas:**

1. <https://quechua-web.onrender.com>
2. <https://quechua-api.onrender.com/docs>
3. <https://quechua-api.onrender.com/api/estado>
4. Neon › SQL Editor
5. GitHub › repositorio, en `backend/src`
6. GitHub › Actions
7. Render › Dashboard
8. [Tablero Trello oficial](https://trello.com/b/U7rnhvA0/proyecto-25-slm-para-preservacion-digital-del-quechua-de-junin)
9. `docs/17_REPORTE_METRICAS_U3.md`
10. SonarQube local (`localhost:9000`)

## Episodio 0 · Carátula

Nombres y roles, proyecto, enlace al repositorio y URL pública.

## Episodio 1 · Pruebas funcionales del PMV1

| Paso (pestaña Consultar) | Qué debe verse (ensayo) |
|---|---|
| `¿cómo se dice zorro en quechua wanka?` | Responde. Similitud **0,6071** ≥ τ 0,48, vía similitud, «Redactado por: gemini», diccionario Wanka, **pág. 37**, unos 0,7–1 s |
| `how do you say fox in Wanka Quechua?` | Lectura de la tabla «zorro», misma entrada, pág. 37 |
| `¿cómo se dice criptomoneda en quechua wanka?` | **Abstención**. Similitud 0,0502, sin forma quechua y sin invocar a Gemini |
| `¿Cuántas vocales tiene el sistema fonológico?` | Abstención con **3 pasajes** rotulados «no es una respuesta» |
| Consulta vacía y una de 301 caracteres | Validación. La API responde 422 |
| Pestaña Fuentes del corpus | CRUD de fuentes |
| Historial | Las consultas de la sesión |

**Qué decir:** la forma sale literal del fragmento, con documento y página; sin respaldo el modelo no se ejecuta.

**Qué no decir:**
- Que el sistema valida la lengua: consulta fuentes publicadas.
- Que Gemini traduce: solo redacta a partir del fragmento, y el verificador lo comprueba.

## Episodio 2 · Pruebas funcionales del PMV2

En la pestaña Predicción ML: los dos modelos con su AUC (0,996 y 0,980), matrices de confusión y curvas ROC. Después, una consulta en «Probar los modelos».

**Qué decir:** los modelos solo pueden añadir abstenciones (RN-06). En la no regresión, las respuestas del PMV2 son un subconjunto de las del PMV1 y ningún predictor retiró respuestas.

**Qué no decir:** que el umbral es adaptativo. τ = 0,48 es fijo.

## Episodio 3 · Data masiva

1. Mostrar los resultados de `docs/evidencias/nube/carga_2026-10-29_2210.json`: 500 consultas contra la API pública, 0 errores, P50 484 ms, P95 624 ms.
2. En Neon › SQL Editor:

   ```sql
   SELECT origen, count(*) FROM consultas GROUP BY origen;
   SELECT * FROM fn_conteo_por_origen();
   SELECT * FROM fn_resumen_demanda();
   ```

   Al 2026-11-01: `carga` 500, `humo` 264, `usuario` 13. El número de `humo` y `usuario` puede haber subido.
3. En la app, Predicción ML › Analítica de demanda: «Historial insuficiente» con las consultas reales. Después, marcar «Ver demostración».

**Qué no decir:** nunca presentar la analítica sintética como demanda real. Son 13 consultas reales y el mínimo es 100. El propio rótulo de la app lo indica.

## Episodio 4 · Métricas

| Mostrar | Valor |
|---|---|
| GitHub Actions | CI en verde, `618714e` |
| Newman contra la nube | 15 peticiones, 39/39 aserciones |
| Pruebas locales | 371 pytest, 34 Vitest, 21 E2E; cobertura 89,9 % |
| SonarQube | Puerta **Passed**; 0 bugs, 0 vulnerabilidades, 0 hotspots |
| ZAP | 0 altas, 0 medias (escaneo base local, no contra la nube) |
| Arnés | A 120/120, B 60/60, D 40/40, 0 falsos positivos en C |
| Latencia | Nube: ~0,9 s con Gemini y ~0,2 s en abstención. Local: Qwen en GPU, P95 2,8 s |

**Qué decir:** A y B derivan del propio diccionario y D es un techo por construcción.

**Qué no decir:** que las pruebas de ZAP o SonarQube se ejecutaron contra Render: son locales.

## Episodio 5 · Predicciones ML desde la app pública

En Predicción ML › «Probar los modelos»:

| Consulta | P(cobertura) | P(pasajes) | Lectura |
|---|---|---|---|
| Cubierta: `¿cómo se dice zorro en quechua wanka?` | 99,94 % | — | Responde |
| Fuera de cobertura: `¿cómo se dice criptomoneda en quechua wanka?` | 0,00 % | 0,00 % | Se abstiene |
| Prosa cubierta: `¿Cuántas vocales tiene el sistema fonológico?` | 31,68 % | 52,98 % (corte 50 %) | Ofrece pasajes, sin afirmar |
| Prosa no cubierta: `¿Cuál es el procedimiento para renovar un pasaporte?` | 1,68 % | 3,25 % | Sin pasajes |

## Episodio 6 · Tablero Trello

Tablero oficial: columnas, tarjetas por historia y evidencia. Lo gestiona otro asistente; revisa el estado antes de grabar.

## Episodio 7 · Arquitectura hexagonal en GitHub

Ruta:

1. `backend/src/domain` (solo biblioteca estándar) y `backend/tests/architecture/test_arquitectura.py`.
2. `application/ports/in` y `ports/out`.
3. `adapters/out`: `generacion` (Ollama y Gemini), `persistencia` (SQLite y PostgreSQL), corpus (`CorpusJsonl` y `RepositorioCorpusPostgres`).
4. `infrastructure/contenedor.py`: elige los adaptadores por variables de entorno.
5. `render.yaml` y `.github/workflows/ci.yml`.
6. `backend/db/postgres/procedimientos.sql` y las funciones en Neon.
7. Los PR de cada integrante.

**Qué decir:** cambiar de Qwen local a Gemini, o de SQLite a Neon, no toca el dominio ni los casos de uso.

## Plan B

| Si pasa | Hacer |
|---|---|
| Render dormido | Abrir `/api/estado` y esperar hasta 2 minutos |
| Gemini sin cuota | El fragmento literal con el motivo visible también demuestra la salvaguarda; decirlo |
| Neon lento en el primer acceso | Repetir la consulta |
| Captura de datos personales | Cerrar sesión de marcadores, correo y paneles con secretos. **Nunca mostrar las variables de entorno de Render** |
