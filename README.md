# Asistente de consulta del quechua wanka

Producto Mínimo Viable de un asistente conversacional con generación aumentada por
recuperación sobre el corpus documental publicado del quechua wanka de Junín.

Toda respuesta cita el documento y la página que la sustentan, y el sistema declara
explícitamente la ausencia de información en lugar de proponer una forma no documentada.

## Arquitectura

Arquitectura hexagonal (puertos y adaptadores). La correspondencia con la estructura
exigida por la consigna es directa; los nombres siguen la convención de Python:

```
backend/
├── domain/                     -> /domain
│   ├── entities/               -> entities
│   ├── value_objects/          -> valueObjects
│   └── ports/                  -> ports (interfaces)
├── application/                -> /application
│   ├── use_cases/              -> useCases
│   └── services/               -> services
└── infrastructure/             -> /infrastructure
    └── adapters/               -> adapters
        ├── input/              -> input (controllers)
        └── output/             -> output (DB, APIs)
```

El núcleo de dominio no conoce ninguna tecnología concreta: solo los puertos. Sustituir
PostgreSQL por SQLite, u Ollama por un motor de inferencia embebido, afecta únicamente al
adaptador correspondiente y se resuelve en `infrastructure/contenedor.py`.

| Puerto | Adaptador actual | Adaptador previsto en el incremento móvil |
|---|---|---|
| `IndiceRecuperacionPort` | Índice híbrido léxico en memoria | El mismo, con índice preconstruido |
| `GeneradorTextoPort` | Ollama por HTTP (Qwen3.5-4B) | llama.cpp embebido (Qwen3.5-0.8B) |
| `RepositorioFuentesPort` | PostgreSQL | SQLite |
| `RepositorioConsultasPort` | PostgreSQL | SQLite |
| `DetectorIdiomaPort` | Heurístico por palabras funcionales | El mismo |

## Historias de usuario implementadas

| Historia | Descripción | Endpoint |
|---|---|---|
| HU-01 | Registro de fuentes con procedencia y licenciamiento | `/api/fuentes` (CRUD) |
| HU-03 | Consulta léxica español/inglés | `POST /api/consultas` |
| HU-06 | Salvaguarda antialucinación | Integrada en la consulta |
| HU-07 | Trazabilidad documental | Campo `respaldo` de la respuesta |
| RF-11 | Historial de sesión | `GET /api/historial` |

## Resultados medidos

Medidos sobre el corpus real (3605 fragmentos) y el conjunto de evaluación de 248
consultas. Reproducibles con `scripts/calibrar_umbral.py`.

| Métrica | Valor |
|---|---|
| recall@5 (español, subconjuntos A y B) | 1.000 |
| recall@5 (inglés, subconjunto D) | 0.950 con traducción previa · 0.175 sin ella |
| Consultas en inglés atendidas | 90 % con traducción previa · 2,5 % sin ella |
| MRR@10 | 0.992 |
| Latencia de recuperación | 1.7 ms (media) |
| Umbral de abstención calibrado | 0.48 |
| Falsos positivos fuera de cobertura | 0 de 28 |
| Consultas atendibles conservadas | 100 % |
| Latencia de respuesta completa | 3.5 s, incluida la primera consulta |
| Ejecución del modelo | 100 % en GPU (3.1 GB de los 8 GB disponibles) |

Tres desviaciones respecto de la prueba de concepto, todas documentadas en el código:

1. **Umbral 0.48 en lugar de 0.41.** El Documento 6 no fija la fórmula exacta de las
   estrategias E2 y E3; aquí ambas se calculan como coseno sobre TF-IDF. El punto de
   operación se recalibró conforme al procedimiento que el propio documento establece, y
   el resultado mejora al publicado: 100 % de recall conservado frente al 85,6 %.
2. **Capa determinista de coincidencia de lema.** Un término muy frecuente en el corpus
   recibe un IDF bajo, de modo que su propia entrada de diccionario puede quedar por
   debajo del umbral (caso medido: «perro», 0,271). Cuando el término consultado coincide
   exactamente con el lema de una entrada lexicográfica se considera respaldo documental
   sin pasar por el umbral. No puede producir falsos positivos, porque solo se activa si la
   entrada existe literalmente en el corpus.

3. **Se traduce el término depurado, no la pregunta completa.** El experimento E7 preveía
   traducir la consulta antes de recuperar, y la prueba de concepto dejó el requisito RF-04
   pendiente de recalibrar el umbral porque la mitad de las consultas traducidas seguía
   quedando por debajo de la frontera. Medido aquí, la causa es que traducir la pregunta
   entera devuelve también su fraseo en español («cómo se dice X en quechua de Wanka»), que
   reintroduce las palabras que la depuración existe para eliminar. Traduciendo únicamente
   el término ya depurado, las consultas atendidas en inglés pasan del 40 % al 90 % **sin
   modificar el umbral**, de modo que la recalibración prevista en la condición C-4 no
   resulta necesaria.

## Puesta en marcha

Ver [docs/INSTALACION.md](docs/INSTALACION.md).

## Alcance declarado

Herramienta de consulta sobre fuentes ya publicadas y validadas. No sustituye la validación
por hablantes de la comunidad ni se constituye en autoridad lingüística sobre la variedad
wanka. Ninguna forma quechua mostrada por el sistema es redactada por el modelo: todas
proceden literalmente de los documentos indexados y se citan con su fuente.

Pendiente para el siguiente incremento: las consultas formuladas en inglés se resuelven por
debajo del criterio comprometido (recall@5 de 0,175) mientras no se incorpore la traducción
previa de la consulta y se recalibre el umbral. El fallo se produce en la dirección segura:
el sistema se abstiene en lugar de responder sin respaldo.
