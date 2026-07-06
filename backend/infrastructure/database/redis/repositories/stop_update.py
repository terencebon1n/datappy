import json
import logging
from typing import List

from redis import Redis

from backend.domain.gtfs_rt.enums import City
from backend.domain.gtfs_rt.stop_update import StopUpdate

logger = logging.getLogger(__name__)


class StopUpdateRepository:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get_stop_updates(
        self,
        city: City,
        route_id: str,
        direction_id: int,
        stop_id: str,
    ) -> List[StopUpdate]:
        key = f"{city}|{route_id}|{direction_id}|{stop_id}"

        data = self.redis.hgetall(key)

        if not data:
            return []

        stop_updates = []
        for value in data.values():
            try:
                stop_updates.append(StopUpdate.model_validate(json.loads(value)))
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Skipping malformed stop update in {key}: {e}")
                continue
        return stop_updates
