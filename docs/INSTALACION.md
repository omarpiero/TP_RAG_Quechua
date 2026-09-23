# Guía de instalación del entorno

Documento correspondiente a la Parte 1 de la consigna. Describe la instalación completa
del entorno de desarrollo y la puesta en marcha del Producto Mínimo Viable.

El sistema tiene cuatro componentes —back-end, base de datos, servicio de inteligencia
artificial y front-end— y los cuatro han de estar disponibles. La sección siguiente reúne
los comandos en el orden en que hay que ejecutarlos; las secciones numeradas explican qué
hace cada uno y por qué, y añaden la verificación del entorno.

## Vía breve: el ejecutable

Para quien solo quiera **usar** el sistema y no trabajar sobre él. No sustituye a la
instalación del entorno que el resto del documento describe, que es la que el proyecto
emplea y la que hay que seguir para desarrollar o para evaluarlo.

```powershell
# 1. Ollama y el modelo generador. Son 3,4 GB: es lo unico que hay que instalar aparte.
winget install Ollama.Ollama
# Cerrar y volver a abrir la terminal para que el comando quede disponible.
ollama pull qwen3.5:4b

# 2. Ejecutar QuechuaWankaWeb.exe
```

El ejecutable lleva dentro el intérprete de Python, las dependencias, el corpus y la
interfaz ya compilada; abre el navegador solo y avisa si no encuentra Ollama. Emplea
**SQLite** en un archivo junto a él en lugar de PostgreSQL, que es lo que permite
prescindir de instalar un servidor de base de datos. La sustitución del motor no requirió
adaptador nuevo alguno —los modelos y el adaptador de persistencia son los mismos— sino
un parámetro de configuración, conforme al desacoplamiento comprometido en RNF-07.

Para construirlo desde el código:

```powershell
cd frontend && npm run build          # con VITE_API_URL vacio, para rutas relativas
xcopy /E /I /Y dist ..\backend\interfaz
cd ..\backend
.venv\Scripts\python.exe -m PyInstaller QuechuaWankaWeb.spec --noconfirm
```

## Instalación rápida

Comandos para Windows. En Linux o macOS cambian `\` por `/`, `copy` por `cp` y
`.venv\Scripts\activate` por `source .venv/bin/activate`.

### Una sola vez

```powershell
# 1. Requisitos. Python 3.12, Node.js 24 y Git se instalan desde sus propias páginas.
winget install Ollama.Ollama
winget install PostgreSQL.PostgreSQL.17

# 2. Código
git clone https://github.com/DalgomXD-byte/asistente-quechua-wanka.git
cd asistente-quechua-wanka

# 3. Base de datos. Pide la contraseña que se definió al instalar PostgreSQL.
psql -U postgres -c "CREATE DATABASE quechua_wanka;"

# 4. Modelo generador. Son 3,4 GB: conviene lanzarlo y seguir con el paso 5 mientras baja.
ollama pull qwen3.5:4b

# 5. Back-end
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env

# 6. Front-end
cd ..\frontend
npm install
copy .env.example .env
```

Antes de arrancar hay que **abrir `backend\.env` y escribir la contraseña de PostgreSQL**
en `POSTGRES_PASSWORD`. Ese archivo no se versiona, de modo que cada instalación pone la
suya. Sin él el sistema arranca igual, pero sin historial ni registro de fuentes.

### Cada vez que se usa

Dos terminales, cada una en su carpeta:

```powershell
# Terminal 1 — back-end
cd backend
.venv\Scripts\activate
uvicorn main:app --port 8000

# Terminal 2 — front-end
cd frontend
npm run dev
```

La aplicación queda en **http://localhost:5173**.

PostgreSQL y Ollama arrancan solos con el sistema, de modo que no hay que hacer nada con
ellos. El back-end tarda cerca de un minuto en cargar el modelo en memoria de vídeo: acepta
consultas desde el primer momento, pero la primera responde despacio hasta que termina.

### Si algo falla

| Síntoma | Causa | Solución |
|---|---|---|
| Toda consulta se abstiene | Ollama no está corriendo o falta el modelo | `ollama list` debe mostrar `qwen3.5:4b` |
| No hay historial ni fuentes | `POSTGRES_PASSWORD` vacío o incorrecto en `backend\.env` | Corregirlo y reiniciar el back-end |
| La interfaz no muestra nada | El back-end no está levantado | Abrir `http://127.0.0.1:8000/docs` para comprobarlo |
| `psql` no se reconoce | PostgreSQL no está en el PATH | Usar la ruta completa o reiniciar la sesión |

## Requisitos previos

| Componente | Versión verificada | Comprobación |
|---|---|---|
| Python | 3.12.10 | `python --version` |
| Node.js | 24.18.1 | `node --version` |
| npm | 11.16.0 | `npm --version` |
| Git | 2.49.0 | `git --version` |
| PostgreSQL | 17.11 | `psql --version` |
| Ollama | 0.34.2 | `ollama --version` |

En Windows, Ollama y PostgreSQL se instalan con winget:

```powershell
winget install Ollama.Ollama
winget install PostgreSQL.PostgreSQL.17
```

## 1. Back-end

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # En Linux o macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env          # En Linux o macOS: cp .env.example .env
```

Editar `.env` y completar `POSTGRES_PASSWORD` con la contraseña del superusuario de
PostgreSQL. El archivo `.env` no se versiona.

Levantar el servicio, una vez creada la base de datos de la sección 2 y descargado el
modelo de la sección 3:

```bash
uvicorn main:app --reload --port 8000
```

La documentación interactiva de la interfaz de programación queda disponible en
`http://127.0.0.1:8000/docs`, generada automáticamente a partir del contrato declarado
en el código.

## 2. Base de datos

El motor ya quedó instalado como servicio de Windows (`postgresql-x64-17`). Crear la base:

```bash
psql -U postgres -c "CREATE DATABASE quechua_wanka;"
```

Las tablas (`fuentes`, `consultas`, `respaldos`) se crean automáticamente al arrancar el
back-end. Si la base de datos no está disponible, el sistema sigue respondiendo consultas
pero sin historial: la recuperación y la salvaguarda de abstención no dependen de ella.

Comprobación de las operaciones CRUD sobre la entidad `fuentes`:

```bash
curl -X POST http://127.0.0.1:8000/api/fuentes -H "Content-Type: application/json" -d "{\"titulo\":\"Diccionario Huanca\",\"entidad_publicadora\":\"MINEDU\",\"licenciamiento\":\"Uso educativo\",\"fecha_extraccion\":\"2026-09-14\",\"nombre_archivo\":\"diccionario.pdf\",\"paginas_totales\":60,\"paginas_con_texto\":60}"
curl http://127.0.0.1:8000/api/fuentes
```

## 3. Integración con el servicio de inteligencia artificial

El modelo generador se ejecuta en Ollama, que expone una interfaz de programación HTTP en
`http://localhost:11434`. Descargar el modelo:

```bash
ollama pull qwen3.5:4b
```

El servicio es externo al proceso de la aplicación, pero interno al equipo: ninguna
consulta ni fragmento del corpus sale del dispositivo, conforme a los requisitos RF-12 y
RNF-06 y al compromiso de soberanía sobre los datos declarado en el proyecto. La dirección
y el modelo se configuran en `.env` mediante `OLLAMA_URL` y `OLLAMA_MODELO`.

**Precarga del modelo.** El back-end lanza una petición de calentamiento en un hilo aparte
al arrancar, de modo que el modelo queda cargado en memoria de video antes de la primera
consulta real y el servicio acepta peticiones mientras tanto. Sin esa precarga la primera
respuesta tardaría unos 47 segundos, por encima del límite de 8 segundos fijado por RNF-01;
con ella se resuelve en 3,5 segundos. La carga completa tarda cerca de un minuto desde que
se levanta el servicio: conviene arrancar el back-end con antelación antes de una
demostración.

## 4. Front-end

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

La interfaz queda disponible en `http://localhost:5173` y consume la interfaz de
programación del back-end. La dirección del servicio se configura con `VITE_API_URL`.

## 5. Verificación de los endpoints con Postman

> Las secciones 5 y 6 no forman parte de la instalación: comprueban que el entorno
> instalado se comporta como debe. Quien solo necesite poner el sistema en marcha puede
> saltar a la sección 8.

La colección `docs/Asistente_Quechua_Wanka.postman_collection.json` cubre los quince
endpoints del sistema, organizados en cuatro carpetas, y cada petición incorpora
comprobaciones automáticas.

Para usarla: abrir Postman, pulsar **Import**, seleccionar el archivo y ejecutar la
colección completa con el **Collection Runner**. El orden importa, porque la creación de una
fuente guarda su identificador en una variable que emplean las peticiones siguientes. La
variable `base_url` viene fijada a `http://127.0.0.1:8000`.

Las comprobaciones no se limitan a verificar códigos de estado: validan las reglas del
sistema. Entre otras, que ninguna respuesta afirmativa se emite sin documento y página
(RNF-08), que una consulta fuera de cobertura no devuelve ningún fragmento (HU-06), y que
una fuente sin licenciamiento declarado se rechaza con 422 (RNF-11).

La petición de incorporación de documentos requiere seleccionar un archivo PDF a mano en la
pestaña *Body* antes de enviarla, porque Postman no almacena el contenido de los archivos
dentro de la colección.

También puede ejecutarse desde la línea de órdenes, sin abrir Postman:

```bash
npx newman run docs/Asistente_Quechua_Wanka.postman_collection.json
```

## 6. Verificación del entorno

```bash
cd backend
.venv\Scripts\python.exe -m pytest tests/ -v
```

La batería comprueba los criterios comprometidos en la prueba de concepto: recuperación
del fragmento pertinente, ausencia total de falsos positivos sobre el subconjunto fuera de
cobertura y conservación de las consultas atendibles.

Para reproducir la calibración completa del umbral:

```bash
.venv\Scripts\python.exe scripts/calibrar_umbral.py
```

## 7. Incorporación de documentos al corpus

Desde la pestaña **Incorporar documentos** de la aplicación, o por la interfaz de
programación:

```bash
curl -X POST http://127.0.0.1:8000/api/corpus/documentos \
  -F "archivo=@documento.pdf" \
  -F "titulo=Titulo del documento" \
  -F "entidad_publicadora=MINEDU" \
  -F "licenciamiento=Acceso publico con finalidad educativa" \
  -F "tipo=lexicografico"
```

El campo `tipo` admite `lexicografico` (diccionarios: se segmenta por entrada) o `prosa`
(relatos y gramática: se segmenta en bloques). La elección no es cosmética: el experimento
E6 de la prueba de concepto midió que segmentar el material lexicográfico por entrada eleva
el recall en el punto de operación del 48,3 % al 85,6 %.

El índice se reconstruye automáticamente tras la ingesta, sin reiniciar el servicio. Para
forzar una reconstrucción: `POST /api/corpus/reindexar`.

## 8. Orden de arranque recomendado

1. Servicio de PostgreSQL (automático al iniciar Windows).
2. Servicio de Ollama (automático tras la instalación).
3. Back-end: `uvicorn main:app --port 8000`.
4. Front-end: `npm run dev`.
