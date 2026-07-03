from typing import Any, Sequence

from src.application.dto.route import ConveyanceDTO
from src.application.ports import ConveyanceReader
from src.domain.enums import RouteTypeId, RouteTypeName


class RouteLoaderService:
    def __init__(self, route_repository: ConveyanceReader) -> None:
        self.route_repository = route_repository

    async def get_conveyances(self) -> list[ConveyanceDTO]:
        rconveyances: Sequence[Any] = await self.route_repository.get_conveyances()
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
