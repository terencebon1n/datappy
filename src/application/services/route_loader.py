from typing import Sequence

from sqlalchemy import Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.application.dto.route import ConveyanceDTO, RouteTypeDTO
from src.domain.enums import RouteTypeId, RouteTypeName
from src.infrastructure.database.postgres.repositories.route import RouteRepository


class RouteLoaderService:
    def __init__(self, session: Session | AsyncSession) -> None:
        self.route_repository = RouteRepository(session)

    async def get_route_types(self) -> list[RouteTypeDTO]:
        rtypes: Sequence[int] = await self.route_repository.get_distinct_types()
        return [
            RouteTypeDTO(
                id=RouteTypeId(rtype),
                name=RouteTypeName[RouteTypeId(rtype).name],
            )
            for rtype in rtypes
        ]

    async def get_conveyances(self, route_type: RouteTypeId) -> list[ConveyanceDTO]:
        rconveyances: Sequence[Row] = await self.route_repository.get_conveyances(
            route_type.value
        )
        return [
            ConveyanceDTO(
                id=rconveyance.id,
                short_name=rconveyance.short_name,
                long_name=rconveyance.long_name,
            )
            for rconveyance in rconveyances
        ]
