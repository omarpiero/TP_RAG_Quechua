import os
import sys
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Al empaquetar con PyInstaller el codigo vive dentro de un directorio temporal que el
# propio ejecutable descomprime, de modo que la raiz del proyecto deja de ser la carpeta
# del archivo. Los datos de solo lectura (corpus, tabla de traduccion, interfaz compilada)
# viajan ahi dentro; lo que el usuario puede modificar va junto al ejecutable.
EMPAQUETADO = getattr(sys, "frozen", False)
RAIZ = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[1]))
CARPETA_EJECUTABLE = Path(sys.executable).parent if EMPAQUETADO else RAIZ


class Configuracion(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=CARPETA_EJECUTABLE / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Motor de persistencia: "postgres" o "sqlite".
    #
    # El proyecto entregado usa PostgreSQL, que es el motor que la consigna evalua. La
    # distribucion como ejecutable emplea SQLite para no exigir la instalacion de un
    # servidor de base de datos a quien solo quiere usar el sistema. Ambos recorren el
    # mismo adaptador y los mismos modelos, porque ninguno usa tipos ni sentencias
    # propias de un motor concreto: la sustitucion es un parametro, que es justo lo que
    # RNF-07 compromete.
    base_datos: str = "sqlite" if EMPAQUETADO else "postgres"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "quechua_wanka"
    postgres_user: str = "postgres"
    postgres_password: str = ""

    ruta_sqlite: Path = CARPETA_EJECUTABLE / "quechua_wanka.db"

    ruta_tabla_traduccion: Path = RAIZ / "data" / "traduccion_en_es.json"
    ollama_url: str = "http://localhost:11434"
    ollama_modelo: str = "qwen3.5:4b"

    umbral_abstencion: float = 0.48
    fragmentos_recuperados: int = 5
    ruta_corpus: Path = RAIZ / "data" / "fragmentos_v3.jsonl"

    # Interfaz ya compilada. Cuando existe, el servicio la sirve y no hace falta ningun
    # proceso aparte para el front-end.
    ruta_interfaz: Path = RAIZ / "interfaz"

    cors_origenes: str = "http://localhost:5173"

    @property
    def url_base_datos(self) -> str:
        if self.base_datos == "sqlite":
            return f"sqlite:///{self.ruta_sqlite}"
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def lista_cors(self) -> list[str]:
        return [o.strip() for o in self.cors_origenes.split(",") if o.strip()]

    @property
    def sirve_interfaz(self) -> bool:
        return (self.ruta_interfaz / "index.html").exists()


configuracion = Configuracion()
