import json
import logging
import time
from typing import Optional

import redis
from quixstreams.sinks import BatchingSink, SinkBatch

from backend.domain.gtfs_rt.enums import City

__all__ = ("RedisHsetAlertSink",)

logger = logging.getLogger(__name__)


def alert_key(city: City) -> str:
    return f"{city}|alerts"


class RedisHsetAlertSink(BatchingSink):
    def __init__(
        self,
        city: City,
        host: str,
        port: int,
        db: int = 0,
        ttl: int = 3600,
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
        hash_key = alert_key(self._city)
        with self._client.pipeline(transaction=True) as pipe:
            for item in batch:
                value = item.value
                pipe.hset(hash_key, value["alert_id"], json.dumps(value))
            pipe.expire(hash_key, self._ttl)
            pipe.execute(raise_on_error=True)
        logger.debug(
            f"Flushed {batch.size} alerts to Redis hset in {round(time.monotonic() - start, 4)}s"
        )
