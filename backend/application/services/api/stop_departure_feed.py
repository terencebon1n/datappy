from datetime import datetime, time, timezone
from typing import Any, Sequence
from zoneinfo import ZoneInfo

from backend.application.dto.departure import StopDepartureDTO, StopDeparturePathDTO
from backend.application.ports import (
    StopDepartureReader,
    StopUpdateReader,
    TripHeadsignReader,
)
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
_DIRECTIONS = (0, 1)


def _clock_to_epoch(clock: str, service_midnight: int) -> int:
    hours, minutes, seconds = (int(part) for part in clock.split(":"))
    return service_midnight + hours * 3600 + minutes * 60 + seconds


class StopDepartureFeed:
    def __init__(
        self,
        stop_update_repository: StopUpdateReader,
        stop_time_repository: StopDepartureReader,
        trip_repository: TripHeadsignReader,
    ) -> None:
        self.stop_update_repository = stop_update_repository
        self.stop_time_repository = stop_time_repository
        self.trip_repository = trip_repository

    async def get_departures(
        self, selection: StopDeparturePathDTO
    ) -> list[StopDepartureDTO]:
        now = datetime.now(tz=timezone.utc)

        realtime = await self._realtime_departures(selection, now)
        scheduled = await self._scheduled_departures(
            selection, now, {departure.trip_id for departure in realtime}
        )

        merged = realtime + scheduled
        merged.sort(key=lambda departure: departure.departure_time)

        return merged[: selection.limit]

    async def _realtime_departures(
        self, selection: StopDeparturePathDTO, now: datetime
    ) -> list[StopDepartureDTO]:
        active: list[tuple[int, StopUpdate]] = []
        for direction_id in _DIRECTIONS:
            stop_updates = await self.stop_update_repository.get_stop_updates(
                city=selection.city,
                route_id=selection.route_id,
                direction_id=direction_id,
                stop_id=selection.stop_id,
            )
            active.extend(
                (direction_id, stop_update)
                for stop_update in stop_updates
                if not stop_update.is_stale(now)
            )

        if not active:
            return []

        headsigns = await self._headsigns_for(
            [stop_update.trip_id for _, stop_update in active]
        )

        return [
            StopDepartureDTO(
                trip_id=stop_update.trip_id,
                direction_id=direction_id,
                headsign=headsigns.get(stop_update.trip_id, ""),
                departure_time=stop_update.departure_time,
                departure_delay=stop_update.departure_delay,
                is_realtime=True,
            )
            for direction_id, stop_update in active
        ]

    async def _headsigns_for(self, trip_ids: list[str]) -> dict[str, str]:
        rows: Sequence[Any] = await self.trip_repository.get_trip_headsigns(trip_ids)
        return {row.id: row.headsign for row in rows}

    async def _scheduled_departures(
        self,
        selection: StopDeparturePathDTO,
        now: datetime,
        realtime_trip_ids: set[str],
    ) -> list[StopDepartureDTO]:
        local_now = now.astimezone(_TIMEZONE)
        service_midnight = int(
            datetime.combine(local_now.date(), time.min, tzinfo=_TIMEZONE).timestamp()
        )

        rows: Sequence[Any] = await self.stop_time_repository.get_stop_departures(
            route_id=selection.route_id,
            stop_id=selection.stop_id,
            after_clock=local_now.strftime("%H:%M:%S"),
            service_date=local_now.strftime("%Y%m%d"),
            weekday=_WEEKDAYS[local_now.weekday()],
            limit=selection.limit,
        )

        return [
            StopDepartureDTO(
                trip_id=row.trip_id,
                direction_id=row.direction_id,
                headsign=row.headsign,
                departure_time=_clock_to_epoch(row.departure_time, service_midnight),
                departure_delay=0,
                is_realtime=False,
            )
            for row in rows
            if row.trip_id not in realtime_trip_ids
        ]
