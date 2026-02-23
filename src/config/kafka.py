from __future__ import annotations

from typing import Dict

import yaml
from pydantic import BaseModel, model_validator


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
    def from_yaml(cls, path: str):
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)
