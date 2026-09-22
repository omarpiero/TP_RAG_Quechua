from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

RAIZ = Path(__file__).resolve().parents[1]


class Configuracion(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=RAIZ / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "quechua_wanka"
    postgres_user: str = "postgres"
    postgres_password: str = ""

    ruta_tabla_traduccion: Path = RAIZ / "data" / "traduccion_en_es.json"
    ollama_url: str = "http://localhost:11434"
    ollama_modelo: str = "qwen3.5:4b"

    umbral_abstencion: float = 0.48
    fragmentos_recuperados: int = 5
    ruta_corpus: Path = RAIZ / "data" / "fragmentos_v3.jsonl"

    cors_origenes: str = "http://localhost:5173"

    @property
    def url_base_datos(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def lista_cors(self) -> list[str]:
        return [o.strip() for o in self.cors_origenes.split(",") if o.strip()]


configuracion = Configuracion()
