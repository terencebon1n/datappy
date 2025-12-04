from dataclasses import dataclass

from .stop_time import StopTimeContainer
from .trip import Trip


@dataclass(frozen=True)
class TripUpdate:
    id: str
    trip: Trip
    stop_times: StopTimeContainer
