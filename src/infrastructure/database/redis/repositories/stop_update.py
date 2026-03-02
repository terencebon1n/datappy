import json
from typing import List

from redis import Redis

from src.domain.gtfs_rt.stop_update import StopUpdate


class StopUpdateRepository:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def get_stop_updates(
        self,
        route_id: int,
        direction_id: int,
        stop_id: int,
    ) -> List[StopUpdate]:
        key = f"{route_id}:{direction_id}:{stop_id}"

        raw_map = self.redis.hgetall(key)

        if not raw_map:
            return []

        stop_updates = []
        for val in raw_map.values():
            try:
                stop_updates.append(StopUpdate.model_validate(json.loads(val)))
            except (json.JSONDecodeError, ValueError) as e:
                continue
        return stop_updates
