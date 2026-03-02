from datetime import datetime, timezone
from typing import List

from redis import Redis

from src.application.dto.stop import TransitPathDTO
from src.domain.gtfs_rt.stop_update import StopUpdate
from src.infrastructure.database.redis.repositories.stop_update import (
    StopUpdateRepository,
)


class StopUpdateFeed:
    def __init__(self, redis: Redis) -> None:
        self.stop_update_repository = StopUpdateRepository(redis)

    async def get_updates(self, transit: TransitPathDTO) -> List[StopUpdate]:
        stop_updates: List[
            StopUpdate
        ] = await self.stop_update_repository.get_stop_updates(
            route_id=transit.route_id,
            direction_id=transit.direction_id,
            stop_id=transit.stop_id,
        )

        now = datetime.now(tz=timezone.utc)

        active_stop_updates = [
            stop_update for stop_update in stop_updates if not stop_update.is_stale(now)
        ]

        active_stop_updates.sort(key=lambda stop_update: stop_update.departure_time)

        return active_stop_updates
