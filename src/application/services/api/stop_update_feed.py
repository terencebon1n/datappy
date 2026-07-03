from datetime import datetime, timezone
from typing import List

from src.application.dto.stop import TransitPathDTO
from src.application.ports import ReachableTripReader, StopUpdateReader
from src.domain.gtfs_rt.stop_update import StopUpdate


class StopUpdateFeed:
    def __init__(
        self,
        stop_update_repository: StopUpdateReader,
        stop_time_repository: ReachableTripReader,
    ) -> None:
        self.stop_update_repository = stop_update_repository
        self.stop_time_repository = stop_time_repository

    async def get_updates(self, transit: TransitPathDTO) -> List[StopUpdate]:
        stop_updates: List[
            StopUpdate
        ] = await self.stop_update_repository.get_stop_updates(
            city=transit.city,
            route_id=transit.route_id,
            direction_id=transit.direction_id,
            stop_id=transit.stop_id__origin,
        )

        now = datetime.now(tz=timezone.utc)

        active_stop_updates: List[StopUpdate] = [
            stop_update for stop_update in stop_updates if not stop_update.is_stale(now)
        ]

        active_trip_ids = [
            active_stop_update.trip_id for active_stop_update in active_stop_updates
        ]

        reachable_trip_ids = await self.stop_time_repository.get_reachable_trip_ids(
            active_trip_ids, transit.stop_id__destination
        )

        reachable_stop_updates = [
            stop_update
            for stop_update in active_stop_updates
            if stop_update.trip_id in reachable_trip_ids
        ]

        reachable_stop_updates.sort(key=lambda stop_update: stop_update.departure_time)

        return reachable_stop_updates
