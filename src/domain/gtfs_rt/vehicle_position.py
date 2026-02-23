from pydantic import BaseModel

from src.domain.gtfs_rt.trip import Trip


class Position(BaseModel):
    latitude: float
    longitude: float
    bearing: int
    speed: int


class VehiclePosition(BaseModel):
    id: str
    trip: Trip
    position: Position
    current_status: str
    timestamp: int
