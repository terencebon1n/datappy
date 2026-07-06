from __future__ import annotations

from types import TracebackType
from typing import Optional, Type

from redis.client import Pipeline, Redis


class RedisPipelineContext:
    def __init__(self, host: str = "redis", port: int = 6379) -> None:
        self.host: str = host
        self.port: int = port

    def __enter__(self) -> RedisPipelineContext:
        self.client: Redis = Redis(
            host=self.host, port=self.port, decode_responses=True
        )
        self.pipe: Pipeline = self.client.pipeline()
        return self

    def add_to_pipeline(self, key: str, field: str, value: str, ttl: int = 300) -> None:
        self.pipe.hset(key, field, value)
        self.pipe.expire(key, ttl)

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        if exc_type is None:
            self.pipe.execute()
        self.client.close()
