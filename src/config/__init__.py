import os

from sqlalchemy import URL

from .config import ProductionSettings, Settings, StagingSettings

_env = os.getenv("ENV", "stg")

settings: Settings = StagingSettings()  # type: ignore[call-arg]
if _env == "prod":
    settings = ProductionSettings()  # type: ignore[call-arg]


postgres_url = URL.create(
    "postgresql+psycopg",
    settings.postgres.username,
    settings.postgres.password,
    settings.postgres.host,
    settings.postgres.port,
    settings.postgres.database,
)
