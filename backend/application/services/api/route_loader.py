from typing import Any, Sequence

from backend.application.dto.route import ConveyanceDTO
from backend.application.ports import ConveyanceReader
from backend.domain.enums import route_type_name


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
                type_name=route_type_name(rconveyance.type),
            )
            for rconveyance in rconveyances
        ]
