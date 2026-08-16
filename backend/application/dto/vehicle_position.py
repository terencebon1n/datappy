from pydantic import BaseModel, Field

from backend.domain.gtfs_rt.enums import City
from backend.domain.gtfs_rt.vehicle_position import VehiclePosition


class VehiclePathDTO(BaseModel):
    city: City = Field(description="City")
    route_id: str = Field(description="Route ID")


class VehiclePositionDTO(BaseModel):
    id: str = Field(description="Vehicle ID")
    trip_id: str = Field(description="Trip ID")
    route_id: str = Field(description="Route ID")
    direction_id: int = Field(description="Direction ID")
    latitude: float = Field(description="Latitude")
    longitude: float = Field(description="Longitude")
    bearing: int = Field(description="Heading in degrees")
    speed: int = Field(description="Speed")
    current_status: str = Field(description="Vehicle stop status")
    timestamp: int = Field(description="Position timestamp")

    @classmethod
    def from_domain(cls, position: VehiclePosition) -> "VehiclePositionDTO":
        return cls(
            id=position.id,
            trip_id=position.trip.id,
            route_id=position.trip.route_id,
            direction_id=position.trip.direction_id,
            latitude=position.position.latitude,
            longitude=position.position.longitude,
            bearing=position.position.bearing,
            speed=position.position.speed,
            current_status=position.current_status,
            timestamp=position.timestamp,
        )
