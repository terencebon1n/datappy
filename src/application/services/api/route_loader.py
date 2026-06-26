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
                type=rconveyance.type,
                type_name=self._type_name(rconveyance.type),
            )
            for rconveyance in rconveyances
        ]

    @staticmethod
    def _type_name(route_type: int) -> str:
        """Human-readable label for a GTFS route_type.

        GTFS allows extended route types beyond the standard 0-7, so fall back
        gracefully instead of raising on an unknown value.
        """
        try:
            return RouteTypeName[RouteTypeId(route_type).name].value
        except ValueError:
            return "Autre"
