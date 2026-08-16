from dataclasses import dataclass, field
from typing import Any, Sequence

from backend.application.dto.route import ConveyanceDTO
from backend.application.dto.stop import NearbyQueryDTO, NearbyStopDTO
from backend.application.ports import NearbyStopReader
from backend.domain.enums import route_type_name
from backend.domain.gtfs.geo import Coordinates


@dataclass
class _NearbyStop:
    distance: float
    latitude: float
    longitude: float
    routes: dict[str, ConveyanceDTO] = field(default_factory=dict)


class NearbyStopLoaderService:
    def __init__(self, stop_repository: NearbyStopReader) -> None:
        self.stop_repository = stop_repository

    async def get_nearby_stops(self, query: NearbyQueryDTO) -> list[NearbyStopDTO]:
        origin = Coordinates(latitude=query.latitude, longitude=query.longitude)
        rows: Sequence[Any] = await self.stop_repository.get_nearby_stops(
            origin.bounding_box(query.radius_m)
        )

        nearby: dict[str, _NearbyStop] = {}
        for row in rows:
            distance = origin.distance_to(
                Coordinates(latitude=row.latitude, longitude=row.longitude)
            )
            if distance > query.radius_m:
                continue

            stop = nearby.get(row.name)
            if stop is None:
                stop = _NearbyStop(
                    distance=distance,
                    latitude=row.latitude,
                    longitude=row.longitude,
                )
                nearby[row.name] = stop
            elif distance < stop.distance:
                stop.distance = distance
                stop.latitude = row.latitude
                stop.longitude = row.longitude

            stop.routes[row.route_id] = ConveyanceDTO(
                id=row.route_id,
                short_name=row.short_name,
                long_name=row.long_name,
                color=row.color,
                type=row.type,
                type_name=route_type_name(row.type),
            )

        ordered = sorted(nearby.items(), key=lambda item: (item[1].distance, item[0]))

        return [
            NearbyStopDTO(
                name=name,
                distance_m=round(stop.distance),
                latitude=stop.latitude,
                longitude=stop.longitude,
                routes=sorted(
                    stop.routes.values(),
                    key=lambda route: (route.type, route.short_name),
                ),
            )
            for name, stop in ordered[: query.limit]
        ]
