from dataclasses import dataclass


@dataclass(frozen=True)
class StopTime:
    stop_id: str
    arrival_delay: int
    arrival_time: int
    departure_delay: int
    departure_time: int
    schedule_relationship: str
