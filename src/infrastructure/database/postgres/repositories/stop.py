from datetime import date
from typing import Sequence

from sqlalchemy import and_, distinct, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.domain.gtfs.stop import Stop
from src.infrastructure.database.postgres.models.stop import StopModel
from src.infrastructure.database.postgres.models.stop_time import StopTimeModel
from src.infrastructure.database.postgres.models.trip import TripModel
from src.infrastructure.database.repository import BaseRepository


class StopRepository(BaseRepository[Stop, StopModel]):
    domain = Stop
    model = StopModel

    def __init__(self, session: Session | AsyncSession) -> None:
        super().__init__(session)

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
