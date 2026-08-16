from typing import Any, Sequence

from backend.application.dto.geometry import (
    DirectionHeadsignDTO,
    PointDTO,
    RouteGeometryDTO,
    RouteShapeDTO,
    RouteStopDTO,
)
from backend.application.ports import (
    RouteGeometryReader,
    RouteStopReader,
    TripHeadsignReader,
)


class RouteGeometryLoaderService:
    def __init__(
        self,
        shape_repository: RouteGeometryReader,
        stop_repository: RouteStopReader,
        trip_repository: TripHeadsignReader,
    ) -> None:
        self.shape_repository = shape_repository
        self.stop_repository = stop_repository
        self.trip_repository = trip_repository

    async def get_route_geometry(self, route_id: str) -> RouteGeometryDTO:
        shape_rows: Sequence[Any] = await self.shape_repository.get_route_shapes(
            route_id
        )
        stop_rows: Sequence[Any] = await self.stop_repository.get_route_stops(route_id)
        headsign_rows: Sequence[
            Any
        ] = await self.trip_repository.get_direction_headsigns(route_id)

        points_by_direction: dict[int, list[PointDTO]] = {}
        for row in shape_rows:
            points_by_direction.setdefault(row.direction_id, []).append(
                PointDTO(latitude=row.latitude, longitude=row.longitude)
            )

        return RouteGeometryDTO(
            shapes=[
                RouteShapeDTO(direction_id=direction_id, points=points)
                for direction_id, points in sorted(points_by_direction.items())
            ],
            stops=[
                RouteStopDTO(
                    id=row.id,
                    name=row.name,
                    latitude=row.latitude,
                    longitude=row.longitude,
                    code=row.code,
                    platform_code=row.platform_code,
                    wheelchair_boarding=row.wheelchair_boarding,
                )
                for row in stop_rows
            ],
            direction_headsigns=[
                DirectionHeadsignDTO(
                    direction_id=row.direction_id, headsign=row.headsign
                )
                for row in headsign_rows
            ],
        )
