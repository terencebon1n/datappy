import json
from typing import List

from redis import Redis

from src.domain.gtfs_rt.enums import City
from src.domain.gtfs_rt.stop_update import StopUpdate


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
        prefix = f"{city}:{route_id}:{direction_id}:{stop_id}:*"

        keys = [key for key in self.redis.scan_iter(match=prefix)]

        if not keys:
            return []

        values = self.redis.mget(keys)

        stop_updates = []
        for val in values:
            try:
                stop_updates.append(StopUpdate.model_validate(json.loads(val)))
            except (json.JSONDecodeError, ValueError) as e:
                print(e)
                continue
        return stop_updates
