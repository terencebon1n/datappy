from dataclasses import dataclass
from datetime import datetime, time, timezone
from typing import Any, Optional, Sequence
from zoneinfo import ZoneInfo

from backend.application.dto.departure import StopDepartureDTO, StopDeparturePathDTO
from backend.application.ports import (
    SiblingStopReader,
    StopDepartureReader,
    StopUpdateReader,
    TripHeadsignReader,
)
from backend.domain.gtfs_rt.stop_update import StopUpdate

_TIMEZONE = ZoneInfo("Europe/Paris")
_UNKNOWN_ROUTE_TYPE = 3
_WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


@dataclass(frozen=True)
class _ServiceKey:
    route_id: str
    direction_id: int
    stop_id: str


@dataclass(frozen=True)
class _RouteInfo:
    short_name: str
    color: Optional[str]
    type: int


def _clock_to_epoch(clock: str, service_midnight: int) -> int:
    hours, minutes, seconds = (int(part) for part in clock.split(":"))
    return service_midnight + hours * 3600 + minutes * 60 + seconds


class StopDepartureFeed:
    def __init__(
        self,
        stop_update_repository: StopUpdateReader,
        stop_time_repository: StopDepartureReader,
        trip_repository: TripHeadsignReader,
        stop_repository: SiblingStopReader,
    ) -> None:
        self.stop_update_repository = stop_update_repository
        self.stop_time_repository = stop_time_repository
        self.trip_repository = trip_repository
        self.stop_repository = stop_repository

    async def get_departures(
        self, selection: StopDeparturePathDTO
    ) -> list[StopDepartureDTO]:
        now = datetime.now(tz=timezone.utc)

        # A stop_id is one platform of one route; riders mean the whole place,
        # so gather every platform in the city carrying the same name.
        stop_ids = list(
            await self.stop_repository.get_sibling_stop_ids(selection.stop_id)
        ) or [selection.stop_id]

        scheduled = await self._scheduled_departures(selection, stop_ids, now)
        routes = {
            departure.route_id: _RouteInfo(
                short_name=departure.route_short_name,
                color=departure.route_color,
                type=departure.route_type,
            )
            for departure in scheduled
        }
        realtime = await self._realtime_departures(selection, stop_ids, now, routes)

        seen = {departure.trip_id for departure in realtime}
        merged = realtime + [
            departure for departure in scheduled if departure.trip_id not in seen
        ]

        return self._capped_per_destination(merged, selection.limit)

    @staticmethod
    def _capped_per_destination(
        departures: list[StopDepartureDTO], limit: int
    ) -> list[StopDepartureDTO]:
        by_destination: dict[tuple[str, str], list[StopDepartureDTO]] = {}
        for departure in departures:
            key = (departure.route_id, departure.headsign)
            by_destination.setdefault(key, []).append(departure)

        kept: list[StopDepartureDTO] = []
        for group in by_destination.values():
            group.sort(key=lambda departure: departure.departure_time)
            kept.extend(group[:limit])

        kept.sort(key=lambda departure: departure.departure_time)
        return kept

    async def _realtime_departures(
        self,
        selection: StopDeparturePathDTO,
        stop_ids: list[str],
        now: datetime,
        routes: dict[str, _RouteInfo],
    ) -> list[StopDepartureDTO]:
        rows: Sequence[Any] = await self.stop_time_repository.get_stop_service_keys(
            stop_ids
        )
        keys = [
            _ServiceKey(
                route_id=row.route_id,
                direction_id=row.direction_id,
                stop_id=row.stop_id,
            )
            for row in rows
        ]

        active: list[tuple[_ServiceKey, StopUpdate]] = []
        for key in keys:
            stop_updates = await self.stop_update_repository.get_stop_updates(
                city=selection.city,
                route_id=key.route_id,
                direction_id=key.direction_id,
                stop_id=key.stop_id,
            )
            active.extend(
                (key, stop_update)
                for stop_update in stop_updates
                if not stop_update.is_stale(now)
            )

        if not active:
            return []

        headsigns = await self._headsigns_for(
            [stop_update.trip_id for _, stop_update in active]
        )

        return [
            self._to_realtime_dto(key, stop_update, routes.get(key.route_id), headsigns)
            for key, stop_update in active
        ]

    @staticmethod
    def _to_realtime_dto(
        key: _ServiceKey,
        stop_update: StopUpdate,
        route: Optional[_RouteInfo],
        headsigns: dict[str, str],
    ) -> StopDepartureDTO:
        return StopDepartureDTO(
            trip_id=stop_update.trip_id,
            route_id=key.route_id,
            route_short_name=route.short_name if route else key.route_id,
            route_color=route.color if route else None,
            route_type=route.type if route else _UNKNOWN_ROUTE_TYPE,
            direction_id=key.direction_id,
            headsign=headsigns.get(stop_update.trip_id, ""),
            departure_time=stop_update.departure_time,
            departure_delay=stop_update.departure_delay,
            is_realtime=True,
        )

    async def _headsigns_for(self, trip_ids: list[str]) -> dict[str, str]:
        rows: Sequence[Any] = await self.trip_repository.get_trip_headsigns(trip_ids)
        return {row.id: row.headsign for row in rows}

    async def _scheduled_departures(
        self,
        selection: StopDeparturePathDTO,
        stop_ids: list[str],
        now: datetime,
    ) -> list[StopDepartureDTO]:
        local_now = now.astimezone(_TIMEZONE)
        service_midnight = int(
            datetime.combine(local_now.date(), time.min, tzinfo=_TIMEZONE).timestamp()
        )

        rows: Sequence[Any] = await self.stop_time_repository.get_stop_departures(
            stop_ids=stop_ids,
            after_clock=local_now.strftime("%H:%M:%S"),
            service_date=local_now.strftime("%Y%m%d"),
            weekday=_WEEKDAYS[local_now.weekday()],
            limit=selection.limit * 12,
        )

        return [
            StopDepartureDTO(
                trip_id=row.trip_id,
                route_id=row.route_id,
                route_short_name=row.route_short_name,
                route_color=row.route_color,
                route_type=row.route_type,
                direction_id=row.direction_id,
                headsign=row.headsign,
                departure_time=_clock_to_epoch(row.departure_time, service_midnight),
                departure_delay=0,
                is_realtime=False,
            )
            for row in rows
        ]
