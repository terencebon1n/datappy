from typing import Sequence

from sqlalchemy import Row, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.domain.gtfs.route import Route
from src.infrastructure.database.postgres.models.route import RouteModel
from src.infrastructure.database.repository import BaseRepository


class RouteRepository(BaseRepository[Route, RouteModel]):
    domain = Route
    model = RouteModel

    def __init__(self, session: Session | AsyncSession) -> None:
        super().__init__(session)

    async def get_conveyances(self) -> Sequence[Row]:
        query = select(
            self.model.id,
            self.model.short_name,
            self.model.long_name,
            self.model.color,
            self.model.type,
        ).order_by(self.model.type, self.model.short_name)

        result = await self.execute_select(query)

        return result.all()
