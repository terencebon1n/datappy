from typing import Sequence

from sqlalchemy import and_, select

from src.infrastructure.database.postgres.models.stop_time import StopTimeModel
from src.infrastructure.database.repository import AsyncQueryRepository


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
