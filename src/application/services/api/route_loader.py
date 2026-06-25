from typing import Sequence

from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.application.dto.route import ConveyanceDTO
from src.domain.enums import RouteTypeId, RouteTypeName
from src.infrastructure.database.postgres.repositories.route import RouteRepository


class RouteLoaderService:
    def __init__(self, session: Session | AsyncSession) -> None:
        self.route_repository = RouteRepository(session)

    async def get_conveyances(self) -> list[ConveyanceDTO]:
        rconveyances: Sequence[Row] = await self.route_repository.get_conveyances()
        return [
            ConveyanceDTO(
                id=rconveyance.id,
                short_name=rconveyance.short_name,
                long_name=rconveyance.long_name,
                color=rconveyance.color,
                type=RouteTypeId(rconveyance.type),
                type_name=RouteTypeName[RouteTypeId(rconveyance.type).name],
            )
            for rconveyance in rconveyances
        ]
