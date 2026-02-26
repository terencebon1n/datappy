from __future__ import annotations

import os
from typing import Dict

import yaml
from pydantic import BaseModel, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class PostgresConfigModel(BaseModel):
    pool_size: int
    max_overflow: int
    pool_recycle: int
    pool_timeout: int


class PostgresModel(BaseModel):
    host: str
    port: int = 5432
    database: str = "postgres"
    username: str
    password: str

    config: PostgresConfigModel


class KafkaModel(BaseModel):
    brokers: str


class Settings(BaseSettings):
    postgres: PostgresModel
    kafka: KafkaModel

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


class KafkaConfig(BaseModel):
    bootstrap_servers: str
    starting_offsets: str
    max_offsets_per_trigger: int

    @model_validator(mode="after")
    def transform_to_spark_format(self) -> KafkaConfig:
        # This keeps the logic internal to the model
        return self

    def to_spark_options(self) -> Dict[str, str]:
        return {
            "kafka.bootstrap.servers": self.bootstrap_servers,
            "startingOffsets": self.starting_offsets,
            "maxOffsetsPerTrigger": str(self.max_offsets_per_trigger),
        }


class AppConfig(BaseModel):
    kafka: KafkaConfig

    @classmethod
    def from_yaml(cls, path: str) -> AppConfig:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)


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
