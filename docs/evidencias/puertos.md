# Puertos, adaptadores y cableado (PR-02 · HT-00)

Generado a mano a partir de `backend/src` el 2026-10-01 (rama `feat/cierre-pmv1-video`). El árbol de
archivos está en [`arbol_src.txt`](arbol_src.txt). El cableado vive en
`backend/src/infrastructure/contenedor.py` (composition root).

Nota técnica: `in` es palabra reservada de Python, por lo que los paquetes `application/ports/in/` y
`adapters/in/` no pueden aparecer en una sentencia `import`. Los puertos de entrada se reexportan desde
`application/ports/__init__.py` (`from application.ports import ConsultarCorpusPort`) y el paquete
`adapters.in.rest` se carga por cadena (`importlib`) en `infrastructure/main.py`.

## Puertos de entrada (`application/ports/in/`)

| Puerto IN | Implementación (caso de uso) | Adaptadores de entrada que lo usan | Cableado en el contenedor |
|---|---|---|---|
| `ConsultarCorpusPort` | `ConsultarCorpusUseCase` | REST `consultas_controller` (`POST /api/consultas`) · CLI `consultar` | `Contenedor.consultar_corpus` |
| `IngestarDocumentoPort` | `IngestarDocumentoUseCase` | REST `corpus_controller` (`POST /api/corpus/documentos`) | `Contenedor.ingestar_documento` |
| `ReindexarCorpusPort` | `ReindexarCorpusUseCase` | REST `corpus_controller` (`GET /api/corpus/documentos`, `POST /api/corpus/reindexar`) · CLI `indexar` | `Contenedor.reindexar_corpus` |
| `ConsultarHistorialPort` | `ConsultarHistorialUseCase` | REST `historial_controller` (`GET /api/historial`) | `Contenedor.consultar_historial` (solo con base de datos; si no, 503) |
| `GestionarFuentesPort` | `GestionarFuentesUseCase` | REST `fuentes_controller` (`/api/fuentes…`) | `Contenedor.gestionar_fuentes` (solo con base de datos; si no, 503) |

`sistema_controller` (`GET /api/estado`) no tiene puerto propio: lee `Contenedor.estado()` a través de
`adapters/in/rest/dependencias.py`.

## Puertos de salida (`application/ports/out/`)

| Puerto OUT | Adaptador (implementación) | Lo usan (casos de uso) | Cableado en el contenedor |
|---|---|---|---|
| `IndiceRecuperacionPort` | `adapters/out/recuperacion/IndiceHibridoLexico` | Consultar, Ingestar, Reindexar | `Contenedor.indice` |
| `GeneradorTextoPort` | `adapters/out/generacion/OllamaGenerador` · alternativa sin modelo `GeneradorLiteral` (CLI) | Consultar | `Contenedor.generador` (`generador="ollama"\|"literal"\|"auto"`) |
| `TraductorPort` | `adapters/out/traduccion/TraductorTabla` (principal) · `OllamaTraductor` (alternativa, no cableada) | Consultar | `Contenedor.traductor` |
| `DetectorIdiomaPort` | `adapters/out/idioma/DetectorIdiomaHeuristico` | Consultar | `Contenedor.detector` |
| `RepositorioConsultasPort` | `adapters/out/persistencia/RepositorioConsultasPostgres` (SQLAlchemy; PostgreSQL o SQLite) | Consultar (registro), Historial | `Contenedor.repositorio_consultas` (opcional) |
| `RepositorioFuentesPort` | `adapters/out/persistencia/RepositorioFuentesPostgres` | Gestionar fuentes, Ingestar | `Contenedor.repositorio_fuentes` (opcional) |
| `RepositorioCorpusPort` | `adapters/out/documentos/CorpusJsonl` | Ingestar, Reindexar | `Contenedor.corpus` |
| `ExtraccionDocumentalPort` | `adapters/out/documentos/ExtractorPdf` | Ingestar | `Contenedor.extractor` |

## Servicios de dominio (`domain/services/`, solo biblioteca estándar)

`DepuradorConsulta` · `EvaluadorConfianza` (τ = 0,48, inyectado desde `infrastructure/config.py`) ·
`Segmentador`. `EvaluadorConfianza` se instancia en el contenedor con `configuracion.umbral_abstencion`.

## Flujo de una consulta (visible en el log INFO, prefijo de capa)

`[REST]` controlador → `[PUERTO-IN]` `ConsultarCorpusPort.ejecutar` → `[CASO-USO]` `ConsultarCorpus` →
`[TRADUCTOR]` → `[INDICE]` → `[EVALUADOR]` → `[GENERADOR]` invocado / NO invocado (sin respaldo) →
`[REPOSITORIO]` registrada / omitido. El log nunca incluye el texto del fragmento: solo ids, cifras,
documento y página.
