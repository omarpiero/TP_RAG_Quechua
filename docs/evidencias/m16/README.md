# M16 · KPI del proceso AS-IS (consulta manual)

Protocolo: `docs/13_BRECHAS_RUBRICA.md` §5. Lo **mide el equipo**; el agente solo prepara la muestra y calcula.

## Muestra

- `lista_m16.csv`: 20 consultas de A y 5 de C, tomadas de `backend/data/evaluacion_v2.json` con
  `random.Random(2026).sample` sobre cada partición ordenada por `id` (20 de A, después 5 de C).
- No incluye la forma esperada ni el documento: quien busca no debe verlos.

## Cómo se mide

1. Dos integrantes que **no** hayan trabajado con el corpus (P1 y P2) buscan el término de cada consulta,
   a mano, en los 8 PDF de `corpus/pdf/`. Pueden usar un visor de PDF y Ctrl+F.
2. Anotan en `kpi_asis.csv`, en sus filas, la hora de `inicio` y de `fin` (hh:mm:ss) y los `segundos`.
3. Cuando encuentran la forma quechua, escriben el `documento` y la `pagina` y marcan
   `resultado = correcto` si la entrada corresponde al término. Si corresponde a otra cosa, marcan
   `incorrecto`.
4. Si a los **5 minutos (300 s)** no la encuentran, abandonan y anotan `no_encontrado`.
5. Para las consultas de C (fuera de cobertura), lo correcto es no encontrar nada: se anota
   `no_encontrado`. Si la persona propone una forma, se anota `incorrecto`.
6. Las personas no se comunican entre sí y no usan buscadores web ni el sistema.

`kpi_asis.csv` tiene codificación UTF-8 con BOM para que Excel muestre bien las tildes; guárdalo como CSV UTF-8.

## Qué calcula el agente al recibir la hoja

- El tiempo medio y el mediano por consulta (A y C por separado).
- La tasa de fallo en A: incorrecto + no encontrado.
- El porcentaje de consultas de C en que se «encuentra» algo.
- La comparación con el sistema sobre las mismas 25 consultas: latencia de M5 y respaldo correcto de M4.

## Limitaciones que se declaran

- La muestra es pequeña.
- Las personas son del propio equipo.
- Ctrl+F favorece a la búsqueda manual, porque en la práctica el usuario no sabe en qué PDF buscar.

Por eso el KPI es **conservador**.
