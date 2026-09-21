import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.adapters.input.api import router
from infrastructure.config import configuracion
from infrastructure.contenedor import Contenedor

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def ciclo_vida(app: FastAPI):
    app.state.contenedor = Contenedor()
    yield


app = FastAPI(
    title="Asistente de consulta del quechua wanka",
    description=(
        "Consulta documental sobre el corpus publicado de quechua wanka de Junin. "
        "Toda respuesta cita el documento y la pagina que la sustentan, y el sistema "
        "declara explicitamente la ausencia de informacion en lugar de proponer una "
        "forma no documentada."
    ),
    version="1.0.0",
    lifespan=ciclo_vida,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=configuracion.lista_cors,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", tags=["sistema"])
def raiz():
    return {"servicio": "asistente-quechua-wanka", "documentacion": "/docs"}
