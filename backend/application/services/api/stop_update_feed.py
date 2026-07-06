from datetime import datetime, time, timezone
from typing import List
from zoneinfo import ZoneInfo

from backend.application.dto.stop import TransitPathDTO
from backend.application.ports import ScheduleReader, StopUpdateReader
from backend.domain.gtfs.scheduled_departure import ScheduledDeparture
from backend.domain.gtfs_rt.stop_update import StopUpdate

_TIMEZONE = ZoneInfo("Europe/Paris")
_WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]
_FEED_SIZE = 5


def _clock_to_epoch(clock: str, service_midnight: int) -> int:
    hours, minutes, seconds = (int(part) for part in clock.split(":"))
    return service_midnight + hours * 3600 + minutes * 60 + seconds


class StopUpdateFeed:
    def __init__(
        self,
        stop_update_repository: StopUpdateReader,
        stop_time_repository: ScheduleReader,
    ) -> None:
        self.stop_update_repository = stop_update_repository
        self.stop_time_repository = stop_time_repository

    async def get_updates(self, transit: TransitPathDTO) -> List[StopUpdate]:
        now = datetime.now(tz=timezone.utc)

        realtime = await self._realtime_updates(transit, now)
        estimated = await self._estimated_updates(
            transit, now, {stop_update.trip_id for stop_update in realtime}
        )

        merged = realtime + estimated
        merged.sort(key=lambda stop_update: stop_update.departure_time)

        return merged[:_FEED_SIZE]

    async def _realtime_updates(
        self, transit: TransitPathDTO, now: datetime
    ) -> List[StopUpdate]:
        stop_updates = await self.stop_update_repository.get_stop_updates(
            city=transit.city,
            route_id=transit.route_id,
            direction_id=transit.direction_id,
            stop_id=transit.stop_id__origin,
        )

        active = [
            stop_update for stop_update in stop_updates if not stop_update.is_stale(now)
        ]

        reachable_trip_ids = await self.stop_time_repository.get_reachable_trip_ids(
            [stop_update.trip_id for stop_update in active],
            transit.stop_id__destination,
        )

        return [
            stop_update
            for stop_update in active
            if stop_update.trip_id in reachable_trip_ids
        ]

    async def _estimated_updates(
        self, transit: TransitPathDTO, now: datetime, realtime_trip_ids: set[str]
    ) -> List[StopUpdate]:
        local_now = now.astimezone(_TIMEZONE)
        service_midnight = int(
            datetime.combine(local_now.date(), time.min, tzinfo=_TIMEZONE).timestamp()
        )

        scheduled_departures = await self.stop_time_repository.get_scheduled_departures(
            route_id=transit.route_id,
            direction_id=transit.direction_id,
            origin_stop_id=transit.stop_id__origin,
            destination_stop_id=transit.stop_id__destination,
            after_clock=local_now.strftime("%H:%M:%S"),
            service_date=local_now.strftime("%Y%m%d"),
            weekday=_WEEKDAYS[local_now.weekday()],
            limit=_FEED_SIZE,
        )

        timestamp = int(now.timestamp())

        return [
            self._to_stop_update(scheduled_departure, service_midnight, timestamp)
            for scheduled_departure in scheduled_departures
            if scheduled_departure.trip_id not in realtime_trip_ids
        ]

    @staticmethod
    def _to_stop_update(
        scheduled_departure: ScheduledDeparture, service_midnight: int, timestamp: int
    ) -> StopUpdate:
        return StopUpdate(
            trip_id=scheduled_departure.trip_id,
            timestamp=timestamp,
            departure_time=_clock_to_epoch(
                scheduled_departure.departure_time, service_midnight
            ),
            departure_delay=0,
            arrival_time=_clock_to_epoch(
                scheduled_departure.arrival_time, service_midnight
            ),
            arrival_delay=0,
            is_realtime=False,
        )
