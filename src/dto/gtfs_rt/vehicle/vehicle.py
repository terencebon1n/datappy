from dataclasses import dataclass

import requests

from ..gtfs_rt_base import GTFSRTContainerBase
from ..trip import Trip
from .position import Position


@dataclass(frozen=True)
class Vehicle:
    id: str
    trip: Trip
    position: Position
    current_status: str
    timestamp: int


class VehicleContainer(GTFSRTContainerBase[Vehicle]):
    items: list[Vehicle]

    def __init__(self) -> None:
        super().__init__()

    async def extract(self, url: str) -> list[Vehicle]:
        response = requests.get(url)
        self.feed.ParseFromString(response.content)
        for entity in self.feed.entity:
            self.items.append(
                Vehicle(
                    id=entity.id,
                    trip=Trip(
                        id=entity.vehicle.trip.trip_id,
                        schedule_relationship=entity.vehicle.trip.schedule_relationship,
                        route_id=entity.vehicle.trip.route_id,
                        direction_id=entity.vehicle.trip.direction_id,
                    ),
                    position=Position(
                        latitude=entity.vehicle.position.latitude,
                        longitude=entity.vehicle.position.longitude,
                        bearing=entity.vehicle.position.bearing,
                        speed=entity.vehicle.position.speed,
                    ),
                    current_status=entity.vehicle.current_status,
                    timestamp=entity.vehicle.timestamp,
                )
            )
        return self.items
