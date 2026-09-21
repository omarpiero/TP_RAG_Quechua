# Guía de instalación del entorno

Documento correspondiente a la Parte 1 de la consigna. Describe la instalación completa
del entorno de desarrollo y la puesta en marcha del Producto Mínimo Viable.

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

Levantar el servicio:

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

**Advertencia sobre la primera consulta.** La carga inicial del modelo en memoria de video
tarda aproximadamente 47 segundos. Las consultas siguientes se resuelven en unos 3,3
segundos, dentro del límite de 8 segundos fijado por RNF-01. Conviene lanzar una consulta
de calentamiento antes de cualquier demostración o medición.

## 4. Front-end

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

La interfaz queda disponible en `http://localhost:5173` y consume la interfaz de
programación del back-end. La dirección del servicio se configura con `VITE_API_URL`.

## 5. Verificación del entorno

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

## 6. Orden de arranque recomendado

1. Servicio de PostgreSQL (automático al iniciar Windows).
2. Servicio de Ollama (automático tras la instalación).
3. Back-end: `uvicorn main:app --port 8000`.
4. Front-end: `npm run dev`.
