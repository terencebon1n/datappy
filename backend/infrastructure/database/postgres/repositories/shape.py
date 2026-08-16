from typing import Sequence

from sqlalchemy import Row, func, select

from backend.infrastructure.database.postgres.models.shape import ShapeModel
from backend.infrastructure.database.postgres.models.trip import TripModel
from backend.infrastructure.database.repository import AsyncQueryRepository


class ShapeRepository(AsyncQueryRepository[ShapeModel]):
    model = ShapeModel

    async def get_route_shapes(self, route_id: str) -> Sequence[Row]:
        point_counts = (
            select(
                TripModel.direction_id.label("direction_id"),
                self.model.id.label("shape_id"),
                func.count().label("point_count"),
            )
            .join(TripModel, TripModel.shape_id == self.model.id)
            .where(TripModel.route_id == route_id)
            .group_by(TripModel.direction_id, self.model.id)
            .subquery()
        )

        ranked = select(
            point_counts.c.direction_id,
            point_counts.c.shape_id,
            func.row_number()
            .over(
                partition_by=point_counts.c.direction_id,
                order_by=point_counts.c.point_count.desc(),
            )
            .label("rank"),
        ).subquery()

        longest = (
            select(ranked.c.direction_id, ranked.c.shape_id)
            .where(ranked.c.rank == 1)
            .subquery()
        )

        query = (
            select(
                longest.c.direction_id,
                self.model.latitude,
                self.model.longitude,
            )
            .join(longest, longest.c.shape_id == self.model.id)
            .order_by(longest.c.direction_id, self.model.sequence)
        )

        result = await self.execute_select(query)

        return result.all()
