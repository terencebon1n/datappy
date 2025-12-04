from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresModel(BaseModel):
    host: str
    port: int = 5432
    database: str = "postgres"
    username: str
    password: str


class Settings(BaseSettings):
    postgres: PostgresModel

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
    )


class StagingSettings(Settings):
    env: str = "stg"

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_prefix="stg_",
        env_file=".env",
        env_file_encoding="utf-8",
    )


class ProductionSettings(Settings):
    env: str = "prod"

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        env_prefix="prod_",
        env_file=".env",
        env_file_encoding="utf-8",
    )
