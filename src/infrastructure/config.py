from __future__ import annotations

import os
from typing import Dict

import yaml
from pydantic import BaseModel, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from src.domain.gtfs_rt.enums import City


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


class RedisModel(BaseModel):
    host: str
    port: int = 6379


class KafkaModel(BaseModel):
    brokers: str


class GoogleOAuthModel(BaseModel):
    client_id: str
    client_secret: str
    redirect_uri: str


class AdminModel(BaseModel):
    allowed_email: str
    session_secret_key: str
    docker_image: str
    docker_network: str
    docker_host: str = "unix:///var/run/docker.sock"
    frontend_url: str = "http://localhost:8001"
    status_poll_interval_seconds: int = 5
    status_keepalive_seconds: int = 25
    google: GoogleOAuthModel


class CityFeedsModel(BaseModel):
    gtfs_schedule: str
    trip_update: str | None = None
    vehicle_position: str | None = None
    alert: str | None = None


_DEFAULT_FEEDS: dict[City, CityFeedsModel] = {
    City.MONTPELLIER: CityFeedsModel(
        gtfs_schedule="https://gtfsproxy.e-tam.fr/URB/GTFS.zip",
        trip_update="https://gtfsproxy.e-tam.fr/URB/TripUpdate.pb",
        vehicle_position="https://gtfsproxy.e-tam.fr/URB/VehiclePosition.pb",
        alert="https://gtfsproxy.e-tam.fr/URB/Alert.pb",
    ),
    City.BORDEAUX: CityFeedsModel(
        gtfs_schedule="https://bdx.mecatran.com/utw/ws/gtfsfeed/static/bordeaux?apiKey=opendata-bordeaux-metropole-flux-gtfs-rt",
        trip_update="https://bdx.mecatran.com/utw/ws/gtfsfeed/realtime/bordeaux?apiKey=opendata-bordeaux-metropole-flux-gtfs-rt",
        vehicle_position="https://bdx.mecatran.com/utw/ws/gtfsfeed/vehicles/bordeaux?apiKey=opendata-bordeaux-metropole-flux-gtfs-rt",
        alert="https://bdx.mecatran.com/utw/ws/gtfsfeed/alerts/bordeaux?apiKey=opendata-bordeaux-metropole-flux-gtfs-rt",
    ),
    City.TOULOUSE: CityFeedsModel(
        gtfs_schedule="https://data.toulouse-metropole.fr/explore/dataset/tisseo-gtfs/files/fc1dda89077cf37e4f7521760e0ef4e9/download/",
        trip_update="https://api.tisseo.fr/opendata/gtfsrt/GtfsRt.pb",
        vehicle_position="https://api.tisseo.fr/opendata/gtfsrt/GtfsRt.pb",
        alert="https://api.tisseo.fr/opendata/gtfsrt/GtfsRt.pb",
    ),
    City.NIMES: CityFeedsModel(
        gtfs_schedule="https://www.data.gouv.fr/api/1/datasets/r/15aeb8a5-1cca-4bb9-ae5f-b6e67e4ff2ab",
        trip_update="https://transport.data.gouv.fr/resources/80731/download",
        vehicle_position="https://transport.data.gouv.fr/resources/80732/download",
        alert="https://transport.data.gouv.fr/resources/80730/download",
    ),
}


class Settings(BaseSettings):
    postgres: PostgresModel
    kafka: KafkaModel
    redis: RedisModel
    admin: AdminModel
    feeds: dict[City, CityFeedsModel] = _DEFAULT_FEEDS

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
