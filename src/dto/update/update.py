from dataclasses import dataclass

from .stop_time import StopTime
from ..vehicle import Trip


@dataclass(frozen=True)
class TripUpdate:
    id: str
    trip: Trip
    stop_times: list[StopTime]
