from typing import Sequence

from sqlalchemy import CompoundSelect, Row, and_, except_, select, union
from sqlalchemy.orm import aliased

from backend.domain.gtfs.scheduled_departure import ScheduledDeparture
from backend.infrastructure.database.postgres.models.calendar import CalendarModel
from backend.infrastructure.database.postgres.models.calendar_date import (
    CalendarDateModel,
)
from backend.infrastructure.database.postgres.models.stop_time import StopTimeModel
from backend.infrastructure.database.postgres.models.trip import TripModel
from backend.infrastructure.database.repository import AsyncQueryRepository


class StopTimeRepository(AsyncQueryRepository[StopTimeModel]):
    model = StopTimeModel

    async def get_reachable_trip_ids(
        self, trip_ids: list[str], destination_stop_id: str
    ) -> Sequence[str]:
        query = select(self.model.trip_id).where(
            and_(
                self.model.stop_id == destination_stop_id,
                self.model.trip_id.in_(trip_ids),
            )
        )

        result = await self.execute_select(query)

        return result.scalars().all()

    @staticmethod
    def _active_services(service_date: str, weekday: str) -> CompoundSelect:
        return except_(
            union(
                select(CalendarModel.service_id).where(
                    and_(
                        CalendarModel.start_date <= service_date,
                        CalendarModel.end_date >= service_date,
                        getattr(CalendarModel, weekday).is_(True),
                    )
                ),
                select(CalendarDateModel.service_id).where(
                    and_(
                        CalendarDateModel.date == service_date,
                        CalendarDateModel.exception_type == 1,
                    )
                ),
            ),
            select(CalendarDateModel.service_id).where(
                and_(
                    CalendarDateModel.date == service_date,
                    CalendarDateModel.exception_type == 2,
                )
            ),
        )

    async def get_stop_departures(
        self,
        route_id: str,
        stop_id: str,
        after_clock: str,
        service_date: str,
        weekday: str,
        limit: int,
    ) -> Sequence[Row]:
        query = (
            select(
                self.model.trip_id,
                self.model.departure_time,
                TripModel.direction_id,
                TripModel.headsign,
            )
            .join(TripModel, TripModel.id == self.model.trip_id)
            .where(
                and_(
                    self.model.stop_id == stop_id,
                    self.model.departure_time >= after_clock,
                    TripModel.route_id == route_id,
                    TripModel.service_id.in_(
                        self._active_services(service_date, weekday)
                    ),
                )
            )
            .order_by(self.model.departure_time)
            .limit(limit)
        )

        result = await self.execute_select(query)

        return result.all()

    async def get_scheduled_departures(
        self,
        route_id: str,
        direction_id: int,
        origin_stop_id: str,
        destination_stop_id: str,
        after_clock: str,
        service_date: str,
        weekday: str,
        limit: int,
    ) -> Sequence[ScheduledDeparture]:
        active_services = self._active_services(service_date, weekday)

        destination = aliased(StopTimeModel, name="st_destination")

        query = (
            select(
                self.model.trip_id,
                self.model.departure_time,
                self.model.arrival_time,
            )
            .join(TripModel, TripModel.id == self.model.trip_id)
            .join(destination, destination.trip_id == self.model.trip_id)
            .where(
                and_(
                    self.model.stop_id == origin_stop_id,
                    self.model.departure_time >= after_clock,
                    TripModel.route_id == route_id,
                    TripModel.direction_id == direction_id,
                    destination.stop_id == destination_stop_id,
                    destination.stop_sequence > self.model.stop_sequence,
                    TripModel.service_id.in_(active_services),
                )
            )
            .order_by(self.model.departure_time)
            .limit(limit)
        )

        result = await self.execute_select(query)

        return [
            ScheduledDeparture(
                trip_id=row.trip_id,
                departure_time=row.departure_time,
                arrival_time=row.arrival_time,
            )
            for row in result.all()
        ]
