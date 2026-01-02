import os

from sqlalchemy import URL

from .config import ProductionSettings, Settings, StagingSettings
from .kafka import AppConfig

_env = os.getenv("ENV", "stg")

settings: Settings = StagingSettings()  # type: ignore[call-arg]
if _env == "prod":
    settings = ProductionSettings()  # type: ignore[call-arg]


postgres_url: URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.postgres.username,
    password=settings.postgres.password,
    host=settings.postgres.host,
    port=settings.postgres.port,
    database=settings.postgres.database,
)

__all__ = ["settings", "postgres_url", "AppConfig"]
