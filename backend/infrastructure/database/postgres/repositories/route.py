from typing import Sequence

from sqlalchemy import Row, select

from backend.infrastructure.database.postgres.models.route import RouteModel
from backend.infrastructure.database.repository import AsyncQueryRepository


class RouteRepository(AsyncQueryRepository[RouteModel]):
    model = RouteModel

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
