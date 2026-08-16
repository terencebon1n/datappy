from typing import Sequence

from sqlalchemy import Row, and_, distinct, select

from backend.domain.gtfs.geo import BoundingBox
from backend.infrastructure.database.postgres.models.route import RouteModel
from backend.infrastructure.database.postgres.models.stop import StopModel
from backend.infrastructure.database.postgres.models.stop_time import StopTimeModel
from backend.infrastructure.database.postgres.models.trip import TripModel
from backend.infrastructure.database.repository import AsyncQueryRepository


class StopRepository(AsyncQueryRepository[StopModel]):
    model = StopModel

    async def get_stop_names(self, route_id: str) -> Sequence[str]:
        query = (
            select(distinct(self.model.name))
            .join(StopTimeModel, StopTimeModel.stop_id == self.model.id)
            .join(TripModel, StopTimeModel.trip_id == TripModel.id)
            .where(
                and_(
                    TripModel.route_id == route_id,
                )
            )
            .order_by(self.model.name)
        )

        result = await self.execute_select(query)

        return result.scalars().all()

    async def get_sibling_stop_ids(self, stop_id: str) -> Sequence[str]:
        name = select(self.model.name).where(self.model.id == stop_id).scalar_subquery()

        query = select(distinct(self.model.id)).where(self.model.name == name)

        result = await self.execute_select(query)

        return result.scalars().all()

    async def get_route_stops(self, route_id: str) -> Sequence[Row]:
        query = (
            select(
                self.model.id,
                self.model.name,
                self.model.latitude,
                self.model.longitude,
                self.model.code,
                self.model.platform_code,
                self.model.wheelchair_boarding,
            )
            .join(StopTimeModel, StopTimeModel.stop_id == self.model.id)
            .join(TripModel, StopTimeModel.trip_id == TripModel.id)
            .where(TripModel.route_id == route_id)
            .order_by(self.model.name)
            .distinct()
        )

        result = await self.execute_select(query)

        return result.all()

    async def get_nearby_stops(self, box: BoundingBox) -> Sequence[Row]:
        query = (
            select(
                self.model.name,
                self.model.latitude,
                self.model.longitude,
                RouteModel.id.label("route_id"),
                RouteModel.short_name,
                RouteModel.long_name,
                RouteModel.color,
                RouteModel.type,
            )
            .join(StopTimeModel, StopTimeModel.stop_id == self.model.id)
            .join(TripModel, StopTimeModel.trip_id == TripModel.id)
            .join(RouteModel, TripModel.route_id == RouteModel.id)
            .where(
                and_(
                    self.model.latitude.between(box.min_latitude, box.max_latitude),
                    self.model.longitude.between(box.min_longitude, box.max_longitude),
                )
            )
            .distinct()
        )

        result = await self.execute_select(query)

        return result.all()
