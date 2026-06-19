import json
import logging
import time
from typing import Optional

import redis
from quixstreams.sinks import BatchingSink, SinkBatch

from src.domain.gtfs_rt.enums import City

__all__ = ("RedisHsetStopUpdateSink",)

logger = logging.getLogger(__name__)


class RedisHsetStopUpdateSink(BatchingSink):
    def __init__(
        self,
        city: City,
        host: str,
        port: int,
        db: int = 0,
        ttl: int = 300,
        password: Optional[str] = None,
        socket_timeout: float = 30.0,
    ) -> None:
        super().__init__()
        self._city = city
        self._ttl = ttl
        self._client: Optional[redis.Redis] = None
        self._client_settings = {
            "host": host,
            "port": port,
            "db": db,
            "password": password,
            "socket_timeout": socket_timeout,
        }

    def setup(self) -> None:
        self._client = redis.Redis(**self._client_settings)
        self._client.ping()

    def write(self, batch: SinkBatch) -> None:
        start = time.monotonic()
        with self._client.pipeline(transaction=True) as pipe:
            for item in batch:
                value = item.value
                hash_key = f"{self._city}:{value['route_id']}:{value['direction_id']}:{value['stop_id']}"
                field = value["trip_id"]
                pipe.hset(hash_key, field, json.dumps(value))
                pipe.expire(hash_key, self._ttl)
            pipe.execute(raise_on_error=True)
        logger.debug(
            f"Flushed {batch.size} stop updates to Redis hset in {round(time.monotonic() - start, 4)}s"
        )
