from typing import List

from pydantic import BaseModel, Field

from src.domain.gtfs_rt.trip import Trip


class StopTime(BaseModel):
    id: str
    arrival_time: int
    arrival_delay: int
    departure_time: int
    departure_delay: int
    schedule_relationship: int


class TripUpdate(BaseModel):
    id: str
    trip: Trip
    stop_times: List[StopTime] = Field(default_factory=list)


class MinimizedTripUpdate(BaseModel):
    id: str
    trip: Trip
    stop_time: StopTime
