from dataclasses import dataclass

from .position import Position
from .trip import Trip


@dataclass(frozen=True)
class Vehicle:
    id: str
    trip: Trip
    position: Position
    current_status: str
    timestamp: int
