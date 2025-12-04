from dataclasses import dataclass


@dataclass(frozen=True)
class Trip:
    id: str
    schedule_relationship: str
    route_id: str
    direction_id: int
